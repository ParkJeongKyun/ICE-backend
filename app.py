from flask import Flask
from flask_cors import CORS
import logging
from views import api_views
import os

# 로깅
logging.basicConfig(filename="log/log.log", level=logging.ERROR)

# Flask 앱
app = Flask(__name__)

# 비밀키 적용
app.secret_key = os.urandom(24)

# CORS를 위한 허용
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# 블루프린터 적용
app.register_blueprint(api_views.bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0')