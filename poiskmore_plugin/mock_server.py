# mock_server.py (отладочный сервер для тестирования API, например, погоды)
# Комментарий: Тестовый HTTP-сервер на Flask для имитации API внешних сервисов (например, получения погодных данных). 
#Запускается на порту 5000.
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/weather', methods=['GET'])
def get_weather():
    return jsonify({"temperature": 25, "wind_speed": 5})

if __name__ == '__main__':
    app.run(port=5000, debug=True)