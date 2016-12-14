import re

def check_cn(pool_name):
    '''检查字符串中是否含有中文'''
    exp = re.compile("[\\u4E00-\\u9FFF]+")
    m = exp.search(pool_name)
    if m:
        return True    #包含中文
    else:
        return False   #不包含中文

def check_ver(pool_version):
    '''检查版本信息是否合法'''
    exp = re.compile("^v[2,4]\.0$")
    m = exp.match(pool_version)
    if m:
        return True    #合法
    else:
        return False   #不合法

def check_pname(pname):
    '''
    ： 检测应用程序名称或应用程序池名称是否合法，数字字母和.组成
    :param pname:应用程序名称
    :return:True合法， False不合法
    '''
    exp = re.compile("^[a-z, A-Z, 0-9, \.]+$")
    m = exp.match(pname)
    if m:
        return True
    else:
        return False


def check_website_name(wname):
    '''
    检测输入的网站名称是否合法，中文，字母，数字组成
    :param wname: 网站名称字符串
    :return: True 合法 False 不合法
    '''
    exp = re.compile("^[\\u4E00-\\u9FFF, a-z, A-Z, 0-9]+$")
    m = exp.match(wname)
    return True if m else False

