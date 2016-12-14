import subprocess, os, time
from config import settings

'''
def create_ps(muban_file, cmd_file, *args, **kwargs):
    with open(muban_file, encoding='utf=8') as f:
        power_cmd = f.read()
        power_cmd = power_cmd % (pool_name, pool_name, pool_ver)
        power_shell_file_name = os.path.join(os.path.join(settings.BASE_DIR, 'temp'), str(time.time()).split('.')[0] + '.ps1')
        power_shell_file = open(power_shell_file_name, 'w')
        power_shell_file.write(power_cmd)
        power_shell_file.close()
'''

def run_ps(cmd_file):  #执行powershell脚本
    result = subprocess.Popen('powershell -file %s' % cmd_file, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info, error = result.stdout.read(), result.stderr.read()
    return info, error


def new_app_pool(pool_name, pool_ver):
    '''
    :
    :param pool_name:
    :param pool_ver:
    :return:创建成功返回True, 失败返回False
    '''
    with open('templates/new_app_pool.py', encoding='utf=8') as f:
        power_cmd = f.read()
        power_cmd = power_cmd % (pool_name, pool_name, pool_ver)
        power_shell_file_name = os.path.join(os.path.join(settings.BASE_DIR, 'temp'), str(time.time()).split('.')[0] + '.ps1')
        power_shell_file = open(power_shell_file_name, 'w')
        power_shell_file.write(power_cmd)
        power_shell_file.close()
        info, error = run_ps(power_shell_file_name)
        return False if error else True


def new_website(website_name, port, bind_domain, web_root, pool_name):
    with open('templates/new_website.py', encoding='utf=8') as f:
        power_cmd = f.read()
        power_cmd = power_cmd % (website_name, port, bind_domain, web_root, website_name, pool_name)
        power_shell_file_name = os.path.join(os.path.join(settings.BASE_DIR, 'temp'), str(time.time()).split('.')[0] + '.ps1')
        print('\033[0;32;1m %s \033[0m' % power_shell_file_name)
        power_shell_file = open(power_shell_file_name, 'w')
        power_shell_file.write(power_cmd)
        power_shell_file.close()
        info, error = run_ps(power_shell_file_name)
        return False if error else True
