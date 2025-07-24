import apache.nms as nms
import apache.nms.activemq as amq
import configparser
import json

config = configparser.ConfigParser()
config.read('config/default.ini')
broker_uri = config.get('ESB', 'broker_uri', fallback='tcp://localhost:61616')
queue_name = config.get('ESB', 'queue_name', fallback='sar.queue')

def send_message_via_esb(message_data):
    try:
        connection_factory = amq.ConnectionFactory(broker_uri)
        connection = connection_factory.CreateConnection()
        session = connection.CreateSession()
        destination = session.GetQueue(queue_name)
        producer = session.CreateProducer(destination)
        message = session.CreateTextMessage(json.dumps(message_data))
        producer.Send(message)
        session.Close()
        connection.Close()
        return True
    except Exception as e:
        print(f"Ошибка ESB: {e}")
        return False
