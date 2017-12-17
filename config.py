import os
from info import config_info

# 主文件夹的路径
basedir = os.path.abspath(os.path.dirname(__name__))


class Config:
    """通用配置，根据需要还可添加其他配置类"""
    # FlaskForm表单为了防止CSRF攻击而设置的密钥
    SECRET_KEY = config_info.get('SECRET_KEY') or 'hard to guess string'
    # 每次请求结束后都会自动提交数据库中的变动
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 邮件的主题前缀
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = '杜雄<15884538142@163.com>'
    # 邮件接收者
    FLASKY_ADMIN = config_info.get('FLASKY_ADMIN')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 587
    # 国内邮件使用SSL协议
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = config_info.get('MAIL_USERNAME')
    MAIL_PASSWORD = config_info.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = config_info.get('DEV_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'date-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = config_info.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = config_info.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}