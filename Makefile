flake: ## check style with flake8
	flake8 --show-source --benchmark --exit-zero pythiaplotter

lint: ## check linting with pylint
	pylint --rcfile=.pylintrc pythiaplotter

lint-py3: ## check py3 porting only
	pylint --py3k pythiaplotter


test: ## run standard tests
	python -m pytest

tests: test ## cos I always forget singular or plural

test-examples: ## run full examples test
	pytest tests/test_examples_full.py

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
