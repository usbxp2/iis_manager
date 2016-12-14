from django.db import models
from Splinter.models import UserProfile
# Create your models here.

class Host(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='服务器')
    ip_addr = models.GenericIPAddressField(unique=True, verbose_name='IP地址')
    type_choices = ((1, 'web'), (2, 'SQL Server'))
    host_type = models.SmallIntegerField(choices=type_choices, verbose_name='服务器类型')

    def __str__(self):
        return self.name

class Domain(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='域名')
    website = models.ForeignKey('WebSite', blank=True, null=True, verbose_name='绑定网站')
    status_choices = ((1, '已使用'), (0, '空闲'))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name='绑定状态')

    def __str__(self):
        return self.name

class AppPool(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name='应用程序名称')
    net_versin_choices = (
        (1, 'v1.1'),
        (2, 'v2.0'),
        (3, 'v3.5'),
        (4, 'v4.0'),
        (5, 'v4.5')
    )
    net_version = models.SmallIntegerField(choices=net_versin_choices, default=2, verbose_name='framwork版本')

    def __str__(self):
        return '%s %s' % (self.name, self.get_net_version_display())

    def get_choice_val(self, first):
        for i in self.net_versin_choices:
            if i[0] == first:
                return i[1]
        return None

class WebSite(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='网站名称')
    app_pool = models.ForeignKey(AppPool, verbose_name='应用程序池')
    webpath = models.CharField(max_length=64, unique=True, verbose_name='物理路径')
    public = models.BooleanField(default=False, verbose_name="是否公开")
    userprofile = models.ForeignKey(UserProfile, verbose_name='所属用户')
    host = models.ForeignKey(Host, verbose_name='所属服务器')

    def __str__(self):
        return self.name

class VirtualApp(models.Model):
    name = models.CharField(max_length=64, verbose_name='应用程序名称')
    father = models.ForeignKey(WebSite, verbose_name='父站点')
    app_pool = models.ForeignKey(AppPool, verbose_name="应用程序池名称", blank=True)
    webpath = models.CharField(max_length=64, verbose_name='物理路径')
    userprofile = models.ForeignKey(UserProfile, verbose_name='所属用户', blank=True)

    def __str__(self):
        return self.name