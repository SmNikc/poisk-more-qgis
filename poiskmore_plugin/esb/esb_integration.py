import os
import json
import configparser
import time
import stomp
from stomp.exception import ConnectFailedException

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'default.ini')
if not os.path.exists(config_path):
    print(f"Конфигурационный файл {config_path} не найден. Используются значения по умолчанию.")
config.read(config_path)

broker_host = config.get('ESB', 'broker_host', fallback='localhost')
broker_port = config.getint('ESB', 'broker_port', fallback=61616)
use_ssl = config.getboolean('ESB', 'use_ssl', fallback=False)
queue_name = config.get('ESB', 'queue_name', fallback='/queue/sar.queue')

class ActiveMQListener(stomp.ConnectionListener):
    def on_error(self, frame):
        print(f"Ошибка ESB: {frame.body}")
    def on_message(self, frame):
        print(f"Получено сообщение: {frame.body}")

def send_message_via_esb(message_data, max_retries=2):
    try:
        hosts = [(broker_host, broker_port)]
        conn = stomp.Connection(hosts)
        conn.set_listener('', ActiveMQListener())
        if use_ssl:
            conn.set_ssl(for_hosts=hosts)
        for attempt in range(max_retries):
            try:
                conn.connect(wait=True)
                conn.send(body=json.dumps(message_data), destination=queue_name)
                time.sleep(0.1)
                conn.disconnect()
                print("Сообщение отправлено через ESB")
                return True
            except ConnectFailedException as e:
                if attempt < max_retries - 1:
                    print(f"Попытка {attempt + 1} из {max_retries} не удалась: {e}. Повтор...")
                    time.sleep(1)
                else:
                    print(f"Ошибка подключения к ESB после {max_retries} попыток: {e}")
                    return False
    except Exception as e:
        print(f"Ошибка ESB: {e}")
        return False

def send_test_message():
    test_data = {"type": "TEST", "data": "Проверка ActiveMQ на 26.07.2025"}
    return send_message_via_esb(test_data)