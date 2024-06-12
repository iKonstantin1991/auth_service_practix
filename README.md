https://github.com/iKonstantin1991/auth_service_practix

## Auth сервис для онлайн кинотеатра practix 

### Команды для запуска приложения

- создать `./auth-service/.env` в соответствии с `./auth-service/.env.template`
- выполнить:

```
cd ./infra
docker-compose --project-name auth-api up -d
```

### Команда для создания суперюзера:

```
docker-compose exec auth_service python /home/app/auth_api/src/create_superuser.py
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
