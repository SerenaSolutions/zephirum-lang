# ZEPHIRUM build targets (standard language-repo entrypoint)
.PHONY: test lint clean

test:
	@/tmp/zyvenv/bin/python -m pytest tests -q --no-header

lint:

clean:
