# Foodgram
---

Продуктовый помощник - сервис с коллекцией рецептов.
Позволяет просматривать и добавлять рецепты, подписываться на авторов, сохранять рецепты в избранное и формировать список покупок.

Проект доступен по адресу http://158.160.26.77


## Стек технологий
- Python 3.7
- Django 3.2.16
- Dango Rest Framework 3.12.4
- Gunicorn 20.0.4
- Nginx 1.21.3
- PostgreSQL
- Docker

## Локальный запуск проекта
1. Клонировать репозиторий
```
git clone git@github.com:ilyakhakhalkin/foodgram-project-react.git
```
2. Установить Docker и docker-compose:
```
https://docs.docker.com/get-docker/
https://docs.docker.com/compose/install/
```
3. В корне проекта создать файл .env с найстройками PostgreSQL:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=придумайте пароль для базы данных
DB_HOST=db
DB_PORT=5432
```
4. В файле .env указать любой секретный ключ:
```
SECRET_KEY=m()1-a#g)k3oizjr2=v7qo8j)5e&j5gu_4ncdoyk$tfu8g#ul%
```
5. Из папки infra выполнить docker-compose:
```
docker-compose up -d
```
6. В контейнере back загрузить данные в базу данных:
```
docker exec -it back bash
python manage.py loaddata dump.json
```
7. В базе уже создан суперпользователь:
```
username: adm
email: adm@adm.ru
password: adm
```
8. Для создания своего суперпользователя выполнить команды:
```
docker exec -it back bash
python manage.py createsuperuser
```

### Список адресов
1. Главная страница: http://localhost/
2. Админ-панель: http://localhost/admin/
3. Документация API: http://localhost/api/docs/


#### Информация об авторе
Хахалкин Илья - студент Яндекс.Практикума, Python-разработчик