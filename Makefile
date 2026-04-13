PYTHON ?= python3

.PHONY: broker-dev
broker-dev:
	cd broker && $(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

.PHONY: local-start
local-start:
	pwsh -File infra/local/start_local_stack.ps1

.PHONY: runpod-deploy
runpod-deploy:
	$(PYTHON) infra/runpod/deploy_pod.py

.PHONY: upload-snapshot
upload-snapshot:
	$(PYTHON) codex/upload_snapshot.py --addon-root "$(ADDON_ROOT)" --module-name "$(ADDON_MODULE)"

.PHONY: submit-job
submit-job:
	$(PYTHON) codex/submit_job.py --wait
