from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ClientProfile, ServiceProfile, Notification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Dodatkowe informacje', {'fields': ('role', 'phone', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'phone'),
        }),
    )


@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone', 'city', 'created_at']
    list_filter = ['voivodeship', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Dane osobowe', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone')
        }),
        ('Adres', {
            'fields': ('address', 'city', 'postal_code', 'voivodeship')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ServiceProfile)
class ServiceProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'city', 'voivodeship', 'is_verified', 'is_active']
    list_filter = ['is_verified', 'is_active', 'voivodeship']
    search_fields = ['company_name', 'email', 'phone', 'nip']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Dane firmy', {
            'fields': ('user', 'company_name', 'nip', 'email', 'phone')
        }),
        ('Adres', {
            'fields': ('address', 'city', 'postal_code', 'voivodeship')
        }),
        ('Opis i specjalizacje', {
            'fields': ('description', 'specializes_in')
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active')
        }),
    )
