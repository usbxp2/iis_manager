import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST_NAME = 'test'
RABBITMQ_IP = '192.168.0.138'
WEB_BASE_DIR= 'C:\\web'

error_code = {
    '1001': '应用程序池创建失败',
    '1002': '站点创建失败',

    '2001': '应用程序池创建成功',
    '2002': '站点创建成功'
}