# Reading list example

This is a synthetic local example. It does not represent user research or a production release.

The requested behavior is to add HTTP or HTTPS URLs to an in-memory reading list, reject invalid URLs, and avoid duplicate entries. Persistence, accounts, network access, and deployment are outside scope.

Copy this directory, including .spec-loop, to a disposable location. Initialize a Git repository there. From that project root, use the plugin tool:

```bash
git init -q
python3 /path/to/spec-loop/scripts/spec_loop.py --root . gate CHG-001 --stage ready
python3 /path/to/spec-loop/scripts/spec_loop.py --root . run CHG-001 --check CHK-001 --observer codex
python3 /path/to/spec-loop/scripts/spec_loop.py --root . gate CHG-001 --stage verify
python3 app.py https://example.com https://example.com
```

The command prints one URL. A bad scheme returns a nonzero exit code. Changing app.py after the check makes its evidence stale.

The release and operations checks are manual and initially have no evidence. Their procedures apply only to this local demonstration. Run them and write your actual observations before using record. Do not report that this example was deployed.

The outcome check is also open. It asks whether a person can complete the local task. Automated code checks cannot answer it.
