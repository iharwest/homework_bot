import logging
import sys

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR,
)

logger = logging.getLogger(__name__)

logger.setLevel(logging.ERROR)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - '
                              '%(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(formatter)


class StatusCodeNot200(Exception):
    """Перехват исключения - эндпоинт не доступен."""

    def __init__(self, response):
        """Инициализатор."""
        self.response = response

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logger.error(f'Эндпойнт "{self.response.url} недоступен.'
                     f'Код ответа API: {self.response.status_code}')


class KeyNotFound(Exception):
    """Исключение, вызываемое при отсутствии ожидаемых ключей в ответе API."""

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logger.error('Ожидаемый ключ отсутствуют в ответе API')


class StatusError(Exception):
    """Исключение, вызываемое при недокументированном статусе работы."""

    def __init__(self, status):
        """Инициализатор."""
        self.status = status

    def __str__(self):
        """Вывод сообщения об ошибке."""
        logger.error(
            f'Недокументированный статус домашней работы: {self.status}')
