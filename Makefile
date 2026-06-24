.PHONY: install test smoke lint clean

install:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test:
	pytest tests/ -v

smoke:
	python -m errorlock.cli run \
		--dataset data/sample/sample_castle.json \
		--provider mock \
		--out-dir results/mock_smoke

download-data:
	python -m errorlock.cli download-castle --out data/CASTLE-C250.min.json

lint:
	python -m py_compile errorlock/*.py && echo "No syntax errors."

clean:
	rm -rf results/mock_smoke results/mock_gated_smoke results/mock_rag_smoke
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
