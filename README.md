# Foodgram
---
![example workflow](https://github.com/ilyakhakhalkin/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Grocery Helper is a recipe collection service that allows users to view and add recipes, subscribe to authors, save recipes to favorites, and create a shopping list.

http://81.200.152.65/


## Tech stack
- Python 3.7
- Django 3.2.16
- Dango Rest Framework 3.12.4
- Gunicorn 20.0.4
- Nginx 1.21.3
- PostgreSQL
- Docker

## How to run project
1. Clone repo
```
git clone git@github.com:ilyakhakhalkin/foodgram-project-react.git
```
2. Install Docker and docker-compose:
```
https://docs.docker.com/get-docker/
https://docs.docker.com/compose/install/
```
3. Create the .env file at the project root directory and provide settings for PostgreSQL:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your password
DB_HOST=db
DB_PORT=5432
```
4. Provide any secret key in the .env file:
```
SECRET_KEY=m()1-a#g)k3oizjr2=v7qo8j)5e&j5gu_4ncdoyk$tfu8g#ul%
```
5. Run docker-compose from the infra/ folder:
```
docker-compose up -d
```
6. Load DB data inside the "back" container:
```
docker exec -it back bash
python manage.py loaddata dump.json
```
7. Superuser is already present in database:
```
username: adm
email: adm@adm.ru
password: adm
```
8. If you want to create your own superuser, run these commands:
```
docker exec -it back bash
python manage.py createsuperuser
```
9. Run this command from the infra/ folder if you want to stop all containers:
```
docker-compose down
```

### Important links
1. Home page: http://localhost/
2. Admin panel: http://localhost/admin/
3. API docs: http://localhost/api/docs/


#### Author
Ilya Khakhalkin - Yandex.Practicum student, Python Developer
