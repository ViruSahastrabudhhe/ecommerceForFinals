from flask import Flask
from .extensions import mail

app=Flask(__name__)
mail.init_app(app)
app.config['SECRET_KEY']='supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/imgs'

from .users import users as users_blueprint
app.register_blueprint(users_blueprint)
from .homepage import homepage as homepage_blueprint
app.register_blueprint(homepage_blueprint)
from .seller import seller as seller_blueprint
app.register_blueprint(seller_blueprint)

app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='api'
app.config['MAIL_PASSWORD']='cf743cf7dd69d62ea86a1ea81cdf45f1'
app.config['MAIL_USE_TLS']=True
# app.config['MAIL_DEFAULT_SENDER'] = ('Default from Mailtrap', 'default@mailtrap.club')

app.static_folder = 'static'
# app.template_folder = 'templates'