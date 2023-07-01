# Инструкция по развертыванию системы для совместного обучения

Рекомендуемая ОС для развертывания: macOS или Linux

## Клонирование

```shell
git clone https://github.com/alicekaeva/collaborative_learning
cd collaborative_learning
```

## Настройка для демонстрации рабочего продукта

```shell
cp docker-compose.prod.yml docker-compose.yml
docker compose pull
docker compose up -d --force-recreate
```

## Настройка для локальной разработки
```shell
cp docker-compose.dev.yml docker-compose.yml
docker compose run --no-deps nginx-unit composer install
docker compose up -d --force-recreate
```
### Сборка и push докер образа
```shell
docker compose build
docker compose push
```

## Импортирование тестовых данных
```shell
cat init/stubs.sql | docker compose exec -T mysql mysql -uuser -ppassword
```

## Развернутый проект будет находиться по ссылке http://127.0.0.1:9999/