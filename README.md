GORA (Guild of Robot’s Armies) - двумерный многопользовательский командный шутер с видом сверху. 
Облачные сервера, регистрация и личный кабинет на сайте, достижения и статистика, динамичные бои с большим количеством игроков, несколько карт и режимов игры.

## Контакты
### [Discord](https://discordapp.com/):
> - Быстрая ссылка: [Infit Team](https://discordapp.com/invite/C2gcnks)
> - Пригласительный код: **C2gcnks**

## Стек технологий:
> - Python 3.4
> - Pygame (клиент)
> - Django (веб часть)
> - PyMySQL
> - PyLint (оценка качества кода)
> - Doxygen (документирование исходного кода)
> - LibreOffice и MindMaple (проектная документация)

## Настройка virtualenv (Python3 + Django):
> - virtualenv -p /usr/bin/python3.4 quest_web
> - source quest_web/bin/activate
> - pip install pymysql
> - pip install django
> - python manage.py runserver

## Положения разработки
- Задание считается просроченным если к назначенному времени не был отправлен Merge Request по заданию
- После отправки Merge Request с выполненным заданием, задание перемещается в группу checking
- После принятия Merge Request - задание считается выполнненым. 
При необходимости внесения изменений - выделяется дополнительное время, но не более 1 дня

## Ревью кода
- Прежде чем отправлять Merge Request, необходимо проверить код Pylint.
- Merge Request будет принят только если код оценен на 10.
- Чтобы проверить код, необходимо запустить из корня проекта команду ```pylint quest```

**© MSHP-Yandex, Infit Team (Группа 53), 2017**