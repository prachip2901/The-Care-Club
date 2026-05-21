from django.contrib import admin
from .models import *

# Register your models here.
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['name','email','mobile','is_verified']
admin.site.register(Registeration,RegistrationAdmin)

class CategoryTypeAdmin(admin.ModelAdmin):
    list_display = ['name','description']
admin.site.register(CategoryType,CategoryTypeAdmin)
admin.site.register(Donation)
admin.site.register(Superuser)