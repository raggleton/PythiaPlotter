.PHONY: clean clean-test clean-pyc clean-build docs
docs:
	cp README.rst docs/main.rst
	sed -i '.bak' 's@docs/@@g' docs/main.rst
	sphinx-apidoc -f -H PythiaPlotter -o docs/ pythiaplotter/
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	@echo "HTML index: docs/_build/html/index.html"

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

examples: test test-examples## update example outputs, but only if our tests are ok
	@echo "Remaking examples..."
	PythiaPlotter example/example_pythia8.txt --inputFormat PYTHIA -O example/example_pythia8.pdf
	PythiaPlotter example/example_pythia8.txt --inputFormat PYTHIA -p WEB -O example/example_pythia8.html
	PythiaPlotter example/example_cmssw.txt --inputFormat CMSSW -O example/example_cmssw.pdf
	PythiaPlotter example/example_cmssw.txt --inputFormat CMSSW -p WEB -O example/example_cmssw.html
	PythiaPlotter example/example_lhe.lhe --inputFormat LHE -O example/example_lhe.pdf
	PythiaPlotter example/example_lhe.lhe --inputFormat LHE -p WEB -O example/example_lhe.html
	PythiaPlotter example/example_hepmc.hepmc --inputFormat HEPMC -O example/example_hepmc.pdf
	PythiaPlotter example/example_hepmc.hepmc --inputFormat HEPMC -p WEB -O example/example_hepmc.html
	PythiaPlotter example/example_heppy.root --inputFormat HEPPY -O example/example_heppy.pdf
	PythiaPlotter example/example_heppy.root --inputFormat HEPPY -p WEB -O example/example_heppy.html
	PythiaPlotter example/example_herwig.log --inputFormat HERWIG -O example/example_herwig.pdf
	PythiaPlotter example/example_herwig.log --inputFormat HERWIG -p WEB -O example/example_herwig.html

test: ## run standard tests
	python -m pytest -k "not test_examples_full" -r fEsp

tests: test ## cos I always forget singular or plural

test-examples: ## run full examples test
	python -m pytest -r fEsp tests/test_examples_full.py

benchmark: ## run performance metrics
	python tests/run_performance_metrics.py

cov:  ## run coverage with all tests
	coverage run -m pytest -r fEsp
	coverage report
	coverage html
	@echo "Report in htmlcov/index.html"

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
