## Два отдельных проекта - телеграм бот и админка на Django:
Связаны за счет единой БД, реализованной на PostgreSQL. Основной функционал бота - магазин, с 
возможностью онлайн-оплаты. Информация о товарах добавляется в БД через админку Django, 
туда же падают данные о заказах. Также из нее есть экспорт данных о заказах в xlsx таблицу и
отправка администраторам email с данными о заказе на почту с помощью SMTP-аккаунта.

### Разворачивание проекта:
* ``` cd online_store/ ```
* ``` sudo socker-compose up -d ```
* ``` python3 manage.py makemigrations ```
* ``` python3 manage.py migrate ```
* ``` python3 manage.py createsuperuser ```
* ``` python3 manage.py runserver ```
* ``` cd ../tg_bot/ ```
* ``` python3 main.py ```