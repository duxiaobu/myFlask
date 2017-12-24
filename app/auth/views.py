from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetForm, \
    PasswordResetRequestForm, ChangeEmailForm
from .. import db


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """当请求类型为GET时，视图函数直接渲染模板
        当表单在POST请求中提交时，Flask-WTF中的validate_on_submit()函数会验证表单数据，然后尝试登入用户
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            # login_user函数在用户会话中把用户标记为已登录
            login_user(user, form.remember_me.data)
            # 用户访问未授权的URL时，会显示登录表单，参数在request。args中查找，若没有，则重定向到首页
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    # 删除并重设用户会话
    logout_user()
    # 显示一个flash消息，确认这次操作
    flash('You hava been logged out.')
    # 重定向到首页
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        # 提交数据库后才能赋予新用户id值，而确认令牌需要用到id，所以不能延后提交
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    """因为login_required修饰器会保护这个路由，因此，用户点击确认邮件中的链接后，要先登录，然后才能执行这个试图函数。"""
    # 已经通过验证的用户
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    # 正验证通过的用户
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    """满足下面3个条件时，before_app_request处理程序会拦截请求
        1、用户已登录
        2、用户的账户还未确认
        3、请求的端点不在认证蓝本中。
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    # is_anonymous 对普通用户必须返回False
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    """向未验证用户重新发送邮件"""
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """已登录用户修改密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 先验证旧密码是否正确
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated!')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """这是在登录条件下，重设密码看见的页面，重设密码的条件就是输入对的邮箱"""
    # 如果不是匿名用户
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_confirmation_token()
            send_email(user.email, 'Reset Your Password.',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html')


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    """点击邮箱中的链接的页面"""
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email address has been sent to you')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password')
    return render_template('auth/change_email.html', form=form)