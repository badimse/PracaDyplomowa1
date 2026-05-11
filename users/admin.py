from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from .models import User, ClientProfile, ServiceProfile, Notification

# --- 1. FUNKCJA POMOCNICZA DO IDENTYFIKACJI KONT DEMO ---
def is_demo_user(user):
    """Zwraca True, jeśli użytkownik należy do grupy demonstracyjnej"""
    return user.username in ['admin', 'user', 'serwis']

# --- 2. MIXIN ZABEZPIECZAJĄCY (Zasada DRY - Don't Repeat Yourself) ---
class DemoSecurityMixin:
    """
    Mixin blokujący usuwanie rekordów oraz masowe akcje usuwania 
    dla wybranych użytkowników demo.
    """
    def has_delete_permission(self, request, obj=None):
        if is_demo_user(request.user):
            return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if is_demo_user(request.user):
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

# --- 3. KLASA BAZOWA DLA MODELI PROFILI ---
class BaseDemoAdmin(DemoSecurityMixin, admin.ModelAdmin):
    """Klasa bazowa dla standardowych modeli profilowych"""
    pass

# --- 4. REJESTRACJA MODELI W PANELU ADMINA ---

@admin.register(User)
class UserAdmin(DemoSecurityMixin, BaseUserAdmin):
    """
    Rozszerzony admin użytkownika z blokadą usuwania dla kont demo.
    Dziedziczy po BaseUserAdmin, aby zachować funkcje Django Auth.
    """
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
class ClientProfileAdmin(BaseDemoAdmin):
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
class NotificationAdmin(BaseDemoAdmin):
    list_display = ['user', 'title', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(ServiceProfile)
class ServiceProfileAdmin(BaseDemoAdmin):
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