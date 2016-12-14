
import json
from Leonardo.modules import rabbit_mq
from . import plugin

def new_app_pool(name, ver, host_name):
    '''
    :param request:
    :param name: 应用程序名称
    :param ver:  .net版本
    :param host_name: 客户端主机名
    :return:  客户端返回来的数据，以此判断操作是否成功
    '''
    message = {
        'name': name,
        'ver': ver
    }
    reply_data = plugin.send_recv(host_name, message)
    return reply_data
