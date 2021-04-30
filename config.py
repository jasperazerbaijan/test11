TOKEN = '1744731804:AAFqSo11XWfoytzUupsm6yCUn5iwWtYMGb8'  # Learn how to get one on https://core.telegram.org/bots#6-botfather
ADMIN_ID = 940086446
SKIP_PENDING = False  # Skip pending updates on bot startup
PLAYERS_COUNT_TO_START = 4  # Minimal quantity of players that is required to start mafia game
PLAYERS_COUNT_LIMIT = 10  # Maximum quantity of players that is allowed to start mafia game
REQUEST_OVERDUE_TIME = 10 * 60  # Time (in seconds) of request's inactivity after which it gets deleted from database
WORD_BASE = '/root/test11/src/words.txt'  # File encoded with cp1251 containing word on each line
DELETE_FROM_EVERYONE = False  # Should bot delete messages from everyone in the chat and not just players?

SET_WEBHOOK = False  # Uses long polling if set to False
if SET_WEBHOOK:  # Refer to https://core.telegram.org/bots/webhooks to learn how to setup webhook components
    SERVER_IP = '91.238.104.150'
    SERVER_PORT = 22
    SSL_CERT = '/root/cert/PUBLIC.pem'  # File path of public SSL certificate
    SSL_PRIV = '/root/cert/PRIVATE.key'  # File path of private key of SSL certificate

import logging
LOGGER_LEVEL = logging.INFO
