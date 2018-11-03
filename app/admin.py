from django.contrib import admin

# Register your models here.
from app.models import *

admin.site.register(Wheel)
admin.site.register(Mustbuy)
admin.site.register(Nav)
admin.site.register(Shop)