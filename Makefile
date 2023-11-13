pre-commit:
	pipenv run pre-commit install --install-hooks

update:
	pipenv run pip freeze > requirements.txt
