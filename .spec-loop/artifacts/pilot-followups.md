# Pilot corrections and limits

The initial clean checkout omitted native state.json, so context failed. The file was added and clean-checkout context was added to CI. An explicit checkpoint/resume check then changed tracked native state before packaging; the package tool correctly refused the dirty tracked tree. The completed pilot builds the committed package before recording mutable evaluation state. It does not bypass the package guard. Nineteen CLI operations then passed the local technical acceptance sequence. Host loading and human feedback remain unobserved.

The independent source/copy exercise used disposable fixtures and identified one changed product.py. Its claimed copy was not obtained from a real host. The actual pilot uses this repository's diagnostics module and native records. CI validates the exact remote source after transfer. Source and remote Git histories differ; tree/source digests carry the comparison, not an assumed shared commit history.
