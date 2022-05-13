### This repository was created by [Pavel Filippenko](https://github.com/pavel-collab), [Mikhail Ovsiannikov](https://github.com/OAMichael) and [Andrey Barannikov](https://github.com/barannikovav).

### Понадобится установить следующее:
```console
pip install psutil
```
Это: 
```console
pip install python-libxdo
```
И, наконец, это:
```console
sudo apt-get install python3-gi gir1.2-wnck-3.0
```

#### Что скрипт должен делать:
1. Получить информацию о компьютере данного работника
2. Передать ее на главный сервер
3. Сервер обрабатывает данную информацию:
	- Записывает все в базу данных
	- По возможности строит графики нужных величин
	- Выводит информацию по необходмому запросу
4. ~~Отсылать всю инфу боссу в телегу~~

#### Что скрипт делает на данный момент:
1. Получает следующую информацию о компьютере и системе данного пользователя:
	- Для каждого процесса получает:
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
	- Температуру каждого ядра (текущую, максимальную и критическую)
	- Названия всех открытых окон
	- ID текущего окна
	- Имя текущего окна
	- Наиболее часто используемое окно и процентаж использования
	- Второе наиболее часто используемое окно и процентаж использования (если есть)
	- Третье наиболее часто используемое окно и процентаж использования (если есть)
	- Положение курсора в пикселях экрана (отсчет от левого верхнего края экрана)
	- ID окна над которым расположен курсор
	- Имя окна над которым расположен курсор
2. Записывает всю информации о процессах в базу данных (пока что прямиком с клиента)


#### Пример вывода (информация всего для одного процесса):
```console
('Proj_get.py', '2022-05-13 22:06:09.790000', 'running', 47464448, 260476928, 27516928, 36528128)
Number of processes:           300
######################### Integral info ##############################
Disk memory usage:             66.9%
CPU frequency(min):            1400.0 MHz
CPU frequency(max):            2100.0 MHz
CPU frequency(current):        1405.6365 MHz
Boot time:                     2022-05-13 19:05:11
Total memory used:             52.6%
Core 0 tempereture:            current=71.000000°C, high=71.000000°C, critical=71.000000°C
Core 1 tempereture:            current=71.000000°C, high=71.000000°C, critical=71.000000°C
Core 2 tempereture:            current=71.000000°C, high=71.000000°C, critical=71.000000°C
Core 3 tempereture:            current=47.000000°C, high=47.000000°C, critical=47.000000°C
######################### Opened windows #############################
Desktop
~/Desktop/MIPT/4th-Sem-Proj/UsersControle/Readme.md - Sublime Text (UNREGISTERED)
michael@michael-Aspire-A515-43: ~/Desktop/MIPT/4th-Sem-Proj/UsersControle
4th-Sem-Proj
pavel-collab/UsersControle at develop - Brave
######################### Current window #############################
Current window id:             90177539
Current window name:           Мессенджер - Brave
Maximum used window:           michael@michael-Aspire-A515-43: ~/Desktop/MIPT/4th-Sem-Proj/UsersControle 33.33%
Second maximum used window:    4th-Sem-Proj 33.33%
Third maximum used window:     Мессенджер - Brave 33.33%
Current mouse location:        (242, 693)
Window at mouse id:            90177539
Window at mouse name:          Мессенджер - Brave
```
