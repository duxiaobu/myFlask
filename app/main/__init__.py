from flask import Blueprint

# 第一个参数是蓝本的名字，第二个参数是蓝本所在的包或模块
main = Blueprint('main', __name__)

# views,errors在末尾导入，因为它们中导入了main，避免了循环导入
# 程序的路由保存在views中，错误处理程序保存在errors中
from . import views, errors
from ..models import Permission


# 为了避免每次调用render_template()时都多添加一个模板参数，可以使用上下文处理器。
# 上下文处理器能让变量在所有模板中全局可访问
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)