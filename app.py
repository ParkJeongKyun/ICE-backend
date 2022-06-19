from flask import Flask
#from flask_cors import CORS
import logging
from views import api_views

logging.basicConfig(filename="log/log.log", level=logging.ERROR)

app = Flask(__name__)
app.register_blueprint(api_views.bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0')