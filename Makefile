build:
	pip install -r requirements.txt 
	touch .env 
	echo PORT=$(port) > .env
	docker-compose build

run: 
	docker-compose up -d  
	jupyter notebook test.ipynb --post=$(port)