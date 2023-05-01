build:
	sudo docker-compose build
up:
	sudo docker-compose up -d
logs:
	sudo docker-compose logs
down:
	sudo docker-compose down -v
reup:
	sudo docker-compose down -v
	sudo docker-compose build
	sudo docker-compose up -d
reup_api:
	sudo docker-compose down -v server
	sudo docker-compose build server
	sudo docker-compose up -d server