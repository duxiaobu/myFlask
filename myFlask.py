from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from info import config_info
from threading import Thread


# myFlask的绝对路径
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# FlaskForm为了避免CSRF攻击，必须设置密钥
app.config['SECRET_KEY'] = 'hard to guress string'
# sqlite数据库路径
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 邮箱服务器地址
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_tls'] = False
app.config['MAIL_USE_SSL'] = True
# 邮箱的账号和密码不能直接写入脚本中，如要中脚本环境中导入敏感信息
app.config['MAIL_USERNAME'] = config_info.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = config_info.get('MAIL_PASSWORD')
# 设置邮件前缀和发送者
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '杜雄<15884538142@163.com>'
# 从脚本环境中取得邮件接收者
app.config['FLASKY_ADMIN'] = config_info.get('FLASKY_ADMIN')
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app)
mail = Mail(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # users属性将返回与角色相关联的用户组成的列表
    # 参数lazy=dynamic，禁止自动执行查询
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    # 外键
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


@app.shell_context_processor
def make_shell_context():
    """让Flsk-Script的shell命令自动导入特定的对象"""
    return dict(app=app, db=db, Role=Role, User=User)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # 查询名字是否存在
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index1.html', form=form, name=session.get('name'), known=session.get('known', False))


@app.route('/user/<name>')
def get_id(name):
    return render_template('user.html', name=name)

# if __name__ == '__main__':
#     app.run(debug=True)
