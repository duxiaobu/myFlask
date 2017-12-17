import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):
        # 在测试前运行,创建一个测试环境，类似于运行中的程序。
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        # 激活上下文，确保像普通请求一样
        self.app_context.push()
        # 创建备用数据库，在tearDown函数中删除
        db.create_all()

    def tearDown(self):
        # 在测试后运行
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        # 测试程序实例存在
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        # 测试确保程序在测试配置中运行
        self.assertTrue(current_app.config['TESTING'])