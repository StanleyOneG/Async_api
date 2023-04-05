
**Переменные окружения**

Для запуска приложения необходимо в **корне проекта** создать `.env` файл и  заполнить его следующими переменными (значения по умолчанию оставить неизменными):
```

POSTGRES_PASSWORD=#<пароль для PostgreSQL>
POSTGRES_USER=#<имя пользователя  PostgreSQL>
POSTGRES_DB=movies_database

POSTGRES_HOST=postgresql # название Докер контейнера с базой PostgreSQL
POSTGRES_PORT=5432
POSTGRES_OPTIONS="-c search_path=content" 

ELASTIC_HOST=elasticsearch # Хост для Elasticsearch 
ELASTIC_PORT=9200 # Порт для Elasticsearch
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=#<пароль для Elasticsearch>

REDIS_ETL_HOST=redis_etl
REDIS_CACHE_API_HOST=redis_cache
REDIS_CACHE_EXPIRE=300
REDIS_CACHE_PORT=6379

SQLITE_PATH=/app/db.sqlite 
PROJECT_NAME="Read-only API для онлайн-кинотеатра"
PROJECT_DESCRIPTION="Информация о фильмах, жанрах и людях, участвовавших в создании произведения"
PROJECT_VERSION="1.0.0"
PROJECT_CACHE_SERVICE_NAME="redis"

```
**Запуск приложения**

Для запуска приложения необходимо в корневой папке проекта запустить команду `docker-compose up --build`.

**Миграция данных из SQLite в Postgres**

Миграция данных из SQLite реализована в отдельном контейнере и выполняется после проверки успешного запуска контейнера с базой PostgreSQL.


**Индексирование Elasticsearch из PostgreSQL**

ETL процесс реализован следующим образом:
1. В **Extract** модуле описан класс `ExtractorFromPostgres`, который циклически проверяет изменения в таблицах `film_work`, `person` и `genre`. Если изменения есть: 

- Возвращает id фильмов, которые нужно обновить в индексе Elasticsearch; 

- Записывает id фильмов в базу Redis для фиксации идентификаторов фильмов, которые необходимо обновить в данный момент; 

- Записывает временную отметку последней проверки PostgreSQL на предмет изменений в данных о фильмах; 

- И в методе-генераторе извлекает необходимые данные о фильмах из PostgreSQL.

2. В **Transform** модуле описан класс `Transformer`, который с помощью метода-генератора преобразует извлеченные из PostgreSQL данные о фильме в формат, подходящий для индекса Elasticsearch.

3. В **Load** модуле описан класс `ElasticLoader`, который: 

- Создает индекс "movies", если такого нет; 

- Загружает преобразованные данные о фильмах в Elasticsearch пачками по *n* фильмов.

4. Модуль **etl_process** оркестрирует ETL процесс, вызывая методы описанных классов в соответствующем порядке.

- Процесс реализован в отдельном Docker контейнере, который стартует только после проверки успешного завершения контейнера-загрузчика данных из SQLite в PostgreSQL и успешного старта контейнеров с базами PostgreSQL, Redis и Elasticsearch.


**API**

###### Документация в формате OpenAPI:

http://localhost/api/openapi

###### Ссылки
 - Cписок фильмов: http://localhost/api/v1/films
 - Детали фильма: http://localhost/api/v1/film/film_uuid
 - Фильмы похожие по жанру: http://localhost/api/v1/films/film_uuid/similar
 - Поиск по фильмам: http://localhost/api/v1/films/search?query=
 - Детальная информация о персоне: http://localhost/api/v1/persons/person_uuid
 - Поиск по персонам: http://localhost/api/v1/persons/search?query=
 - Фильмы в которых участвовал(а): http://localhost/api/v1/persons/person_uuid/film
 - Список жанров: http://localhost/api/v1/genres
 - Детали жанра: http://localhost/api/v1/genres/genre_uuid/

**Тесты**

Тесты работы api реализованы с помощью библиотеки pytest. 
Для запуска функциональных тестов необходимо:

1. В папке `tests/functional` создать `.env` файл (пример расположен в файле `tests/functional/.env.example`) 
2. В консоли перейти в директорию `tests/functional` и выполнить команду `docker-compose up --build --exit-code-from tester`. 

*Функционал `wait-for-it` для контейнеров реализован методами docker-compose healthcheck в соответствующем файле `tests/functional/docker-compose.yml`*

