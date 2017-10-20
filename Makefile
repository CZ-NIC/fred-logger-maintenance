APP = logger_maintenance drop_parts.py tests.py

.PHONY: default isort check-isort check-flake8 check-doc check-all

default: check-all

isort:
	isort --recursive ${APP}

check-all: check-isort check-flake8 check-doc

check-isort:
	isort --recursive --check-only --diff ${APP}

check-doc:
	pydocstyle ${APP}

check-flake8:
	flake8 --config=.flake8 --format=pylint --show-source ${APP}

test:
	python tests.py

test-coverage:
	coverage run --source . --omit setup.py,tests.py tests.py
