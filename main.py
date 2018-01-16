import os
import os.path as op
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from config import DevConfig
from flask_babelex import Babel

from flask_admin.model import typefmt

from wtforms import validators

from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters

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
    name = db.Column(db.Unicode(64))

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
    date = db.Column(db.DateTime)
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

    column_sortable_list = ('name', )
    column_labels = dict(name='部门名称', equipments='设备')
    column_searchable_list = ('name', )

    # 可用于行内编辑
    column_editable_list = ['name', ]

    # def __init__(self, session):
    #     # Just call parent class with predefined model.
    #     super(DepartmentAdmin, self).__init__(Department, session)


def format_status(status):

    """格式化状态码的显示"""

    status = str(status)

    status_list = {'0':'新增', '1':'使用中', '2':'维修中', '3':'报废'}

    return status_list[status]


class EquipmentAdmin(sqla.ModelView):

    """设备管理相关视图"""


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
        date=dict(label='购买日期', validators=[validators.required()]),
        status=dict(label='设备状态', validators=[validators.required()])
    )

    # form_ajax_refs = {
    #     'department': {
    #         'fields': (Department.name, )
    #     },
    # }


    # def __init__(self, session):
    #     # Just call parent class with predefined model.
    #     super(EquipmentAdmin, self).__init__(Equipment, session)


# 创建管理系统
admin = Admin(app, name='设备管理系统', template_mode='bootstrap3')

# 加载社稷
admin.add_view(DepartmentAdmin(Department, db.session, name='部门管理'))
admin.add_view(EquipmentAdmin(Equipment, db.session, name='设备管理'))



def build_db():

    """ 生成测试数据 """

    import random
    import datetime
    from random import choice

    db.drop_all()
    db.create_all()

    equipment_names = [
        '打印机', '饮水机', '打火机', '灯泡', '水杯', '手机', '充电器', '电池', '电话', '电脑', '显示器', '键盘',
        '鼠标', '水壶', '桌子', '椅子', '风扇', '插座', '插头', '手表', '现金', '银行卡', '饮料', '白酒', '菜叶',
        '胸卡', '一卡通', '门禁卡', '耳机'
    ]

    department_names = [
        '人力资源部', '党委办', '客户经理部', '计划财务部', '监察室'
    ]

    department_list = []
    for i in range(len(department_names)):
        department = Department()
        department.name = department_names[i]
        department_list.append(department)
        db.session.add(department)


    for i in range(len(equipment_names)):
        equipment = Equipment()
        equipment.name = equipment_names[i]
        equipment.model = 'DN' + str(random.randint(0, 9))
        equipment.code = 'SN' + str(random.randint(100, 999))
        equipment.status = 0
        equipment.date = datetime.datetime.now()
        equipment.department = choice(department_list)
        db.session.add(equipment)


    db.session.commit()

    return


if __name__ == '__main__':
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])

    if not os.path.exists(database_path):
        build_db()

    app.run(debug=True)
