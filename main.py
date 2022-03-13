import requests
import os
from telegram import Bot
from time import sleep


to_load_from_env = [
    'TG_TOKEN',
    'TG_CHAT_ID',
    'DVMN_TOKEN'
]
config = dict((x, os.environ[x]) for x in to_load_from_env)

TIMEOUT = 100


def check_marks(timeout: int):
    headers = {}
    params = {}
    headers['Authorization'] = f'Token {config["DVMN_TOKEN"]}'
    url = 'https://dvmn.org/api/long_polling/'
    while True:
        try:
            response = requests.get(
                url=url, 
                headers=headers, 
                timeout=timeout,
                params=params
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            continue
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            sleep(5)

        response_json = response.json()
        
        if response_json.get('status', '') != 'timeout':
            return response_json.get('new_attempts', '')
        params['timestamp'] = response_json['timestamp_to_request']    
        
def format_marks(lesson_info: dict):
    lesson_title = lesson_info['lesson_title']
    if not lesson_info.get('is_negative', ''):
        return f'Работа "{lesson_title}" проверена. \\n\\nРабота принята.'
    return f'Работа "{lesson_title}" проверена. \\n\\nК сожалению в работе нашлись ошибки.'

def main():
    bot = Bot(token=config["TG_TOKEN"])
    while True:
        marks = check_marks(TIMEOUT)
        bot.send_message(
            text=format_marks(marks), 
            chat_id=config["TG_CHAT_ID"]
        )

        
if __name__ == '__main__':
    main()
