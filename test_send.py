# -*- coding: utf-8 -*-
from esb.esb_integration import send_message_via_esb

data = {
    "type": "TEST",
    "data": "Проверка ActiveMQ 5.19.0"
}

send_message_via_esb(data)