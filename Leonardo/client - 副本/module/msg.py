import pika, threading, json, os, time, subprocess
from config import settings
from module import rabbit_reply

class TaskHandle(object):
    def __init__(self, main_obj, task_body):
        self.main_obj = main_obj  #传进来的实例
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

    def add_website(self):
        if self.task_body['data'].get('host_name') == settings.HOST_NAME:
            home_dir = os.path.join(settings.WEB_BASE_DIR, self.svr_name)
            web_root = os.path.join(home_dir, self.task_body['data'].get('web_path'))
            websit_name = self.task_body['data'].get('website_name')
            bind_domain = self.task_body['data'].get('bind_domain')
            pool_name = self.task_body['data'].get('pool_name')
            pool_ver = self.task_body['data'].get('pool_ver')
            callback_queue = self.task_body['callback_queue']
            print('pool_ver:', pool_ver)
            if pool_ver:
                with open('templates/new_app_pool.py', encoding='utf=8') as f:
                    power_cmd = f.read()
                    power_cmd = power_cmd % (pool_name, pool_name, pool_ver)
                    power_shell_file_name = settings.BASE_DIR + 'templates' + str(time.time()).split('.')[0] + '.ps1'
                    power_shell_file = open(power_shell_file_name, 'w')
                    power_shell_file.write(power_cmd)
                    power_shell_file.close()
                result = subprocess.Popen('powershell %s' % power_shell_file_name, shell=True,
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                recv_data = {
                    'info':  'ok' if result.stdout.read() else "",
                    'error': 'bad' if result.stderr.read() else ""
                }
                obj = rabbit_reply.MsgReply(callback_queue)
                obj.send(recv_data)
            else:
                print('没有新建应用程序池')




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
        #将自身实例传进去
        task = TaskHandle(self, task_body)
        task.processing()


    def msg_consume(self):
        self.channel.queue_declare(queue=self.queue_name)
        self.channel.basic_consume(self.msg_callback, queue=self.queue_name, no_ack=True)
        print('begin recives......')
        self.channel.start_consuming()