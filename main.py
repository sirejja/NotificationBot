import requests
import traceback
from telegram import Bot
from utils import get_logger
from settings import get_config

config = get_config()
DVMN_TIMEOUT = 100


def check_marks(timestamp):
    params = {'timestamp': timestamp}
    headers = {'Authorization': f'Token {config["DVMN_TOKEN"]}'}
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
    log_bot = Bot(token=config['TG_LOGS_TOKEN'])
    logger = get_logger(__name__, log_bot, config['TG_CHAT_ID'])

    logger.info('Starting notification messages bot')
    messages_bot = Bot(token=config['TG_TOKEN'])
    timestamp = None

    while True:

        try:

            lessons_info, timestamp = check_marks(timestamp)
            
            if not lessons_info:
                continue
            
            for message in format_messages(lessons_info):
                messages_bot.send_message(
                    text=message, 
                    chat_id=config['TG_CHAT_ID']
                )
            
        except requests.exceptions.HTTPError:
            logger.error('HTTPError messages bot')
            logger.error(traceback.format_exc())
            continue
        except requests.exceptions.ReadTimeout:
            logger.error('ReadTimeout messages bot')
            logger.error(traceback.format_exc())
            continue
        except ConnectionError:
            logger.error('ConnectionError messages bot')
            logger.error(traceback.format_exc())
            continue
        
        
if __name__ == '__main__':
    main()
