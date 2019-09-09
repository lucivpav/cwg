init: setup
	pip install pipenv
	pipenv install
	pipenv install --dev

setup:
	./setup.sh

test:
	(cd backend; pipenv run python -m unittest discover)
