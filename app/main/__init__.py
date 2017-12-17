from flask import Blueprint

# 第一个参数是蓝本的名字，第二个参数是蓝本所在的包或模块
main = Blueprint('main', __name__)

# views,errors在末尾导入，因为它们中导入了main，避免了循环导入
# 程序的路由保存在views中，错误处理程序保存在errors中
from . import views, errors