__author__ = 'huanghao'
import pika, random, json
from django.conf import settings


class leo_rabbitmq(object):
    def __init__(self, server_name):
        '''server_name: routing_key 队列名称'''
        self.server_name = server_name
        self.task_id = random.randint(100000, 999999)
        self.rabbit_IP = settings.RABBITMQ_IP
        self.create()

    def create(self):
        '''连接rabbitmq'''
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.rabbit_IP))
        self.channel = self.connection.channel()


    def send(self, message):
        self.channel.queue_declare(queue=self.server_name)
        print('-------------> begin send data...')
        self.task_data = {
            'callback_queue': 'TASK_CALLBACK_%s' % self.task_id,
            'data': message
        }
        print('等待发送的消息---------->', self.task_data)
        print('---------------->正在连接消息队列')
        self.channel.basic_publish(exchange='', routing_key=self.server_name, body=json.dumps(self.task_data))
        print('已发送到队列%s' % self.server_name)
        self.close()

    def get_callback(self, ch, method, properties, body):
        print(body)
        self.get_client_data_1 = body
        print('1111111111111111', self.get_client_data_1)
        self.close()

    def wait_callback(self):
        self.create()
        print('create reply queue.....')
        self.channel.queue_declare(queue=self.task_data['callback_queue'])
        print('ready to recv.....')
        self.channel.basic_consume(self.get_callback, queue=self.task_data['callback_queue'], no_ack=True)
        self.channel.start_consuming()

    def get_client_data(self):
        print('关闭连接')
        return self.get_client_data_1

    def close(self):
        self.connection.close()
