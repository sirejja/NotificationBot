# Notification bot for devman marks
### Фунционал:
* Программа опрашивает API сайта dvmn.org в режиме long-polling
* В случае ответа сервера с полезной информацией формируется сообщение для отправки пользователю через Телеграм бота.
  
### Env vars:
* TG_TOKEN - токен телеграмм бота
* TG_CHAT_ID - id чата человека, получающего уведомления
* DVMN_TOKEN - токен для работы с API Devman. [DVMN's API](https://dvmn.org/api/docs/)
  
### Globals:
* DVMN_TIMEOUT - по умолчанию равен 100с, на момент написания бота long-polling API Devman рассчитан на 90с.
