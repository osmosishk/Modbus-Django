from django.contrib import admin
from .models import Slaves
from .models import Setting
from .models import Address


# Register your models here.
admin.site.register(Slaves)
admin.site.register(Setting)
admin.site.register(Address)