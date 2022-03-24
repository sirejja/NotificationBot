import requests
import logging
import os
import time
from telegram import Bot
from utils import get_bot_handler
from dotenv import load_dotenv


logger = logging.getLogger(__file__)


def check_marks(timestamp, dvmn_token, dvmn_timeout):
    params = {'timestamp': timestamp}
    headers = {'Authorization': f'Token {dvmn_token}'}
    url = 'https://dvmn.org/api/long_polling/'
    response = requests.get(
        url=url, 
        headers=headers, 
        timeout=dvmn_timeout,
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

    load_dotenv()
    TG_TOKEN = os.environ['TG_TOKEN'] 
    TG_LOGS_TOKEN = os.environ['TG_LOGS_TOKEN'] 
    TG_CHAT_ID = os.environ['TG_CHAT_ID'] 
    DVMN_TOKEN = os.environ['DVMN_TOKEN'] 
    DVMN_TIMEOUT = 100

    logging.basicConfig(level=logging.INFO)
    logger.addHandler(
        get_bot_handler(
            Bot(token=TG_LOGS_TOKEN), 
            TG_CHAT_ID
        )
    )

    logger.info('Starting notification messages bot')
    messages_bot = Bot(token=TG_TOKEN)
    timestamp = None

    while True:

        try:
            
            lessons_info, timestamp = check_marks(timestamp, DVMN_TOKEN, DVMN_TIMEOUT)
            
            if not lessons_info:
                continue
            
            for message in format_messages(lessons_info):
                messages_bot.send_message(
                    text=message, 
                    chat_id=TG_CHAT_ID
                )
            
        except requests.exceptions.HTTPError:
            logger.exception('HTTPError messages bot')
            time.sleep(60)
            continue
        except requests.exceptions.ReadTimeout:
            logger.exception('ReadTimeout. Check the API docs')
            continue
        except ConnectionError:
            logger.exception('ConnectionError messages bot')
            time.sleep(60)
            continue
        
        
if __name__ == '__main__':
    main()
