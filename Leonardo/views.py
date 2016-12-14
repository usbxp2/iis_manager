from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from . import models
from Leonardo.modules import rabbit_mq, plugin
from Splinter.models import UserProfile
from Leonardo.modules.legal_check import check_pname, check_website_name
# Create your views here.

#全局
def global_setting(request):
    hosts = models.Host.objects.all()
    public_websites = models.WebSite.objects.filter(public=True)
    app_pool_list = models.AppPool.objects.all()
    return locals()

def acc_login(request):
    if request.method == "GET":
        return render(request, 'Leonardo/login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(index)
        else:
            login_err = 'wrong username or password!'
            return render(request, 'Leonardo/login.html', locals())

def index(request):
    return render(request, 'Leonardo/index.html')

def add_app_pool(request, host_id):
    try:
        host_name = models.Host.objects.get(id=host_id).name  #获取客户端服务器名称
        pool_name = request.POST.get('pool_name')          #应用程序池名称
        pool_ver_choice = int(request.POST.get('pool_ver'))   #应用程序池版本
        pool_ver_obj = models.AppPool()      #实例化models表
        pool_ver = pool_ver_obj.get_choice_val(pool_ver_choice)  #取出版本对应的字符串,choices中的字符串
        if pool_ver and check_pname(pool_name):  #判断接收到的应用程序池版本是否是选项中的，并且应用程序池名称要合法
            if not models.AppPool.objects.filter(name=pool_name): #如果输入的应用程序池名称在数据库中不存在
                message = {'cmd': 'add_app_pool',
                           'pool_name': pool_name,  #应用程序名
                           'pool_ver': pool_ver,
                           'host_name': host_name,  #主机名
                           'svr_name': request.user.name
                           }
                print('message:', message)
                reply_data = plugin.send_recv(host_name, message)
                if reply_data == '2001':     #成功
                    try:
                        models.AppPool.objects.create(name=pool_name, net_version=pool_ver_choice)  #写入数据库
                        return HttpResponse('2001')
                    except:
                        #如果写入数据库失败，那么需要删除创建的应用程序池，保证数据库信息与真实情况一致
                        return HttpResponse('4001')
            else:
                return HttpResponse('3001')   #名称已存在
        return HttpResponse('1001')      #失败
    except Exception as e:
        print(e)
        return HttpResponse('1001')    #失败

def websites(request, host_id):
    #print(request.user.email)
    try:
        host_obj = models.Host.objects.get(id=host_id)
    except:
        return render(request, 'Leonardo/404.html')
    website_list = models.WebSite.objects.filter(host__id=host_id, userprofile__email=request.user.email, public=False)
    return render(request, 'Leonardo/websites.html', locals())

def add_website(request, host_id):
    host_id = host_id
    host_name = models.Host.objects.get(id=host_id).name
    if request.method == "GET":
        pool_list = models.AppPool.objects.all()
        domain_list = models.Domain.objects.filter(status=0)
        svr_name = request.user.name
        message = {'cmd': 'get_dir',
                   'svr_name': svr_name,  #用户
                   'host_name': host_name  #主机名
                   }
        dir_list = plugin.send_recv(host_name, message)
        #print('dir_list:', dir_list, type(dir_list))
        return render(request, 'Leonardo/add_website.html', locals())
    else:
        #POST请求
        website_name = request.POST.get('website_name')
        pool_name_id = request.POST.get('pool_name') or ('new ' + request.POST.get('box'))
        domain_id = request.POST.get('bind_domain')
        bind_domain = ''
        if domain_id.isdigit():
            bind_domain = models.Domain.objects.get(id=request.POST.get('bind_domain')).name
        web_path = request.POST.get('web_path')
        public = request.POST.get('isadmin') or False
        owner = request.user.name
        error_msg = ''
        website_name_isexist = False
        pool_name_isexist = False

        if check_website_name(website_name) and check_pool(pool_name_id) and bind_domain and web_path:
            pool_name = ''
            if 'new' in pool_name_id:
                pool_name, pool_ver = pool_name_id.split()[1], pool_name_id.split()[2]
                if models.AppPool.objects.filter(name=pool_name):
                    error_msg += '应用程序池名称已经存在！'
            else:
                pool_name, pool_ver = models.AppPool.objects.get(id=pool_name_id), ''

            if models.WebSite.objects.filter(name=website_name):
                website_name_isexist = True
                error_msg += '网站名称已经存在'

            if website_name_isexist or pool_name_isexist:
                return render(request, 'Leonardo/add_website.html', locals())

            #print('+++++++++++++++++++++++++++++++++++++=', bind_domain)

            message = {
                'cmd': 'add_website',
                'website_name': website_name,
                'pool_name': pool_name,
                'pool_ver': pool_ver,
                'bind_domain': bind_domain,
                'web_path': web_path,
                'is_public': public,
                'svr_name': owner,           #用户名
                'host_name': host_name,       #主机名
                'port': 80
            }
            reply_data = plugin.send_recv(host_name, owner, message)
            #print('reply_data:', reply_data, type(reply_data))
            if reply_data == '1002':
                error_msg = '创建失败'
            else:
                #站点创建成功，将应用程序池，站点信息写入数据库
                net_ver_tup = models.AppPool().net_versin_choices
                pool_choice_id = 2   #设置默认值为2
                for i in net_ver_tup:
                    if i[1] == pool_ver:
                        pool_choice_id = i[0]
                models.AppPool.objects.create(name=pool_name, net_version=pool_choice_id)  #这里注意
                app_pool_id = models.AppPool.objects.get(name=pool_name).id
                user_id = UserProfile.objects.get(email=request.user.email).id
                models.WebSite.objects.create(name=website_name, webpath=web_path,
                                              public=public, app_pool_id=app_pool_id,
                                              userprofile_id=user_id, host_id=host_id)
                website_id = models.WebSite.objects.get(name=website_name).id
                models.Domain.objects.filter(name=bind_domain).update(website_id=website_id, status=1)
                return redirect('/leonardo/websites/%s' % host_id)
            return HttpResponse(reply_data)
        else:
            #print('website:', check_website_name(website_name))
            #print('pool_status:', check_pool(pool_name_id))
            error_msg = '填写不规范，请重新填写'
            return render(request, 'Leonardo/add_website.html', locals())

def get_dir(request, host_id):
    if request.method == 'GET':
        host_name = models.Host.objects.get(id=host_id).name
        user_name = request.user.name
        #print('username:', user_name)

        message = {'cmd': 'get_dir',
                   'svr_name': user_name,  #用户
                   'host_name': host_name  #主机名
                   }
        dir_list = plugin.send_recv(host_name, user_name, message)
        return dir_list


def show_app(request, host_id, web_id):
    host_id, web_id = host_id, web_id
    if request.method == 'GET':
        web_obj = models.WebSite.objects.get(id=web_id)
        app_list = web_obj.virtualapp_set.filter(userprofile=request.user.id)
        dir_list = get_dir(request, host_id)
        print(dir_list)
        return render(request, 'Leonardo/show_app.html', locals())
    else:
        print(request.POST)