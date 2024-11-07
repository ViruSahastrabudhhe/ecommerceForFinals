from flask import Flask
from flask_mail import Mail

app=Flask(__name__)
app.config['SECRET_KEY']='supersecretkey'

app.config['MAIL_SERVER']='live.smtp.mailtrap.io'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='api'
app.config['MAIL_PASSWORD']='cf743cf7dd69d62ea86a1ea81cdf45f1'
app.config['MAIL_USE_TLS']=True
# app.config['MAIL_DEFAULT_SENDER'] = ('Default from Mailtrap', 'default@mailtrap.club')

app.static_folder = 'static'
# app.template_folder = 'templates'

mail=Mail(app)

from awesomers import routes