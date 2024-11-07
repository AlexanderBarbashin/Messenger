# Сервис микроблогов


## О проекте

Проект представляет собой API веб приложение, разработанное на фреймворке FastAPI. API веб приложение отвечает за 
backend, за отображение интернет-страниц отвечает статическое веб приложение, которое получает запросы от клиентов,
направляет запросы на бэкенд, получает ответы и возвращает ответы клиентам.

## Особенности

* Автоматизированный запуск линтеров и тестов
* Синхронизация - легко переключаться между режимами dev и prod
* Отдельное хранение пользовательских изображений
* Разделение dev и prod окружений

## Использованные технологии

* Python 3
* FastAPI
* SQLAlchemy - ORM
* Alembic - Создание и применение миграций
* Loguru - логирование
* Gunicorn - веб-сервер
* Aiofiles - асинхронная работа с файлами
* Pytest - юнит-тестирование
* Factoryboy, Faker - генерация данных в фикстурах
* Mypy, We make python styleguide - линтеры
* Nginx - проксирование запросов на API и Docs, раздача статики
* PostgreSQL - СУБД
* Docker - контейнеризация
* Docker Compose - управление контейнерами Docker

## Подготовка и запуск

Для развертывания проекта на удаленном сервере необходимо:

### Общие требования:

* Установить Docker (если установка не была выполнена ранее)
* Склонировать проект на удаленный репозиторий: **git clone**
* Перейти в папку проекта: **cd python_advanced_diploma**
* Создать файл .env по образцу (файл .env.template), установить необходимые env опции

### Для запуска линтеров и тестов:

* Запустить скрипт (может потребоваться ввода пароля sudo): **./linters_and_tests.sh**

### Для запуска проекта в prod режиме:

* Создать файл .env.prod по образцу (файл .env.prod.template), установить необходимые env опции
* Запустить проект **docker compose up -d**
* Подключиться к БД (PgAdmin, DBeaver), создать записи пользователей