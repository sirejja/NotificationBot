import requests
import os
from telegram import Bot


TG_TOKEN = os.environ['TG_TOKEN']
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
    bot = Bot(token=TG_TOKEN)
    timestamp = None
    while True:
        
        try:
            lessons_info, timestamp = check_marks(timestamp)
        except requests.exceptions.HTTPError:
            print('HTTPError')
            continue
        except requests.exceptions.ReadTimeout:
            print('ReadTimeout')
            continue
        except ConnectionError:
            print('ConnectionError')
            continue
            
        if not lessons_info:
            continue
            
        for message in format_messages(lessons_info):
            bot.send_message(
                text=message, 
                chat_id=TG_CHAT_ID
            )

        
if __name__ == '__main__':
    main()
