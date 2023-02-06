# Foodgram
---
http://158.160.26.77

email: adm@adm.ru
pswd:  adm

Продуктовый помощник - сервис с коллекцией рецептов.
Позволяет просматривать и добавлять рецепты, подписываться на авторов, сохранять рецепты в избранное и формировать список покупок.

### Запуск проекта
1. Клонировать репозиторий
2. Создать файл .env:
```
DEBUG=True или False
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=придумайте пароль для базы данных
DB_HOST=db
DB_PORT=5432
SECRET_KEY=любой секретный ключ
```
3. Из папки infra выполнить docker-compose up
4. В контейнере back загрузить данные в базу данных:
```
docker exec -it back bash
python manage.py loaddata dump.json
```

### Документация
Документация API доступна по адресу /api/docs/
