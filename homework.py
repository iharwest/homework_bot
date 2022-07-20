import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import KeyNotFound, StatusCodeNot200, StatusError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

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
)

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.CRITICAL)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - '
                              '%(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(formatter)


def send_message(bot, message):
    """Функция отправки сообщений об изменении статуса в мессенджер."""
    try:
        logger.info('Бот начинает отправку сообщения')
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        raise ConnectionError(
            f'Не удалось отправить сообщение "{message}".'
            'Сбой при отправке сообщения.'
        )
    else:
        logger.info(f'Бот отправил сообщение "{message}"')


def get_api_answer(current_timestamp):
    """Функция отправки запросов к API."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise StatusCodeNot200(response)
    except requests.RequestException as error:
        raise requests.RequestException(f'Проблемы с запросом {error}')
    return response.json()


def check_response(response):
    """Функция проверки статуса домашнего задания в ответе API."""
    if not isinstance(response, dict):
        logger.error('Тип данных ответа от API не dict.')
        raise TypeError('Тип данных ответа от API не dict.')
    try:
        homeworks = response.get('homeworks')
        if 'homeworks' not in response or 'current_date' not in response:
            raise KeyNotFound
    except KeyError:
        raise KeyNotFound
    try:
        homework = homeworks[0]
        if not isinstance(homeworks, list):
            raise KeyError(
                'В ответе от API под ключом "homeworks" пришел не список.'
                f' response = {response}.'
            )
    except IndexError:
        raise IndexError('Список работ на проверке пуст.')
    return homework


def parse_status(homework):
    """Функция для анализа статуса домашнего задания в ответе API."""
    if 'homework_name' not in homework:
        logger.error('Отсутствует ключ homework_name')
        raise KeyError(
            'Отсутствует ключ homework_name')
    if 'status' not in homework:
        logger.error('Отсутствует ключ status')
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
    return all(tokens)


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = (
            'Отсутcтвует обязательная переменная окружения. '
            'Программа принудительно завершена')
        logger.critical(message)
        sys.exit(message)
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
        except Exception as error:
            logger.error(error)
            error_message = f'Сбой в работе программы: {error}'
            if error_message != send_error:
                send_message(bot, error_message)
                send_error = error_message
        else:
            response = get_api_answer(current_timestamp)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
