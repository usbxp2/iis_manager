from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.acc_login),
    url(r'index/$', views.index, name='index'),
    url(r'websites/(?P<host_id>\d+)$', views.websites, name='websites'),
    url(r'^add_website/(?P<host_id>\d+)$', views.add_website, name='add_website'),
    url(r'^get_dir/(?P<host_id>\d+)$', views.get_dir, name='get_dir'),
    url(r'^show_app/(?P<host_id>\d+)/(?P<web_id>\d+)$', views.show_app, name='show_app'),
    url(r'^add_apl/(?P<host_id>\d+)$', views.add_app_pool, name='add_app_pool'),
]
