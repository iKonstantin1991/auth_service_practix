https://github.com/iKonstantin1991/Auth_sprint_1

## Auth сервис для онлайн кинотеатра practix 

### Команды для запуска приложения

- создать `./auth-service/.env` в соответствии с `./auth-service/.env.template`
- выполнить:

```
cd ./infra
docker-compose --project-name auth-api up -d
```
- применить миграции

```
docker exec -it auth-api-auth_service-1 alembic upgrade head
```

### Команда для создания суперюзера:

```
docker exec -it -w /home/app/auth_api/src auth-api-auth_service-1 python create_superuser.py
```

### Команды для запуска тестов

- создать `./auth-service/tests/functional/.env` в соответствии с `./auth-service/tests/functional/.env.template`
- выполнить:

```
cd ./auth-service/tests/functional
docker-compose --project-name auth-api-tests up -d
```

### Контакты
https://github.com/iKonstantin1991<br>
https://github.com/kcherednichenko
