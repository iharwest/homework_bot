# BOT-ASSISTENT - Telegram-бот
## Описание проекта
Telegram-бот обращается к API сервиса Практикум.Домашка.

### Функционал бота:
- Раз в 10 минут опрашивает API сервис и проверяет статус отправленной на ревью домашней работы
- При обновлении статуса анализирует ответ API и отправляет пользователю соответствующее уведомление в Telegram
- Применяет логирование, обрабатывает исключения при доступе к внешним сетевым ресурсам и сообщает пользователю о важных проблемах сообщением в Telegram.

Конфиденциальные данные хранятся в пространстве переменных окружения.

## Системные требования
- Python 3.7+
- Works on Linux, Windows, macOS

## Используемые технологии:
- Python 3.7+
- Pytest
- Telegram Bot API
- Requests

## Запуск проекта:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:iharwest/homework_bot.git
cd telegram_bot
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
В Windows:
```
source venv/Scripts/activate
```
В macOS или Linux:
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Создать файл виртуального окружения .env в корневой директории проекта:
```
touch .env
```
В нём указать свои ключи для окен API сервиса Практикум.Домашка и Telegram:
```
- PRAKTIKUM_TOKEN =
- TELEGRAM_TOKEN =
- TELEGRAM_CHAT_ID =
```
Запустить проект на локальной машине:
```
python homework.py
```

Автор: Alexey Nikolaev 
