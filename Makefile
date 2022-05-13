build:
	pip install -U pip setuptools wheel 
	pip install -U spacy 
	python -m spacy download es_core_news_sm
	pip install redis
	pip install progressbar
	pip install ipykernel
	pip install notebook

run: 
  	docker-compose up -d && jupyter notebook test.ipynb