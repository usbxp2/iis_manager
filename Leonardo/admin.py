from django.contrib import admin
from . import models
# Register your models here.



admin.site.register(models.Host)
admin.site.register(models.WebSite)
admin.site.register(models.AppPool)
admin.site.register(models.Domain)
admin.site.register(models.VirtualApp)
