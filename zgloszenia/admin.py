from django.contrib import admin
from .models import DeviceCategory, DeviceType, ServiceRequest, ServiceOffer, ServiceRequestView, Message, Review, Payment


@admin.register(DeviceCategory)
class DeviceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(DeviceType)
class DeviceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'device_brand', 'status', 'priority', 'voivodeship', 'created_at']
    list_filter = ['status', 'priority', 'device_category', 'voivodeship', 'warranty_status']
    search_fields = ['title', 'description', 'device_brand', 'device_model', 'client__first_name', 'client__last_name']
    readonly_fields = ['submitted_at', 'completed_at', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informacje podstawowe', {
            'fields': ('client', 'title', 'description', 'status', 'priority')
        }),
        ('Urządzenie', {
            'fields': ('device_category', 'device_type', 'device_brand', 'device_model', 'serial_number', 'purchase_date', 'warranty_status')
        }),
        ('Lokalizacja', {
            'fields': ('voivodeship', 'city', 'postal_code', 'address', 'is_mobile_service')
        }),
        ('Budżet', {
            'fields': ('estimated_budget',)
        }),
        ('Daty', {
            'fields': ('submitted_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceOffer)
class ServiceOfferAdmin(admin.ModelAdmin):
    list_display = ['service', 'service_request', 'price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['service__company_name', 'service_request__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Oferta', {
            'fields': ('service_request', 'service', 'price', 'status')
        }),
        ('Szczegóły', {
            'fields': ('message', 'estimated_time', 'warranty_period', 'additional_info')
        }),
        ('Daty', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServiceRequestView)
class ServiceRequestViewAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'service', 'viewed_at']
    list_filter = ['viewed_at']
    ordering = ['-viewed_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'sender', 'recipient', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username', 'recipient__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'client', 'rating', 'would_recommend', 'created_at']
    list_filter = ['rating', 'would_recommend', 'created_at']
    search_fields = ['service__company_name', 'client__first_name', 'client__last_name', 'comment']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'service_request', 'service_offer', 'amount', 'admin_fee', 'final_amount', 'status', 'payment_method', 'paid_at', 'released_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['service_request__title', 'service_offer__service__company_name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at', 'paid_at', 'released_at', 'refunded_at', 'released_by']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informacje o płatności', {
            'fields': ('service_request', 'service_offer', 'status', 'payment_method', 'transaction_id')
        }),
        ('Kwoty', {
            'fields': ('amount', 'admin_fee', 'final_amount')
        }),
        ('Daty', {
            'fields': ('paid_at', 'released_at', 'refunded_at', 'created_at', 'updated_at')
        }),
        ('Notatki administratora', {
            'fields': ('admin_notes', 'released_by'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['release_selected_payments', 'refund_selected_payments']
    
    def release_selected_payments(self, request, queryset):
        """Akcja masowa: wypłać środki dla wybranych płatności"""
        released_count = 0
        for payment in queryset.filter(status='paid_to_admin'):
            try:
                payment.release_to_service(released_by_user=request.user)
                released_count += 1
            except ValueError:
                pass
        self.message_user(request, f'Wypłacono {released_count} płatności.')
    release_selected_payments.short_description = 'Wypłać wybrane płatności serwisom'
    
    def refund_selected_payments(self, request, queryset):
        """Akcja masowa: zwróć środki dla wybranych płatności"""
        refunded_count = 0
        for payment in queryset.filter(status='paid_to_admin'):
            try:
                payment.refund_to_client()
                refunded_count += 1
            except ValueError:
                pass
        self.message_user(request, f'Zwrócono {refunded_count} płatności.')
    refund_selected_payments.short_description = 'Zwróć wybrane płatności klientom'
