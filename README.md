# Build and push docker image

```shell
docker compose build
docker compose push
```

# Installation

```shell
git clone https://github.com/alicekaeva/collaborative_learning
cd collaborative_learning
```

## Setup for prod

```shell
cp docker-compose.prod.yml docker-compose.yml
docker compose pull
docker compose up -d --force-recreate
```

## Setup for dev
```shell
cp docker-compose.dev.yml docker-compose.yml
docker compose run --no-deps nginx-unit composer install
docker compose up -d --force-recreate
```

## Import database stub
```shell
cat init/stubs.sql | docker compose exec -T mysql mysql -uuser -ppassword
```