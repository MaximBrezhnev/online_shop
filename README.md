# http://online-shop-django.store/commerce/

# Интернет магазин на Django

Это полноценный проект интернет-магазина, разработанный на Django.

# Установка

1. Клонируйте репозиторий
```
git clone https://github.com/MaximBrezhnev/online_shop.git
```

2. Установите на свое устройство docker и docker compose

3. Перейдите в папку проекта
4. Создайте файл .env в данной папке по аналогии с файлом .env_example

5. Запустите контейнеры с приложением, background worker'ом celery, redis, nginx, postgres командой
```
docker compose up -d
```
6. После того как контейнеры запустились, узнайте ID контейнера приложения.
У него столбец IMAGE будет соответствовать online_shop-app
```
docker container ls
```
7. Перейдите в командную строку внутри контейнера с приложением
```
docker exec -it <ID контейнера> sh
```
8. Создайте суперпользователя для возможности администрировать сайт
```
python3 manage.py createsuperuser
```

# Готово!
Вы успешно установили магазин на Django и готовы начать его использовать!
