from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

login_manager = LoginManager()
# session_protection属性可以设为None、'basic'、'strong'，提供不同的安全等级防止用户会话遭修改
login_manager.session_protection = 'strong'
# 未登录时，访问需要登录的页面，会跳转过去的登录页面。这个值是登录页面视图函数的endpoint
login_manager.login_view = 'auth.login'

# 前端框架
bootstrap = Bootstrap()
# 电子邮件插件
mail = Mail()
# 本地时间化插件
moment = Moment()
# ORM插件
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    # 当传入用config字典提取的值之后，系统就会应用类属性里面的配置了。
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    # url_prefix为url前缀，注册后蓝本中定义的所有路由都会加上指定的前缀。
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app