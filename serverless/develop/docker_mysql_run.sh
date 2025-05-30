#!/bin/sh

docker run --name mysql8 \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_ROOT_HOST='%' \
  -p 3306:3306 \
  -d mysql:8.0.32
