from django.contrib import admin
from .models import User, Session

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'name', 'phone_number', 'auth_type', 'created_at', 'updated_at')
    list_filter = ('auth_type', 'created_at')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('email',)

class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'token', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'user', 'device_name')
    search_fields = ('user__username', 'device_name', 'token')

admin.site.register(Session, SessionAdmin)

admin.site.register(User, UserAdmin)
