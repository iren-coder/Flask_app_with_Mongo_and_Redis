<b>Описание веб-приложения:
Это приложение является веб-сервером на Python. 
Основная база данных MongoDB.
Для кеширования используется Redis.

Приложение позволяет<ul> 
- добавлять объявления с тегами и комментариями с помощью POST запроса к серверу.
- получать существующее объявление (с тегами и комментариями) по ID с помощью GET запроса к серверу.
- добавлять тег к существующему объявлению с помощью POST запроса к серверу.
- добавлять комментарий к существующему объявлению с помощью POST запроса к серверу.
- получать статистику для данного объявления: сколько у него тегов и комментариев с помощью GET запроса к серверу.</ul>
</b>

1. Склонируйте проект.
2. Создайте виртуальное окружение <b>python -m venv env</b>
3. Активируйте виртуальное окружение <b>source env/Scripts/activate</b>
4. Перейдя в директорию с проектом введите <b>docker-compose build</b>
5. Запустите проект <b>docker-compose up</b>
6. Приложение доступно по http://localhost:5000/.