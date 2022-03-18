import requests
import os

from telegram import Bot
import utils

    
TG_TOKEN = os.environ['TG_TOKEN']
TG_LOGS_TOKEN = os.environ['TG_LOGS_TOKEN']
TG_CHAT_ID = os.environ['TG_CHAT_ID']
DVMN_TOKEN = os.environ['DVMN_TOKEN']

DVMN_TIMEOUT = 100


def check_marks(timestamp):
    params = {'timestamp': timestamp}
    headers = {'Authorization': f'Token {DVMN_TOKEN}'}
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(
        url=url, 
        headers=headers, 
        timeout=DVMN_TIMEOUT,
        params=params
    )
    response.raise_for_status()
    dvmn_data = response.json()
    timestamp = dvmn_data.get('last_attempt_timestamp') or\
                dvmn_data.get('timestamp_to_request')
    
    lessons_info = dvmn_data.get('new_attempts')
    return lessons_info, timestamp

    
def format_messages(lessons_info):
    messages = []
    for lesson in lessons_info:
        if not lesson.get('is_negative'):
            messages.append(
                f'''
                Работа \"{lesson["lesson_title"]}\" проверена.
                \n{lesson["lesson_url"]}
                \nРабота принята.
                '''
            )
            continue
        messages.append(
            f'''
            Работа \"{lesson["lesson_title"]}\" проверена.
            \n{lesson["lesson_url"]}
            \nК сожалению в работе нашлись ошибки.
            '''
        )
    return messages


def main():
    log_bot = Bot(token=TG_LOGS_TOKEN)
    logger = utils.get_logger(__name__, log_bot, TG_CHAT_ID)

    logger.info('Starting notification messages bot')
    messages_bot = Bot(token=TG_TOKEN)
    timestamp = None

    while True:

        try:
            lessons_info, timestamp = check_marks(timestamp)
            
            if not lessons_info:
            continue
            
        for message in format_messages(lessons_info):
            messages_bot.send_message(
                text=message, 
                chat_id=TG_CHAT_ID
            )
            
        except requests.exceptions.HTTPError:
            logger.error('HTTPError messages bot')
            continue
        except requests.exceptions.ReadTimeout:
            logger.error('ReadTimeout messages bot')
            continue
        except ConnectionError:
            logger.error('ConnectionError messages bot')
            continue
        
        
if __name__ == '__main__':
    main()
