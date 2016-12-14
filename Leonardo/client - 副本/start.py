import os, sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from module import msg


if __name__ == '__main__':
    msg_par = msg.msghandle()
