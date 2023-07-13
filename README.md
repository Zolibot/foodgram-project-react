# **praktikum_new_diplom**

![githab](https://raw.githubusercontent.com/Zolibot/Interview_of_a_real_fighter/main/food.gif)

![](https://img.shields.io/badge/license-MIT-green)
![](https://img.shields.io/badge/Powered%20by-Python3.9-green)

---

## **Оглавление**

- [**praktikum\_new\_diplom**](#praktikum_new_diplom)
  - [**Оглавление**](#оглавление)
    - [**Проект Foodgram**](#проект-foodgram)
    - [**Описание функциональности**](#описание-функциональности)
        - [**Основные функции сайта включают:**](#основные-функции-сайта-включают)
      - [**Технологии:**](#технологии)
    - [**Запуск проекта через Docker compose**](#запуск-проекта-через-docker-compose)
      - [**Настройка файла окружения .env**](#настройка-файла-окружения-env)
      - [**_Установка Docker_**](#установка-docker)
      - [**Запуск**](#запуск)
    - [**Настройка CI/CD используя GitHab Action**](#настройка-cicd-используя-githab-action)
      - [**Список переменных:**](#список-переменных)
  - [**Для проверки вход в Админ панель**](#для-проверки-вход-в-админ-панель)
  - [**Авторы**](#авторы)

---

### **Проект Foodgram**

Проект "Рецепты онлайн" - это веб-приложение, разработанное на основе` Django REST framework` с использованием `gunicorn` для взаимодействия `Django` и `Nginx`. В проекте также используется `PostgreSQL` для хранения данных, а сам проект развертывается в `Docker` контейнерах.

### **Описание функциональности**

Сайт представляет собой платформу, где пользователи могут публиковать свои рецепты блюд, подписываться на авторов публикаций, создавать список избранных рецептов и добавлять рецепты в список покупок. Пользователи могут также скачивать список ингредиентов для покупок и использовать его при походе в магазин.

##### **Основные функции сайта включают:**

- Регистрацию и аутентификацию пользователей
- Создание, редактирование и удаление рецептов
- Просмотр списка всех опубликованных рецептов
- Подписка на авторов рецептов и просмотр их профилей
- Добавление рецептов в список избранных
- Скачивание списка ингредиентов для покупок
- Фильтрация рецептов по тегам

#### **Технологии:**

- ![](https://img.shields.io/badge/Python-3.9-brightgreen)
- ![](https://img.shields.io/badge/Django-3.2-brightgreen)
- ![](https://img.shields.io/badge/Nginx-1.19.3-brightgreen)
- ![](https://img.shields.io/badge/NodeJs-13.12.0-brightgreen)
- ![](https://img.shields.io/badge/Gunicorn-20.1.0-brightgreen)
- ![](https://img.shields.io/badge/Docker-24.0.2-brightgreen)
- ![](https://img.shields.io/badge/PostgreSQL-13.10-brightgreen)

---

### **Запуск проекта через Docker compose**

- клонировать репозиторий или скачать архив

```bash
git clone git@github.com:Zolibot/foodgram-project-react.git
```

---

#### **Настройка файла окружения .env**

- В корневом каталоге создать файл **.env**

```bash
touch .env
```

- Добавить переменные среды для базы данных и `backend`

```bash
# Postgres setup
POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
# Django setup
SECRET_KEY='django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ALLOWED_HOSTS='xxx.xxx.xxx.xxx 127.0.0.1 localhost your.domain.name.org'
DEBUG=True
```

- копировать так же на удаленный сервер предварительно создав папку `foodgram`

```bash
scp -i ~/.ssh/ssh-key .env server-login@xxx.xxx.xxx.xxx:/home/server-login/foodgram/.env
```

---

#### **_[Установка Docker](https://docs.docker.com/desktop/uninstall/)_**

---

**Установка Docker на Linux**

- В терминале вести команды

```bash
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

- Проверка установки `Docker`

```bash
sudo docker -v
```

- Вывод

```bash
Docker version 23.0.1, build e92dd87
```

- Проверка установки `Docker Compose`

```bash
sudo docker compose version
```

- Вывод

```bash
Docker Compose version 2.16.0
```

---

#### **Запуск**

- На локальном сервере в папке `infra/`

```bash
sudo docker compose -f docker-compose.yml up
```

- Копировать файл `Docker Compose`, файл настроек `Nginx` на удаленный сервер предварительно создав папку `foodgram`

```bash
scp -i ~/.ssh/ssh-key infra/docker-compose.production.yml server-login@xxx.xxx.xxx.xxx:/home/server-login/foodgram/docker-compose.production.yml

scp -i ~/.ssh/ssh-key infra/nginx.conf server-login@xxx.xxx.xxx.xxx:/home/server-login/foodgram/nginx.conf

scp -i ~/.ssh/ssh-key .env server-login@xxx.xxx.xxx.xxx:/home/server-login/foodgram/.env
```

- На удаленном сервере в режиме демона

```bash
sudo docker compose -f docker-compose.production.yml up -d
```

- Собрать статику для `backend`

```bash
sudo docker exec kittygram_final-backend-1 python manage.py collectstatic --noinput
```

---

### **Настройка CI/CD используя GitHab Action**

- Для корректной работы `GitHub Actions` необходимо задать переменные для работы с контейнерами, удаленным сервером и телеграм-ботом.

#### **Список переменных:**

```bash
# доступ к DockerHab обновления образов
DOCKER_USERNAME=yous_dockerhab_login
DOCKER_PASSWORD=yous_dockerhab_password
# настройки базы данных
POSTGRES_DB=django
POSTGRES_PASSWORD=django_password
POSTGRES_USER=django
DB_HOST=db
DB_PORT=5432
# ip адрес удаленной машины
USER=yous_server_login
HOST=xxx.xxx.xxx.xxx
# доступ к удаленному серверу
# закрытый ключ ssh
SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----xxxx-----END OPENSSH PRIVATE KEY-----
# фраза для закрытого ключа
SSH_PASSPHRASE=passphrase
# отправка сообщения об успешной сборки
# id кому отправить
TELEGRAM_TO=128xxxxxxx
# токен Telegram бота
TELEGRAM_TOKEN=123456:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# Django setup
SECRET_KEY='django-insecure-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
ALLOWED_HOSTS='xxx.xxx.xxx.xxx 127.0.0.1 localhost your.domain.name.org'
DEBUG=True
```

- В случае успешного выполнения программы, `Telegram-бот` отправит сообщение об успешной сборке и развертывании на удаленном сервере, а также обновятся образы на `DockerHub`.

---

## **Для проверки вход в Админ панель**

- [адрес](https://floodapocalypse.zapto.org) Админ панели
```
https://floodapocalypse.zapto.org/admin/
```

- Email
```
d.banana@fruitmail.com
```
- Password
```
murdermuffin
```

## **Авторы**

_[Александр Андреевич](https://github.com/Zolibot)_

![GitHub followers](https://img.shields.io/github/followers/Zolibot?style=social)
