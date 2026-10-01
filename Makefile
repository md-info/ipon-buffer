PYTHON ?= python
.PHONY: setup check demo sim test
setup check demo sim test:
	$(PYTHON) scripts/tasks.py $@
