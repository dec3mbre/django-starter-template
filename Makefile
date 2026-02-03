.PHONY: run migrate install test lint shell superuser clean

run:
	python manage.py runserver

migrate:
	python manage.py makemigrations
	python manage.py migrate

install:
	pip install -r requirements/dev.txt

test:
	pytest

lint:
	ruff check .
	ruff format .

shell:
	python manage.py shell_plus

superuser:
	python manage.py createsuperuser

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
