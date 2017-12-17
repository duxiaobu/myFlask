from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serilizer
from flask_login import UserMixin
from flask import current_app
from . import db, login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """密码为只写属性，因为生成的散列值后就无法还原原来的密码了"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """生成令牌，参数未存活时间，单位为秒"""
        s = Serilizer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def generate_reset_token(self, expiration=3600):
        s = Serilizer(current_app['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    def confirm(self, token):
        """在邮箱中点击链接时，会调用函数进行验证，通过的话会将confirmed字段设置为True"""
        s = Serilizer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    @staticmethod
    def reset_password(token, new_password):
        s = Serilizer(current_app['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def __repr__(self):
        return '<User %r>' % self.username    # %r是repr()方法处理的对象


@login_manager.user_loader
def load_user(user_id):
    """加载用户的回调函数接收以Unicode字符串形式表示的用户标识符，若能找到用户，则返回用户对象"""
    return User.query.get(int(user_id))