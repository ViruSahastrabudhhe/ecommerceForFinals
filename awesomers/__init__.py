from flask import Flask
from .extensions import mail

app=Flask(__name__)
app.config['SECRET_KEY']='supersecretkey'
app.config['UPLOADED_FILES_DEST'] = '/awesomers/static/imgs'
app.config['UPLOAD_FOLDER'] = '/awesomers/static/imgs'

from .users import users as users_blueprint
app.register_blueprint(users_blueprint)
from .homepage import homepage as homepage_blueprint
app.register_blueprint(homepage_blueprint)
from .seller import seller as seller_blueprint
app.register_blueprint(seller_blueprint)
from .profiles import profiles as profiles_blueprint
app.register_blueprint(profiles_blueprint)
from .products import products as products_blueprint
app.register_blueprint(products_blueprint)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='awesomersecommerce@gmail.com'
app.config['MAIL_PASSWORD']='veop zyzn bpwp ymbk '
app.config['MAIL_USE_TLS']=True
app.config["MAIL_USE_SSL"]=False
# app.config['MAIL_DEFAULT_SENDER'] = ('Default from Mailtrap', 'default@mailtrap.club')

mail.init_app(app)

app.static_folder = 'static'
# app.template_folder = 'templates'