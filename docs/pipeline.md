# Pipeline

## End-to-end loop

1. Codex edits files under the addon root.
2. Codex packages the current working tree addon snapshot.
3. Codex uploads the snapshot to the broker.
4. Codex submits a job referencing that snapshot.
5. Broker materializes the snapshot under `/workspace/jobs/<job_id>/snapshot`.
6. Broker ensures Blender is running and the runtime bridge is reachable.
7. Broker installs or reloads the addon in Blender.
8. Broker runs smoke scripts:
   - addon import and registration
   - UI smoke
   - playback smoke
9. Broker writes artifacts:
   - `result.json`
   - `stdout.log`
   - `stderr.log`
   - screenshots
   - optional clip
10. Codex polls job status and reads artifacts.
