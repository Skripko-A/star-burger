# Star-burger
## О приложении
Сайт для сети доставки готовой еды. [Демоверсия](https://lucky0ne.duckdns.org/) реализована на примере сети бургеров. Клиент выбирает продукты, оформляет заказ, указывая адрес куда доставить. 
## [Интерфейс клиента](https://lucky0ne.duckdns.org/) 
Клиенту не нужно регистрироваться для того чтобы заказать. Подразумевается что клиент хочет просто заказать еды, лениво, просто и быстро. Ведь в этом и заключается идея доставки еды. Захотел поесть, выбрал продукты и написал куда доставить. Терпеть не могу когда мне голодному подсовывают сначала какие то анкеты и просят что то подтвердить на почте. Я есть хочу а не регистрироваться и получать спам.

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

YANDEX_GEOCODER_API_KEY=ваш ключ геокодера яндекса
ROLLBAR_TOKEN=ваш 

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
Идём на [~~первый тост за локалхост~~](http://127.0.0.1:8000/) 
и смотрим всё ли запустилось