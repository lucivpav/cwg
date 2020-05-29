init: setup
	pip install pipenv
	pip install codecov
	pipenv install
	pipenv install --dev

setup:
	./setup.sh

test:
	(export PYTHONPATH=$$PYTHONPATH:src; cd backend; pipenv run pytest test)
	(export PYTHONPATH=$$PYTHONPATH:src; cd backend; pipenv run pytest test --cov ./src)
