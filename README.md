**GORA** *(Guild of Robots' Armies)* - двумерный многопользовательский командный шутер с видом сверху.
Облачные сервера, регистрация и личный кабинет на сайте, достижения и статистика, динамичные бои с большим количеством игроков, несколько карт и режимов игры.

### Контакты
#### [Discord](https://discordapp.com/):
> - Быстрая ссылка: [Infit Team](https://discordapp.com/invite/C2gcnks)
> - Пригласительный код: **C2gcnks**

### Стек технологий:
> - Python 3.4
> - Pygame (клиент)
> - Django (веб часть)
> - PyMySQL
> - PyLint (оценка качества кода)
> - Doxygen (документирование исходного кода)
> - LibreOffice и MindMaple (проектная документация)

### Запуск проекта

#### Настройка окружения (Yandex)
> - sudo add-apt-repository ppa:jonathonf/python-3.6
> - sudo apt-get update
> - sudo apt-get install python3.6

#### Настройка окружения (Yandex)
> - virtualenv -p python3.6 venv_python3.6
> - source venv_python3/bin/activate

#### Установка pygame и pylint:
> - pip install pygame
> - pip install pylint

#### Установка и запуск Django:
> - pip install pymysql
> - pip install django
> - python manage.py runserver

#### PyCharm:
> - Settings... -> Project Interpreter: выбрать venv_python3

### Положения разработки
- Задание считается просроченным если к назначенному времени не был отправлен Merge Request по заданию
- После отправки Merge Request с выполненным заданием, задание перемещается в группу checking
- После принятия Merge Request - задание считается выполнненым. 
При необходимости внесения изменений - выделяется дополнительное время, но не более 1 дня

### Ревью кода
- Прежде чем отправлять Merge Request, необходимо проверить код Pylint.
- Merge Request будет принят только если код оценен на 10.
- Чтобы проверить код, необходимо запустить из корня проекта команду ```pylint quest```

#### Полезные ссылки:
> - [Сравнение python2 и python3](https://pythonworld.ru/osnovy/python2-vs-python3-razlichiya-sintaksisa.html)

**© MSHP-Yandex, Infit Team (Группа 53), 2017**