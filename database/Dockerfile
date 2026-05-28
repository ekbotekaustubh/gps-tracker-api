FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=toor
ENV MYSQL_ROOT_USERNAME=root

COPY ./mysql-init.sql /docker-entrypoint-initdb.d/
