.PHONY: install-deps test lint sample images run-vision run-ocr report

MODEL := gemini-3.5-flash-lite

# Uso:
# make install-deps
install-deps:
	uv sync

# Uso:
# make test
test:
	uv run pytest

# Uso:
# make lint
lint:
	uv run ruff check .
	uv run ruff format --check .

# Uso:
# make sample
sample:
	uv run python scripts/build_sample.py

# Uso:
# make images
images:
	uv run python scripts/download_images.py

# Uso:
# make run-vision
run-vision:
	set -a && . ./.env && set +a && uv run python scripts/run_experiment.py --source vision --model $(MODEL)

# Uso:
# make run-ocr
run-ocr:
	set -a && . ./.env && set +a && uv run python scripts/run_experiment.py --source ocr --model $(MODEL)

# Uso:
# make report
report:
	uv run python scripts/report.py
