<h1 align="center">Продуктовый помощник</h1>

<h4>На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.</h4>

### Стек технологий:
![python version](https://img.shields.io/badge/Python-3.7.9-green)
![django version](https://img.shields.io/badge/Django-3.2-green)
![django rest framework](https://img.shields.io/badge/DjangoRestFramework-3.12.4-green)
![Html](https://img.shields.io/badge/HTML-green)
![CSS](https://img.shields.io/badge/CSS-green)
![JavaScript](https://img.shields.io/badge/JavaScript-green)
![Docker](https://img.shields.io/badge/Docker-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-green)

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Artem-Bespalov/foodgram-project-react
```
### Развернуть докер контейнеры:
```
sudo docker-compose up
```

### Выполнить миграции, создать суперпользователя и собрать статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

### Шаблон наполнения env-файла:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```
### Автор проекта:
<a href="https://github.com/Artem-Bespalov">Артем Беспалов</a>
