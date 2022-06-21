### This repository was created by [Pavel Filippenko](https://github.com/pavel-collab), [Mikhail Ovsiannikov](https://github.com/OAMichael) and [Andrey Barannikov](https://github.com/barannikovav).
<h1 align="center"> ENGLISH </h1>
### You will have to install these packages:
```console
pip install psutil
pip install python-libxdo
pip install python-telegram-bot
pip install seaborn
pip install sqlalchemy
pip install faker
pip install PyQt5
sudo apt-get install python3-gi gir1.2-wnck-3.0
```

#### How to start
##### Program named `MainServer.py` starts on main computer. Worker machines execute `Worker.py` program. There must be paths to config files as command arguments for both programs respectively. Once in a 5 seconds `Worker.py` gets necessary information and sends it to the server. Last one processes it and writes it into database immediately. If config file for server has line `bot = True` the telegram bot will be running, and boss can request information about all workers or about one particular via telegram. Moreover, being on local server you can run `QtBase.py` program, which was implemented with help of QtCreator, so file `Base.ui` is necessary. Using this program you can observe all collected data as TabWidget with multiple tables. 


#### What script should do:
1. Get information about computer of this worker
2. Send it to main server
3. Server processes this information:
	- Writes all into database
	- Plots graphs of needed quantities if possible
	- Prints information if request was made
4. After starting `QtBase.py` displays all information about all workers
5. Send all data to telegram for boss via `TGBot.py`, if corresponding flag is set

#### What script actually does:
1. Launches main server. Launches [**telegram bot**](https://t.me/Conntrol_test_bot) if line `bot = True` is in server config file
2. Every client gets following information about its computer and system:
	- For processes related with opened windows:
		- Name
		- Create time
		- Status
		- RSS memory
		- VMS memory
		- Shared memory
		- Data memory
	- Number of processes
	- Disk memory usage
	- CPU frequency (min, max and current)
	- System boot time
	- Total memory used
	- Current window name
	- Mostly used window and its percentage
	- Second mostly used window and its percentage (if there is)
	- Third mostly used window and its percentage (if there is)
3. All this information is being send to server via Transmission Control Protocol (TCP). Server writes everything into SQL database
4. After request through commands or interactive keyboard in telegram bot all information mentioned above about particular worker is printed in telegram, then script sends a histogram graph with no more then three most used windows and their usage percentage.


***Remark:*** while running `MainServer.py` with `bot = True` config child process with telegram bot `TGBot.py` being launched (at present moment bot keeps alive only while computer which started `MainServer.py` is on). Child process sleeps until boss requested information in telegram. As soon as it happened, `TGBot.py` runs `Plot.py` subprocess and waits until graph will be built and saved, then sends picture of graph and additional information.


# Database

Work with database is built with help of sqlalchemy framework, so you have to install it to work with database:
```console
pip install sqlalchemy
```
Besides, for testing you will need Faker package (its purpose is to fill database with fake data in case you want to test your base)
```colsole
pip install faker
```

## Structure

There are files with description of used models and tables in models directory. Explicitly: `user.py` - description of user object type, `computer.py` - description of computer object type (user and computers are one to one), `applications.py` - table of applications which were executed by at least one user. `Database.py` contains description of database itself (name, database engine and source model of object which all other tables inhirited from).

Main directory contains `CreateDB.py` file which has creating table function `__create_database(load_fake_data: bool = True)__`. By default internal parameter is set to `True`, which means that after creation of table it will be filled with fake data (`load_fake_data` is responsible for it). To create empty table you have to call this function with internal parameter `False`: `create_database(False)`.

To open database you can use sqlitebrowser. Just run:
```console
sqlitebrowser worker_base.sqlite
```

In `main_db.py` file function of database creation is called in case it isn't exist yet in working directory (it is assumed that database creation and queries will be done in other part of project).

## DB_access.py

This module contains functions of database editing and querying.

Querying functions:
- `GetComputerInfo()` returns **Computer** object with relevant information of current user (3 most used windows, their usage percentage etc.)
- `GetUsers()` returns list of users in system
- `GetAuthorisationTime()` returns dictionary: user -> authorisation time
- `GetExitTime()` returns dictionary: user -> exit time
- `GetAppsList()` for given user returns list of all applications which were executed on his computer
- `GetMostUsableWindows()` for given moment of time returns two lists: most used windows and their usage percentage





<h1 align="center"> РУССКИЙ </h1>
### Понадобится установить следующее:
```console
pip install psutil
pip install python-libxdo
pip install python-telegram-bot
pip install seaborn
pip install sqlalchemy
pip install faker
pip install PyQt5
sudo apt-get install python3-gi gir1.2-wnck-3.0
```

#### Как запустить
##### На главном компьютере запускается программа `MainServer.py`. На компьютерах работников запускаются программы `Worker.py`. В качестве аргументов командной строки должны присутствовать пути к файлам конфигураций соответственно для сервера и работника. Раз в 5 секунд `Worker.py` получает нужную информацию и отправляет ее на сервер. Сервер же обрабатывает эту информацию и записывает в базу данных. Если в конфиге для сервера прописать `bot = True`, то запускается телеграм-бот, через которого босс может запросить информацию о работниках в целом и каком-то конкретном. Вдобавок, на локальном сервере можно запустить программу `QtBase.py`, для которой использовался QtCreator, поэтому файл `Base.ui` необходим. Через нее можно наблюдать всю собранную сервером информацию в виде TabWidget с таблицами.


#### Что скрипт должен делать:
1. Получить информацию о компьютере данного работника
2. Передать ее на главный сервер
3. Сервер обрабатывает данную информацию:
	- Записывает все в базу данных
	- По возможности строит графики нужных величин
	- Выводит информацию по необходмому запросу
4. При запуске `QtBase.py` выводить всю информацию о работниках
5. Отсылать всю информацию боссу в телеграм через `TGBot.py`, если установлен соответствующий флаг

#### Что скрипт делает на данный момент:
1. Запускает главный сервер. На сервере запускает [**телеграм-бота**](https://t.me/Conntrol_test_bot), если установлен флаг `bot = True` в конфиге для сервера
2. Каждый клиент получает следующую информацию о своем компьютере и системе:
	- Для процессов, связанных с открытыми окнами, получает:
		- Name
		- Create time
		- Status
		- RSS memory
		- VMS memory
		- Shared memory
		- Data memory
	- Количество процессов
	- Использование дисковой памяти
	- Частоту CPU (минимальную, максимальную и текущую)
	- Время запуска системы
	- Общее использование памяти
	- Имя текущего окна
	- Наиболее часто используемое окно и процентаж использования
	- Второе наиболее часто используемое окно и процентаж использования (если есть)
	- Третье наиболее часто используемое окно и процентаж использования (если есть)
3. Вся эта информация передается серверу через TCP протокол. Он записывает все базу данных SQL
4. В телеграм-боте по запросу с помощью команд или интерактивной клавиатуры выдается информация, оговоренная выше, о работнике с конкретным именем и присылается картинка с гистограммой не более трех наиболее используемых окон и процентаж использования.

***Замечание:*** при запуске программы `MainServer.py` с конфигом `bot = True` запускается дочерний процесс с телеграм-ботом `TGBot.py` (пока что бот жив при условии, что компьютер того, кто запустил `MainServer.py`, включен). Тот в свою очередь бесконечно спит, пока босс в телеграме не запросит информацию. Как только это произошло, `TGBot.py` запускает подпроцесс `Plot.py` и ждет, пока построится и сохранится график, после чего уже отправляет картинку и дополнительную информацию.


# База данных

Работа с базой данных построена на базе фрэймворка sqlalchemy, поэтому для работы с ним неободимо установить этот фрэймворк:
```console
pip install sqlalchemy
```
Кроме того, для теста вам понадобится пакет Faker (предназначен для заполнения базы фэйковой информацией, если вам необходимо протестировать базу):
```colsole
pip install faker
```

## Структура

В директории models лежат файлы с описанием моделей и соответсвующих таблиц, которые используются в работе. Конкретно: `user.py` - описание объекта пользователь, `computer.py` - объект компьютер (за одним компьютером работает один пользователь), `applications.py` - таблица приложений, которые запускались всеми пользователями (хотя бы раз за рабочий день). Файл `Database.py` содержит описание базы данных (имя, используемый движок (СУБД), а так же исходную модель объекта, от которого наследуются все остальные таблицы).

В основной директории сожержится файл `CreateDB.py`, который содержит функцию создания таблицы `__create_database(load_fake_data: bool = True)__`. По умолчанию параметр выставлен на `True`, это значит, что при создании базы она заполнится фэйковыми данными (за это отвечает функция `load_fake_data`). Для того чтобы создать пустую таблицу необходимо вызвать эту функцию с параметром `False`: `create_database(False)`.

Для того, чтобы открыть базу данных в sqlitebrowser для просмотра выполните в консоли команду:
```console
sqlitebrowser worker_base.sqlite
```

В файле `main_db.py` вызывается функция создания базы данных, если файла с именем базы еще нет в рабочем каталоге (предполагается, что создание базы и обращения к ней в последствии будут происходить в других частях проекта).

## DB_access.py

В этом модуле содержатся функции редактирования базы и функции запросов.

Функции запросов к базе:
- `GetComputerInfo()` возвращает объект **Computer** c актуальной информацией по текущему пользователю (3 наиболее используемые окна, процент их использования, и др.)
- `GetUsers()` возращает список пользователей в системе
- `GetAuthorisationTime()` возвращает словарь: пользователь -> время авторизации в системе
- `GetExitTime()` возвращает словарь: пользователь -> время выхода пользователя из системы
- `GetAppsList()` по заданному имени пользователя возвращает список всех приложений, которые открывались на его компьютере
- `GetMostUsableWindows()` для данного момента времени возвращает два списка: наиболее используемые заданным пользователем окна и процентаж их использования
