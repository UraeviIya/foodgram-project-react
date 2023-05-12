[![foodgram-project-react workflow](https://github.com/UraeviIya/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/UraeviIya/foodgram-project-react/actions/workflows/main.yml)

## Описание проекта: foodgram_project_react

Проект foodgram_project_react предсталяет собой пользовательский сервис. Пользователи могут поделиться
своими рецептами и мастерством приготавления **Вкуснейших блюд**, так же можно подписаться на автора рецепта, добавлять рецепты в «Избранное», скачать список нужных продуктов для приготовления. 

Проект был подготовлен на основе **Redoc** API документации. 
Подробнее про **Redoc** – https://redocly.com/redoc/

На данный момент сайт находится в открытом доступе по адресам:
http://pss.hopto.org
http://158.160.25.20/admin/
Логин администратора: admin@admin.com
Пороль: qwerty_1

## Запуск проекта через Docker:

Устанавливаем Docker, используя инструкции с официального сайта:
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)

Клонируйте репозиторий
```
https://github.com/UraeviIya/foodgram-project-react.git
```

В директории infra создать файл .env и заполните его:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='SECRET_KEY'
```

- ### Там же, в директории infra запустим сборку контейнеров коммандой
```
docker compose up -d --build
```

- ### Выполняем миграции
```
docker compose exec backend python manage.py migrate
```

- ### Собираем статику
```
docker compose exec backend python manage.py collectstatic --no-input
```

- ### Импортируем ингредиенты
```
docker-compose exec backend python manage.py import_ingredients
```

Теперь приложение будет доступно в браузере по адресу 127.0.0.1/admin

## Authors

- [@uraevilya](https://github.com/UraeviIya)