# Star-burger
## О приложении
Сайт для сети доставки готовой еды. [Демоверсия](https://lucky0ne.duckdns.org/) реализована на примере сети бургеров. Клиент выбирает продукты, оформляет заказ, указывая адрес куда доставить. 
## [Интерфейс клиента](https://lucky0ne.duckdns.org/) 
Клиенту не нужно регистрироваться для того чтобы заказать. Подразумевается что клиент хочет просто заказать еды, лениво, просто и быстро.  
~~Бесплатно, без регистрации и смс~~.

![Пример заказа](demo/interface/order.gif)

## [Интерфейс администратора](https://lucky0ne.duckdns.org/manager/orders/)
![Интерфейс менеджера](demo/interface/manager.gif)  
Администратор должен быть зарегистрирован на сайте с пометкой персонала.  
Интерфейс менеджера разбит на три экрана - продукты, рестораны, заказы.  
Администратор имеет возможность просмотра, редактирования, добавления.
Кстати зацените что приложуха сама считает расстояние от адреса доставки до всех ресторанов в которых можно приготовить конкретный заказ.

## Мониторинг
Приложение настроено для работы с [Rollbar](https://app.rollbar.com/).  
Интерфейс сервиса предоставляет:
 - Экран ошибок
 ![alt text](demo/rollbar/items.png)
 - Экран деплоев
 ![alt text](demo/rollbar/deploy.png)
 И еще несколько экранов, сами разберетесь=)

## Запуск в среде разработки
### Получите свои токены:  
[yandex geocoder](https://yandex.ru/maps-api/products/geocoder-api)
нужен для расчета расстояния от адреса доставки до ресторанов  
[rollbar](https://rollbar.com) нужен для мониторинга работы сайта  
[django secret key](https://djecrety.ir/)  просто генератор, который вычислит вас по айпи и угонит ваши сервера

### Настройте переменные окружения
```env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,любой другой хостнейм или айпи сайта
SECRET_KEY=ваш ключ проекта джанго

YANDEX_GEOCODER_API_KEY=ваш токен геокодера яндекса
ROLLBAR_TOKEN=ваш токен rollbar

DB_SCHEMA=-c search_path=myschema
DATABASE_URL=postgresql://psql-user:password@host:port/databasename # подробнее ниже
```
DATABASE URL нам понадобится если вы хотите себе PostgreSQL.  
Теперь о том, как его сделать (в смысле постгрес):
```bash
sudo apt install -y postgresql-common
sudo su - postgres
psql
CREATE DATABASE mydb;
CREATE USER myuser WITH PASSWORD 'mypassword';

\connect mydb;

CREATE SCHEMA myschema AUTHORIZATION myuser;

ALTER ROLE myuser SET client_encoding TO 'utf8';
ALTER ROLE myuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE myuser SET timezone TO 'UTC';
# Запомните или запишите имя базы данных, пользователя, пароль и схему 
# вот их вы и занесете в .env DATABASE_URL
```
Если захотите сохранить и/или перенести данные из бэдэшечки то есть вот что:
```bash
manage.py dumpdata --exclude contenttypes > db.json 
# выкачает в жсончик данные из базы, 
# на которую прямо сейчас настроен джанго
manage.py loaddata db.json 
# вкачает данные из жсончика в новую бд, 
#но не забудьте сначала переключить джанго на новую бд и отмигрировать
```

Теперь соберем бэкэнд  
```bash
sudo apt install python3 git
git clone https://github.com/Skripko-A/star-burger
cd star-burger
python3 -m venv .venv
source .venv/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```
В новом окне (вкладке) терминала соберем фронтэнд
```bash
sudo apt install nodejs
npm ci --dev
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./" # может быть нестерпимо долго но вы держитесь до конца
```
[~~Первый тост за локалхост~~](http://127.0.0.1:8000/)  

## Запуск на проде
Повторить всё тоже что и в разработке, но изменить в .env
```env
DEBUG=False
ALLOWED_HOSTS=хостнейм # например lucky0ne.duckdns.org
SECRET_KEY=ваш ключ проекта джанго

YANDEX_GEOCODER_API_KEY=ваш токен геокодера яндекса
ROLLBAR_TOKEN=ваш токен от rollbar

DB_SCHEMA=-c search_path=myschema
DATABASE_URL=postgresql://psql-user:password@host:port/databasename 
```
Запускать `runserver` на проде не надо, и `debug` тоже не надо.
Что нам понадобится:
 - `gunicorn` - вместо `runserver`
 - `nginx` - без `debug` он будет расдавать статику
 - `systemd` - демон будет крутить нужные нам процессы
 - `certbot` - чтобы у нас было https

 Итак, `gunicorn` запускаем в сервисе `ssytemd`
 ```bash
 touch /etc/systemd/system/star-burger.service
 vim /etc/systemd/system/star-burger.service
 ```
 Конфиг `star-burger.service`
 ```service
[Unit]
Description=Star-burger start
After=syslog.target
After=network.target
After=nginx.service
Requires=postgresql.service

[Service]
User=root
Group=root
WorkingDirectory=/opt/django/star-burger
ExecStart=/opt/django/star-burger/.venv/bin/gunicorn -w 3 -b 127.0.0.1:8080 star_burger.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=True
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target

```
~~Пинаем демона~~
```bash
systemctl daemon-reload
systemctl start star-burger.service
systemctl status star-burger.service # смотрим запустился ли
journalctl -u star-burger.service -n 20
# смотрим в логи сервиса если вдруг проблемы
# -f добавляем чтоыб смотреть логи "онлайн"
```
Теперь `nginx`
```bash
sudo apt install nginx
touch /etc/nginx/sites-enabled/star-burger
vim /etc/nginx/sites-enabled/star-burger
```
Конфиг `nginx` кладём в `vim`
```config
server {
    listen 80 default;
    location /media/ {
        alias /opt/django/star-burger/media/;
    }
    location /static/ {
        alias /opt/django/star-burger/staticfiles/;
    }

   location / {
        include '/etc/nginx/proxy_params';
        proxy_pass http://127.0.0.1:8080/;
    }
}
```

`certbot`
Тут отличная [офф дока](https://certbot.eff.org/lets-encrypt/)
А ещё можно настроить сертобу автоматическое обновление сертификатов:
```bash
touch /etc/systemd/system/certbot-renewal.service
vim /etc/systemd/system/certbot-renewal.service
```
```service
[Unit]
Description=Certbot Renewal

[Service]
ExecStart=/opt/certbot/.venv/bin/certbot renew --force-renewal --post-hook "systemctl reload nginx.service"
```
Теперь таймер, который будет пинать наш сервис обновления сертификатов
```bash
touch /etc/systemd/system/certbot-renewal.timer
vim /etc/systemd/system/certbot-renewal.timer
```
```timer
[Unit]
Description=Timer for Certbot Renewal

[Timer]
OnBootSec=300
OnUnitActiveSec=1w

[Install]
WantedBy=multi-user.target
```
Очистка устаревших пользовательских сессий

`clearsessions - 
Django does not provide automatic purging of expired sessions. Therefore, it’s your job to purge expired sessions on a regular basis. Django provides a clean-up management command for this purpose: clearsessions. It’s recommended to call this command on a regular basis, for example as a daily cron job.`  
Офф дока советует пихнуть его в `cron`. Так и сделаем:
```bash
crontab -e # если нажмёте -r то удалите файл крона
```
Дописываем внизу
```config
0 0 * * * /opt/django/star-burger/.venv/python3 /opt/django/star/burger manage.py clearsessions
```
Теперь очистка сессий будет происходить каждую полночь!

Ну и вишенка на торте, `bash` скрипт для деплоя.
 - обновляет с гита репу
 - обновляет библиотеки
 - пересобирает фронт
 - пересобирает статику
 - перезапускает на горячую сервисы `systemd`
 - сообщает в `rollbar` о делое

 Ищите его в корне репозитория. Удачи.


## Цель проекта
Проект написан в рамках прохождения курса веб-разработчика [Devman](https://dvmn.org/).