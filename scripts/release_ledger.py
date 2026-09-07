"""Frozen local release records. All side effects remain under the given project."""
import base64
import binascii
from datetime import datetime, timedelta
import hashlib
import json
import re
import uuid

MAX_FILE = 4 * 1024 * 1024
MAX_RECORD = 24 * 1024 * 1024


def timestamp(core, value):
    try:
        result = datetime.fromisoformat(value)
        if result.tzinfo is None:
            raise ValueError()
        return result
    except (ValueError, TypeError):
        raise core.LoopError("Use an ISO timestamp with a timezone.")


def release_path(core, root, release_id):
    if not re.fullmatch(r"REL-[A-Z0-9][A-Z0-9-]*", release_id):
        raise core.LoopError("Use a release ID such as REL-001.")
    return core.inside(root, f"{core.META}/releases/{release_id}.json")


def blob(core, root, relative):
    path = core.inside(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_FILE:
        raise core.LoopError("A reviewed attachment must be a regular file of at most 4 MiB.")
    content = path.read_bytes()
    if len(content) > MAX_FILE:
        raise core.LoopError("Attachment grew beyond 4 MiB while being read.")
    return {"path": relative, "sha256": core.digest(content),
            "content_base64": base64.b64encode(content).decode("ascii")}


def decode(core, item):
    try:
        value = base64.b64decode(item["content_base64"], validate=True)
    except (ValueError, binascii.Error):
        raise core.LoopError("Invalid embedded attachment encoding.")
    if len(value) > MAX_FILE or core.digest(value) != item["sha256"]:
        raise core.LoopError("Embedded attachment size or digest does not match.")
    return value


def with_digest(core, value):
    # This is an integrity digest, not a cryptographic signature or identity check.
    value["digest"] = core.digest(core.canonical(value))
    return value


def validate_envelope(core, value, schema_name):
    errors = core.schema_errors(value, core.read_json(core.PLUGIN / "schemas" / schema_name))
    if errors:
        raise core.LoopError("Invalid archive record: " + "; ".join(errors))
    payload = {key: val for key, val in value.items() if key != "digest"}
    if core.digest(core.canonical(payload)) != value["digest"]:
        raise core.LoopError("Archive record digest does not match.")


def bounded_json(core, path):
    if path.stat().st_size > MAX_RECORD:
        raise core.LoopError("Archive record exceeds the 24 MiB limit.")
    return core.read_json(path)


def validate_release(core, record, expected):
    validate_envelope(core, record, "release.schema.json")
    if record["id"] != expected:
        raise core.LoopError("Release ID does not match its filename.")
    clock = timestamp(core, record["sealed_at"])
    if clock > core.now() + timedelta(seconds=30):
        raise core.LoopError("Release time is in the future.")
    files = {item["path"]: decode(core, item) for item in record["files"]}
    if len(files) != len(record["files"]) or record["receipt_path"] not in files:
        raise core.LoopError("Release contains duplicate files or lacks its receipt.")
    entries = {item["contract"]["id"]: item for item in record["changes"]}
    if len(entries) != len(record["changes"]) or record["change_id"] not in entries:
        raise core.LoopError("Release contains duplicate changes or lacks its main change.")
    graph = {key: item["contract"]["depends_on"] for key, item in entries.items()}
    if any(dep not in entries for deps in graph.values() for dep in deps) or core.cycles(graph):
        raise core.LoopError("Frozen dependency graph is invalid.")
    cache = {}
    def frozen_hash(key):
        if key in cache:
            return cache[key]
        contract = json.loads(json.dumps(entries[key]["contract"]))
        contract.pop("phase", None)
        for task in contract["tasks"]:
            task.pop("status", None)
        artifacts = []
        for item in contract["artifacts"]:
            if item["path"] not in files:
                raise core.LoopError("A frozen contract artifact is missing.")
            artifacts.append([item["id"], item["path"], core.digest(files[item["path"]])])
        cache[key] = core.digest(core.canonical({"config": record["project"], "contract": contract,
            "artifacts": artifacts, "dependencies": {dep: frozen_hash(dep) for dep in graph[key]},
            "engine": record["engine_version"]}))
        return cache[key]
    for key, entry in entries.items():
        if frozen_hash(key) != entry["contract_hash"]:
            raise core.LoopError("Frozen contract digest does not match.")
        if any(task["status"] != "done" for task in entry["contract"]["tasks"]):
            raise core.LoopError("Frozen release has unfinished tasks.")
        for check in entry["contract"]["checks"]:
            if check["purpose"] == "outcome":
                continue
            state = core.check_evidence(None, check, entry["evidence"], entry["contract_hash"],
                                       record["source_hash"], clock, frozen_files=files)
            if state != "pass":
                raise core.LoopError(f"Frozen evidence {key}/{check['id']}: {state}")
    return entries, files


def read_release(core, root, release_id):
    record = bounded_json(core, release_path(core, root, release_id))
    entries, _ = validate_release(core, record, release_id)
    return record, entries


def seal(core, root, args):
    path = release_path(core, root, args.release)
    with core.writer(root):
        if path.exists():
            raise core.LoopError("Release ID already exists. Existing history was preserved.")
        report = core.gate(root, args.change, "release")
        if not report["passed"]:
            raise core.LoopError("Release gate failed: " + "; ".join(report["errors"]))
        config, changes, _ = core.select(root, args.change)
        source = core.snapshot(root)
        pending, included, files = [args.change], {}, {}
        while pending:
            key = pending.pop()
            if key in included:
                continue
            contract = changes[key]
            records = core.evidence_records(root, contract)
            selected = []
            for check in contract["checks"]:
                if check["purpose"] == "outcome":
                    continue
                candidates = [item for item in records if item["check_id"] == check["id"]]
                selected.append(max(candidates, key=lambda item: timestamp(core, item["observed_at"])))
            included[key] = {"contract": contract, "contract_hash": core.contract_hash(root, config, contract),
                             "evidence": selected}
            for relative in [item["path"] for item in contract["artifacts"]] + [item["artifact"] for item in selected if item["artifact"]]:
                files[relative] = blob(core, root, relative)
            pending.extend(contract["depends_on"])
        files[args.receipt] = blob(core, root, args.receipt)
        artifact_path = core.inside(root, args.artifact)
        if not artifact_path.is_file():
            raise core.LoopError("The released artifact must be an existing regular file.")
        hasher, count = hashlib.sha256(), 0
        with artifact_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                hasher.update(chunk)
                count += len(chunk)
        record = with_digest(core, {"schema_version": 1, "id": args.release,
            "sealed_at": core.stamp(), "engine_version": core.VERSION, "change_id": args.change,
            "target": args.target, "observer": args.observer, "authority_ref": args.authority_ref,
            "source_hash": source, "project": config, "changes": list(included.values()),
            "files": list(files.values()), "receipt_path": args.receipt,
            "artifact": {"path": args.artifact, "sha256": hasher.hexdigest(), "size_bytes": count},
            "trust": "local-untrusted"})
        validate_release(core, record, args.release)
        current_config, current_changes = core.load_project(root)
        if core.snapshot(root) != source or any(core.contract_hash(root, current_config, current_changes[key]) != item["contract_hash"] for key, item in included.items()):
            raise core.LoopError("Release inputs changed while sealing. No record was written.")
        if len(json.dumps(record, ensure_ascii=False, indent=2).encode()) + 1 > MAX_RECORD:
            raise core.LoopError("Release record exceeds the 24 MiB limit.")
        core.atomic_json(path, record)
    return {"release": args.release, "digest": record["digest"], "sealed": True,
            "trust": "Local recorded evidence; no deployment or authenticated approval was performed."}


def observe(core, root, args):
    with core.writer(root):
        release, entries = read_release(core, root, args.release)
        contract = entries[release["change_id"]]["contract"]
        check = next((x for x in contract["checks"] if x["id"] == args.check), None)
        if not check or check["purpose"] != "outcome" or check["kind"] != "manual":
            raise core.LoopError("Select a manual outcome check from the frozen main change.")
        record = with_digest(core, {"schema_version": 1, "id": "OBS-" + uuid.uuid4().hex,
            "release_id": args.release, "release_digest": release["digest"], "check_id": args.check,
            "observed_at": core.stamp(), "window_start": args.window_start, "window_end": args.window_end,
            "cohort": args.cohort, "observer": args.observer, "notes": args.note, "result": args.result,
            "artifact": blob(core, root, args.artifact), "trust": "local-untrusted"})
        validate_observation(core, record, release, {check["id"]})
        path = core.inside(root, f"{core.META}/releases/{args.release}/observations/{record['id']}.json")
        if path.exists():
            raise core.LoopError("Observation ID collision; no record was replaced.")
        core.atomic_json(path, record)
    return {"release": args.release, "observation": record["id"], "result": args.result}


def validate_observation(core, record, release, check_ids):
    validate_envelope(core, record, "outcome.schema.json")
    if record["release_id"] != release["id"] or record["release_digest"] != release["digest"] or record["check_id"] not in check_ids:
        raise core.LoopError("Observation does not match the frozen release and outcome check.")
    observed = timestamp(core, record["observed_at"])
    start, end = timestamp(core, record["window_start"]), timestamp(core, record["window_end"])
    if not (start <= end <= observed <= core.now() + timedelta(seconds=30)) or observed < timestamp(core, release["sealed_at"]):
        raise core.LoopError("Observation window or record time is invalid.")
    decode(core, record["artifact"])


def learn(core, root, release_id):
    release, entries = read_release(core, root, release_id)
    checks = [x for x in entries[release["change_id"]]["contract"]["checks"] if x["purpose"] == "outcome"]
    records = []
    folder = core.inside(root, f"{core.META}/releases/{release_id}/observations")
    for path in sorted(folder.glob("*.json")):
        path = core.inside(root, path.relative_to(root).as_posix())
        record = bounded_json(core, path)
        validate_observation(core, record, release, {x["id"] for x in checks})
        if path.stem != record["id"]:
            raise core.LoopError("Observation ID does not match its filename.")
        records.append(record)
    states = {}
    for check in checks:
        candidates = [x for x in records if x["check_id"] == check["id"]]
        if check["kind"] != "manual":
            states[check["id"]] = "automated historical outcome collection is not supported"
        elif not candidates:
            states[check["id"]] = "missing"
        else:
            states[check["id"]] = max(candidates, key=lambda x: timestamp(core, x["observed_at"]))["result"]
    return {"release": release_id, "passed": bool(checks) and all(x == "pass" for x in states.values()),
            "checks": states, "errors": [] if checks else ["The frozen change has no outcome check."],
            "trust": "Historical local observations. Observer identity, cohort, causality, and target are not independently verified."}


def execute(core, root, args):
    if args.command == "release-seal":
        return seal(core, root, args)
    if args.command == "release-observe":
        return observe(core, root, args)
    if args.command == "release-learn":
        return learn(core, root, args.release)
    record, entries = read_release(core, root, args.release)
    return {"release": record["id"], "passed": True, "digest": record["digest"],
            "sealed_at": record["sealed_at"], "engine_version": record["engine_version"],
            "target": record["target"], "artifact": record["artifact"], "changes": sorted(entries),
            "basis": "Frozen evidence at seal time; current source files were not checked.", "trust": record["trust"]}
