import os
import requests
import telegram
import time
import logging
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
bot = telegram.Bot(token=TELEGRAM_TOKEN)
headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
logging.basicConfig(filename="info.log", level=logging.INFO)


def parse_homework_status(homework):
    homework_name =  homework.get('homework_name')
    if not (
        homework_name and
        homework and
        homework.get('status')
    ):
        logging.exception(f'Не получается получить информацию о {homework}')
    if homework.get('status') == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if not current_timestamp:
        current_timestamp = int(time.time())
    params = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(url, params=params, headers=headers)
        return homework_statuses.json()
    except requests.exceptions.RequestException as err_requests:
        logging.exception(err_requests, 'ошибка соеднения:(')


def send_message(message):
    try:
        return bot.send_message(chat_id=CHAT_ID, text=message)
    except requests.exceptions.RequestException as err_requests:
        logging.exception(err_requests, 'ошибка при отправке сообщения:(')


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(300)

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
