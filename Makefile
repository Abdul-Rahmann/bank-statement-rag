.PHONY: test lint format run refresh install docker-build docker-up

test:
	pytest tests/ --cov=src --cov-report=term

lint:
	ruff check src/ streamlit_app/ cli.py

format:
	ruff format src/ streamlit_app/ cli.py

run:
	streamlit run streamlit_app.py

refresh:
	python cli.py --refresh

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

docker-build:
	docker compose build

docker-up:
	docker compose up -d
