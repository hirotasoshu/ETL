# Проектное задание: ETL

Написать отказоустойчивый перенос данных из Postgres в Elasticsearch

# Dev зависимости
1. Установить dev зависимости и создать .env файл на основе .env.template:
```console
$ make install
```
# Docker
Потребуется уже запущенная postgres (локально или в другом докер контейнере)
Параметры подключения для нее находятся в .env
Базу можно взять [отсюда](https://github.com/hirotasoshu/Admin_panel_sprint_2)
1. Запуск приложения (если вы не выполняли команду выше, не забудьте создать .env файл)
```console
$ make up
```
2. Остановка приложения

```console
$ make down
```

3. Удалить все volumes
```console
$ make destroy
```

4. Открыть ETL логи
```console
$ make etl-logs
```
