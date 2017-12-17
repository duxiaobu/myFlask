"""与用户认证系统相关的路由由auth蓝本定义"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views