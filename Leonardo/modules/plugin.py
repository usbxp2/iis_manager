from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from Leonardo import models
from Leonardo.modules import rabbit_mq
from Splinter.models import UserProfile
import json
from Leonardo.modules.legal_check import check_pool, check_website_name


def send_recv(host_name, message):
    get_dir_obj = rabbit_mq.leo_rabbitmq(host_name)  #实例化
    get_dir_obj.send(message)    #发送message到队列
    reply = get_dir_obj.wait_callback()   #接收客户端回复，阻塞
    reply_data = json.loads(str(get_dir_obj.get_client_data(), 'utf-8'))  #获取到客户端回复
    return reply_data