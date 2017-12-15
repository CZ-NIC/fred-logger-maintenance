APP = logger_maintenance drop_parts.py create_parts.py tests.py

.PHONY: default isort check-isort check-flake8 check-doc check-all

default: check-all

isort:
	python3 -m isort --recursive ${APP}

check-all: check-isort check-flake8 check-doc

check-isort:
	python3 -m isort --recursive --check-only --diff ${APP}

check-doc:
	python3 -m pydocstyle ${APP}

check-flake8:
	python3 -m flake8 --config=.flake8 --format=pylint --show-source ${APP}

test:
	python3 -m unittest tests.py

test-coverage:
	coverage3 run --source . --omit setup.py --branch -m unittest tests.py 
