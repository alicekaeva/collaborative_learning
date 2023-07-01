FROM nginx/unit:1.29.1-php8.1 as stateful

EXPOSE 8080

RUN apt update -y && \
    apt install zip unzip && \
    apt clean

RUN set xe && \
    cd /tmp/ && \
    php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" && \
    php -r "if (hash_file('sha384', 'composer-setup.php') === 'e21205b207c3ff031906575712edab6f13eb0b361f2085f1f1237b7126d785e826a450292b6cfd1d64d92e6563bbde02') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" && \
    php composer-setup.php --install-dir=/usr/local/bin/ --filename=composer && \
    php -r "unlink('composer-setup.php');"

RUN docker-php-ext-install -j$(nproc) pdo pdo_mysql

FROM stateful as stateless

COPY ./nginx-unit/config.json /docker-entrypoint.d/

USER nobody
WORKDIR /app

ARG APP_ENV=dev
ENV COMPOSER_HOME=/app/.composer.cache

COPY --chown=nobody . /app

RUN set -xe && \
    echo APP_ENV="$APP_ENV" > .env.local && \
    echo DATABASE_URL= >> .env.local && \
    if [ "${APP_ENV}" = "prod" ] ;then \
    composer install --optimize-autoloader --no-dev \
    ;else \
    composer install --optimize-autoloader \
    ;fi && \
    composer dump-autoload --classmap-authoritative --optimize && \
    composer dump-env "$APP_ENV" && \
    php bin/console cache:warmup && \
    rm -rf $COMPOSER_HOME

USER ""
