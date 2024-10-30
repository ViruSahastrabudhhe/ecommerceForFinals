from flask import *
from routes import routes_bp

app = Flask(__name__)
app.secret_key = 'secretkey'
app.register_blueprint(routes_bp)

if __name__ == '__main__':
    app.run(debug=True)