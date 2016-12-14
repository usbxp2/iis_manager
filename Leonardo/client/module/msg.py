import pika, threading, json, os, time, subprocess
from config import settings
from module import rabbit_reply, plugin

class TaskHandle(object):
    def __init__(self, task_body):
        #self.main_obj = main_obj  #传进来的实例
        self.task_body = task_body
        self.par_message()

    def par_message(self):
        print('before:', self.task_body)
        self.task_body = json.loads(str(self.task_body, 'utf-8'))
        print('after:', self.task_body)
        print('keys:---->', self.task_body.keys())
        print('data_keys:----->', self.task_body['data'].keys())
        self.callback_queue = self.task_body['callback_queue']
        self.cmd = self.task_body['data']['cmd']
        self.svr_name = self.task_body['data']['svr_name']
        self.host_name = self.task_body['data']['host_name']

    def send_message(self, message):
        obj = rabbit_reply.MsgReply(self.callback_queue)
        obj.send(message)

    def get_dir(self):
        home_dir = os.path.join(settings.WEB_BASE_DIR, self.svr_name)
        print('家目录：', home_dir)
        try:
            dir_list = [x for x in os.listdir(home_dir) if os.path.isdir(os.path.join(home_dir, x))]
        except:
            dir_list = ['服务器上没有你的家目录(%s)，请联系系统管理员' % home_dir]
        print('家目录下的文件夹：', dir_list)
        obj = rabbit_reply.MsgReply(self.callback_queue)
        obj.send(dir_list)

    def add_app_pool(self):
        pool_name = self.task_body['data'].get('pool_name')
        pool_ver = self.task_body['data'].get('pool_ver')
        add_pool_status = plugin.new_app_pool(pool_name, pool_ver)
        message = '1001'
        if add_pool_status:
            message = '2001'
        self.send_message(message)

    def add_website(self):
        home_dir = os.path.join(settings.WEB_BASE_DIR, self.svr_name)
        web_root = os.path.join(home_dir, self.task_body['data'].get('web_path'))
        website_name = self.task_body['data'].get('website_name')
        bind_domain = self.task_body['data'].get('bind_domain')
        pool_name = self.task_body['data'].get('pool_name')
        pool_ver = self.task_body['data'].get('pool_ver')
        port = self.task_body['data'].get('port')
        callback_queue = self.task_body['callback_queue']
        print('pool_ver:', pool_ver)
        app_pool_flag = 0

        if pool_ver:
            print('----------->: 创建应用程序池')
            add_pool_status = plugin.new_app_pool(pool_name, pool_ver)

            #应用程序池没有创建成功
            if add_pool_status is False:
                app_pool_flag = 1
                obj = rabbit_reply.MsgReply(callback_queue)
                obj.send('1001')
            else:
                print('------->：应用程序池创建成功')

        #应用程序池创建完成之后创建站点
        if app_pool_flag == 0:
            print('------------->: 创建站点')
            create_website_status = plugin.new_website(website_name, port, bind_domain, web_root, pool_name)
            obj = rabbit_reply.MsgReply(callback_queue)
            message = '2002' if create_website_status else '1002'
            obj.send(message)



    def processing(self):
        print(self.task_body)
        #分析服务端发过来的指令，并执行相应操作
        if self.host_name == settings.HOST_NAME:
            if hasattr(self, self.cmd):
                cmd = getattr(self, self.cmd)
                cmd()
        else:
            print('没有这台主机')

class msghandle(object):
    def __init__(self):
        self.queue_name = settings.HOST_NAME
        self.make_connect()
        self.msg_consume()

    def make_connect(self):
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_IP))
        self.channel = self.conn.channel()

    def msg_callback(self, ch, method, properties, body):
        thread = threading.Thread(target=self.start_thread, args=(body,))
        thread.start()

    def start_thread(self, task_body):
        task = TaskHandle(task_body)
        task.processing()


    def msg_consume(self):
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_consume(self.msg_callback, queue=self.queue_name, no_ack=True)
        print('begin recives......')
        self.channel.start_consuming()