# Decision log

## Chosen now

- Runpod Pods for v1.
- Broker inside the same Pod as Blender for v1.
- Base SHA + overlay snapshot sync.
- Warp installed in-image via pip or vendored wheels.
- No broad package-manager or root shell control plane in v1.
- Basic browser-accessible viewer only.

## Intentionally deferred

- Broader provisioning API for privileged package installs.
- Multi-Pod fleet management.
- Auto-scaling warm pools.
- Separate durable artifact store.
- Hardened viewer auth and clip streaming.
