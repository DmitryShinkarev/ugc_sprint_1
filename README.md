# Проектная работа 8 спринта

Проект состоит из частей:

[Admin panel](https://github.com/DmitryShinkarev/new_admin_panel_sprint_3)
[Async API](https://github.com/fall3nangel/Async_API_sprint_2)
[Auth API](https://github.com/DmitryShinkarev/Auth_sprint_2)

Тек проект.
[https://github.com/DmitryShinkarev/ugc_sprint_1](https://github.com/DmitryShinkarev/ugc_sprint_1)

В рамках спринта были реализованы следующие задачи:

1. Описана [архитектура](https://github.com/DmitryShinkarev/ugc_sprint_1/tree/main/architecture) системы в формате `plantuml`. 

2. Разработан [API](https://github.com/DmitryShinkarev/ugc_sprint_1/tree/main/api_ugc) получения сообщений о событиях и записи их в Kafka.

3. Реализованы настройки хранилищ [Kafka и ClickHouse](https://github.com/DmitryShinkarev/ugc_sprint_1/tree/main/db)

4. Разработан [ETL](https://github.com/DmitryShinkarev/ugc_sprint_1/tree/main/etl) загрузчие сообщений из Kafka в ClickHouse.

### Endpoints

`http://localhost:8000/api/openapi` - Генерированное описание OpenAPI

`http://localhost:8000/api/v1/produce` - пишет сообщение об одном событии

`http://localhost:8000/api/v1/batch_produce` - пишет массив сообщений об одном событии


### Формат сообщения

```json
{
  "payload": {
    "movie_id": "1ec4cd73-2fd5-4f25-af68-b6595d279af2",
    "user_id": "1ec4cd73-2fd5-4f25-af68-b6595d279af2",
    "event": "some_event",
    "event_data": "some_event_data",
    "event_timestamp": 1621932759
  },
  "language": "RU",
  "timezone": "Europe/Moscow",
  "ip": "192.168.1.1",
  "version": "1.0",
  "some_client_data": "some_client_data"
}
```

## Запуск проекта

Для запуска проекта необходимо запустить отдельные сервисы в том порядке, в котором они находятся в этом описании.

### Запуск кластера kafka

    cd db/kafka
    docker-compose up -d

### Запуск API
    
    cd api_ugc
    docker-compose up -d

Документация к API: http://0.0.0.0:8000/api/openapi#/

### Запуск ClickHouse

    cd db/clickhouse
    docker-compose up -d
    
### Запуск ETL
    
    cd etl
    docker-compose up -d