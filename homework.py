from dotenv import load_dotenv
import logging
import os
import requests
import time
import sys
import telegram

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
ENV = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout)


class StatusCodeNot200(Exception):
    """Перехват исключения - эндпоинт не доступен."""

    def __init__(self, response):
        """Инициализатор."""
        self.response = response

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logging.error(f'Эндпойнт "{self.response.url} недоступен.'
                      f'Код ответа API: {self.response.status_code}')


class KeyNotFound(Exception):
    """Исключение, вызываемое при отсутствии ожидаемых ключей в ответе API."""

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logging.error('Ожидаемый ключ отсутствуют в ответе API')


class StatusError(Exception):
    """Исключение, вызываемое при недокументированном статусе работы."""

    def __init__(self, status):
        """Инициализатор."""
        self.status = status

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logging.error(
            f'Недокументированный статус домашней работы: {self.status}')


def send_message(bot, message):
    """Функция отправки сообщений об изменении статуса в мессенджер."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info(f'Бот отправил сообщение "{message}"')
    except Exception:
        logging.error(
            f'Не удалось отправить сообщение "{message}".'
            'Сбой при отправке сообщения.'
        )


def get_api_answer(current_timestamp):
    """Функция отправки запросов к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise StatusCodeNot200(response)
    except requests.RequestException as error:
        logging.error(f'Проблемы с запросом {error}')
    except ValueError as error:
        logging.error(f'Недопустимое значение {error}')
    return response.json()


def check_response(response):
    """Функция проверки статуса домашнего задания в ответе API."""
    try:
        homeworks = response['homeworks']
    except KeyError:
        raise KeyNotFound
    try:
        homework = homeworks[0]
    except IndexError:
        raise IndexError('Список работ на проверке пуст.')
    return homework


def parse_status(homework):
    """Функция для анализа статуса домашнего задания в ответе API."""
    if 'homework_name' not in homework:
        logging.error('Отсутствует ключ homework_name')
        raise KeyError(
            'Отсутствует ключ homework_name')
    if 'status' not in homework:
        logging.error('Отсутствует ключ status')
        raise KeyError(
            'Отсутствует ключ status')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES.keys():
        raise StatusError
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверки наличия токенов."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if all(tokens):
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_status = ''
    send_error = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            message = parse_status(homework)
            current_timestamp = response.get('current_date')
            if message != last_status:
                send_message(bot, message)
            time.sleep(RETRY_TIME)
        except Exception as error:
            error_message = f'Сбой в работе программы: {error}'
            logging.error(error_message)
            if error_message != send_error:
                send_message(bot, error_message)
                send_error = error_message
            time.sleep(RETRY_TIME)
        else:
            response = get_api_answer(current_timestamp)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
