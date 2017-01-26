freeze: ## freeze package requirements
	pip freeze -l > requirements_new.txt
	sed -i '.bak' '/.*PythiaPlotter.*/d' requirements_new.txt
	rm requirements_new.txt.bak

flake: ## check style with flake8
	flake8 --show-source --benchmark --exit-zero pythiaplotter

lint: ## check linting with pylint
	pylint --rcfile=.pylintrc pythiaplotter

lint-py3: ## check py3 porting only, but not perfect
	pylint --rcfile=.pylintrc --py3k pythiaplotter

examples: test ## update example outputs, but only if our tests are ok
	@echo "Remaking examples..."
	PythiaPlotter examples/example_pythia8.txt --inputFormat PYTHIA
	PythiaPlotter examples/example_cmssw.txt --inputFormat CMSSW
	PythiaPlotter examples/example_lhe.lhe --inputFormat LHE
	PythiaPlotter examples/example_hepmc.hepmc --inputFormat HEPMC

test: ## run standard tests
	python -m pytest -k "not test_examples_full"

tests: test ## cos I always forget singular or plural

test-examples: ## run full examples test
	python -m pytest tests/test_examples_full.py

benchmark: ## run full examples test
	python tests/run_performance_metrics.py

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

installe: ## install the package as editable
	pip install -e .

install: ## install the package properly
	pip install .

uninstall:
	pip uninstall -y PythiaPlotter

reinstall: uninstall clean install
	@echo "Reinstalling PythiaPlotter"

reinstalle: uninstall clean installe
	@echo "Reinstalling PythiaPlotter in editable mode"

## list all targets, taken from http://stackoverflow.com/a/26339924
.PHONY: list
list:
	@echo "Available targets:"
	@echo "=================="
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
