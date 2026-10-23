# ZEPHIRUM build targets (standard language-repo entrypoint)
.PHONY: test lint clean

test:
	python3 tests/test_canonical.py
	python3 tests/test_zqea_verify.py
	python3 tests/test_meta.py

lint:
	python3 -m py_compile src/*.py

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
