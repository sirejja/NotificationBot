from ast import Return
import os

def get_config():
    config = {}
    env_names = ['TG_TOKEN', 'TG_LOGS_TOKEN', 'TG_CHAT_ID', 'DVMN_TOKEN']
    try: 
        return {
            env_name: os.environ[env_name] 
            for env_name in env_names
        }
    except KeyError:
        from dotenv import load_dotenv
        load_dotenv('.env')
        return {
            env_name: os.environ[env_name] 
            for env_name in env_names
        }