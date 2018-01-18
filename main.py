#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'W.Y.P'
__version__ = "1.0.1"
__email__ = "wyp@41ms.com"
__date__ = '2018/1/18'


import os
import os.path as op
import xlrd
import re
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from config import DevConfig
from flask_babelex import Babel


from wtforms import validators

from flask_admin.contrib import sqla

# 创建应用
app = Flask(__name__)

# 多语言支持
babel = Babel(app)

# 加载配置
app.config.from_object(DevConfig)

db = SQLAlchemy(app)


class Department(db.Model):

    """部门模型"""

    id = db.Column(db.Integer, primary_key=True)
    # 部门名称
    name = db.Column(db.Unicode(64), unique=True)

    def __str__(self):
        return self.name


class Equipment(db.Model):

    """设备模型"""

    id = db.Column(db.Integer, primary_key=True)
    # 设备名称
    name = db.Column(db.Unicode(500))
    # 设备型号
    model = db.Column(db.Unicode(500))
    # 设备编码
    code = db.Column(db.Unicode(500))
    # 设备状态
    status = db.Column(db.Integer)
    # 购买日期
    date = db.Column(db.Date)
    # 备注
    remark = db.Column(db.Text, nullable=True)

    # 外键 部门ID
    department_id = db.Column(db.Integer(), db.ForeignKey(Department.id))
    department = db.relationship(Department, backref='equipments')

    def __str__(self):
        return self.name + ' | ' + self.model + ' | ' + self.code


# 视图

@app.route('/')
def index():

    """默认首页"""

    return '<a href="/admin/">Click me to get to Admin!</a>'


class DepartmentAdmin(sqla.ModelView):

    """部门管理相关视图"""

    # 可以导出
    can_export = True

    # 导出格式为excel
    export_types = ['xlsx']

    column_sortable_list = ('name', )
    column_labels = dict(name='部门名称', equipments='设备')
    column_searchable_list = ('name', )

    # 可用于行内编辑
    column_editable_list = ['name', ]


def format_status(status):

    """格式化状态码的显示"""

    status = str(status)

    status_list = {'0':'新增', '1':'使用中', '2':'维修中', '3':'报废'}

    return status_list[status]


class EquipmentAdmin(sqla.ModelView):

    """设备管理相关视图"""

    # 可以导出
    can_export = True

    # 导出格式为excel
    export_types = ['xlsx']


    # 配置可排序字段
    column_sortable_list = ('name', ('department', 'department.name'), 'date')

    # 可用于行内编辑
    column_editable_list = ['name', 'status']

    # 配置下拉项字段候选集
    form_choices = {
        'status': [
            ('0', '新增'),
            ('1', '使用中'),
            ('2', '维修中'),
            ('3', '报废')
        ]
    }

    # 字段值格式化
    column_formatters = dict(status=lambda v, c, m, p: format_status(m.status))

    # 配置各字段显示名称
    column_labels = dict(
        name='设备名称',
        model='设备型号',
        code='设备编码',
        date='购买日期',
        status='状态',
        remark='备注',
        department='部门名称'
    )


    # 配置可搜索字段
    column_searchable_list = ('name', Department.name, 'model', 'code', 'date')

    # 配置字段必填
    form_args = dict(
        name=dict(label='设备名称', validators=[validators.required()]),
        model=dict(label='设备型号', validators=[validators.required()]),
        code=dict(label='设备编码', validators=[validators.required()]),
        status=dict(label='设备状态', validators=[validators.required()])
    )


# 创建管理系统
admin = Admin(app, name='设备管理系统', template_mode='bootstrap3')

# 加载视图
admin.add_view(DepartmentAdmin(Department, db.session, name='部门管理'))
admin.add_view(EquipmentAdmin(Equipment, db.session, name='设备管理'))



def build_db():

    """ 生成测试数据 """

    db.drop_all()
    db.create_all()

    # 通过 excel 导入测试数据
    data = xlrd.open_workbook('demo.xlsx')

    table = data.sheets()[0]

    nrows = table.nrows

    for i in range(nrows):

        # 从第二行开始
        if i == 0:
            continue

        datetime = None

        try:
            datetime = xlrd.xldate.xldate_as_datetime(table.cell(i, 6).value, 0)
        except (ValueError, TypeError):
            pass

        # 首先增加部门数据
        department_name = str(table.cell(i, 1).value)
        department_name = re.sub('\s', '', department_name)

        department = Department.query.filter_by(name=department_name).first()

        # 新增部门
        if not department:
            department = Department()
            department.name = department_name
            db.session.add(department)

        # 增加设备数据
        equipment = Equipment()
        equipment.name = str(table.cell(i, 2).value)
        equipment.model = str(table.cell(i, 3).value)
        equipment.code = str(table.cell(i, 4).value)
        equipment.status = 1
        equipment.date = datetime
        equipment.department = department
        db.session.add(equipment)

    db.session.commit()

    return

if __name__ == '__main__':
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])

    if not os.path.exists(database_path):
        build_db()

    app.run(debug=True)
