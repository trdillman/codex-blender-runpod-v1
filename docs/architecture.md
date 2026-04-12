# Architecture

## Goal

Give Codex Cloud a directly callable Blender GPU sandbox that can:

- run the exact addon snapshot currently under edit,
- execute Blender Python quickly,
- perform basic live UI and viewport checks,
- return logs, screenshots, clips, and machine-readable results.

## Chosen topology

```text
Codex Cloud
  setup script
    -> bootstrap short-lived broker token
  agent phase
    -> POST /snapshots
    -> POST /jobs
    -> GET  /jobs/{id}
    -> GET  /jobs/{id}/artifacts

Runpod Pod
  broker API        :8080/http
  Blender viewer    :3001/http
  Blender runtime   :9876/tcp (local only)
  /workspace/data
  /workspace/artifacts
  /workspace/jobs
```

## Why one Pod for v1

One Pod keeps the first delivery simple:

- no extra control-plane host,
- no inter-service network complexity,
- Codex reaches a single broker URL,
- Blender, viewer, broker, and artifacts share the same volume.

## Snapshot model

Every execution is pinned to:

- `base_sha`: Git commit Codex started from or synced to
- `snapshot_id`: immutable overlay created from the current addon working tree

## Lanes

### Runtime lane

- snapshot upload
- materialization into `/workspace/jobs/<job_id>/snapshot`
- addon install and reload
- Blender Python execution
- UI macro trigger
- artifact capture

### Provisioning lane

Deferred in v1 unless a real dependency forces it.

For now the image is expected to include:

- Blender runtime prerequisites
- Warp (`warp-lang`)
- broker dependencies
- screenshot and clip tooling
