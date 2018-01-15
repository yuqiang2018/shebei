#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = 'wyp@41ms.com'
__date__ = '2018/1/15'
__time__ = '上午9:15'

class Config(object):
    """Base config class."""
    pass

class ProdConfig(Config):
    """Production config class."""
    pass

class DevConfig(Config):
    """Development config class."""
    # Open the DEBUG
    DEBUG = True
    BABEL_DEFAULT_LOCALE = 'zh_CN'
    SECRET_KEY = '1234567890'
    DATABASE_FILE = 'db.sqlite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True





