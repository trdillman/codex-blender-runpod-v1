# AGENTS.md

Use this workflow inside Codex Cloud for this project.

## Primary loop

1. Make code changes under the addon root.
2. Package the current in-progress addon snapshot:
   ```bash
   python codex/upload_snapshot.py --addon-root "$ADDON_ROOT" --module-name "$ADDON_MODULE"
   ```
3. Submit a Blender sandbox job:
   ```bash
   python codex/submit_job.py --snapshot-id <SNAPSHOT_ID> --wait
   ```
4. Inspect `result.json`, logs, screenshots, and clips.
5. Iterate until the result is green.

## Rules

- Do not assume branch head equals the addon state under test.
- Always run against a snapshot created from the current working tree.
- Prefer artifact-driven validation over live viewer dependency.
- Use the viewer only when a human needs to confirm viewport/UI behavior.
- Avoid adding new network destinations without updating the Codex environment allowlist.
