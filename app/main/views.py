from flask import render_template
from . import main
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    # first_or_404()如果没有找到就以404当方式中止，而不是返回none
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)
