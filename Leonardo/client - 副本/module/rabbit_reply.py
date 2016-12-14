import pika, json
from config import settings

class MsgReply(object):
    def __init__(self, queue_name):
        self.server_ip = settings.RABBITMQ_IP
        self.queue_name = queue_name
        self.make_connect()

    def make_connect(self):
        print('connenting queue....')
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(self.server_ip))
        self.channal = self.conn.channel()

    def send(self, message):
        print('连接队列%s.....' % self.queue_name)
        self.channal.queue_declare(queue=self.queue_name)
        print('ready send message......')
        print('等待发送的数据:', message)
        self.channal.basic_publish(exchange='', routing_key=self.queue_name, body=json.dumps(message))
        print('send message success...')
        self.conn.close()