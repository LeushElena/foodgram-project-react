# Дипломный проект "Продуктовый помощник Foodgram"

### Описание проекта
[Админка]: <http://178.154.221.216/admin/>

Тестовый пользователь: 
- login: test_user@test.ru
- password: test777

Возможности сервиса:

- Регистрация пользователей.
- Создание, изменение, удаление рецептов.
- Добавление рецептов в избранное, просмотр избранных рецептов.
- Фильтрация рецептов по тегам.
- Подписка на авторов и просмотр его рецептов.
- Добавление рецептов и скачивание списка покупок для их приготовления в формате .txt

### Алгоритм регистрации пользователей:
Регистрация проходит на сайте, по форме регистрации.

### Запуск проекта
Проект собран в Docker 20.10.07 и содержит четыре контейнера:
- backend - бэк проекта
- frontend - фронт проекта
- postgres - образ базы данных PostgreSQL v 13.02
- nginx - образ web сервера nginx

1. Клонируйте проект 
```bash
git clone https://github.com/LeushElena/foodgram-project-react
```
2. [Установите Докер](https://docs.docker.com/engine/install/)

3. [Установите docker-compose, ссылка на официальную документацию](https://docs.docker.com/compose/install/)

4. Перейдите в каталок проекта:
```bash
- cd foodgram-project-react
```
5. Переименуйте dev.env в .env и заполните его.

6. Перейдите в каталог infra и запустите создание контейнеров:
```bash
- cd infra
- docker-compose up -d --build
```

#### Первоочередная настройка Django:
```bash
- docker-compose exec backend python manage.py makemigrations api --noinput
- docker-compose exec web python manage.py migrate --noinput
- docker-compose exec web python manage.py collectstatic --no-input
```

#### Создание суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Автор
Автор Леуш Елена. Проект был выполнен в рамках курса от Yandex Praktikum по бекенд разработке.
