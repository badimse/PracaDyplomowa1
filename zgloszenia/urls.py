from django.urls import path
from . import views

urlpatterns = [
    path('', views.request_list_view, name='request_list'),
    path('create/', views.request_create_view, name='request_create'),
    path('<int:pk>/', views.request_detail_view, name='request_detail'),
    path('<int:pk>/submit/', views.request_submit_view, name='request_submit'),
    path('<int:pk>/cancel/', views.request_cancel_view, name='request_cancel'),
    path('<int:pk>/complete/', views.request_complete_view, name='request_complete'),
    path('<int:pk>/review/', views.review_create_view, name='review_create'),
    path('<int:pk>/message/', views.message_send_view, name='message_send'),
    path('<int:request_pk>/offer/', views.offer_create_view, name='offer_create'),
    path('offer/<int:pk>/accept/', views.offer_accept_view, name='offer_accept'),
    path('offer/<int:pk>/reject/', views.offer_reject_view, name='offer_reject'),
    
    # Payment Escrow URLs
    path('offer/<int:offer_pk>/payment/', views.payment_create_view, name='payment_create'),
    path('platnosci/<int:pk>/', views.payment_detail_view, name='payment_detail'),
    path('platnosci/<int:pk>/process/', views.payment_process_view, name='payment_process'),
    path('platnosci/<int:pk>/release/', views.payment_release_view, name='payment_release'),
    path('platnosci/<int:pk>/refund/', views.payment_refund_view, name='payment_refund'),
    path('platnosci/', views.payment_list_view, name='payment_list'),
    
    # API endpoints
    path('api/device-types/', views.get_device_types_ajax, name='api_device_types'),
    path('api/search/', views.search_requests_ajax, name='api_search'),
    path('api/stats/', views.dashboard_stats_ajax, name='api_stats'),
    
    # Chat & Notifications
    path('chat/<int:request_pk>/', views.chat_view, name='chat'),
    path('api/messages/<int:request_pk>/', views.get_messages_ajax, name='api_messages'),
    path('api/notifications/count/', views.notifications_count_ajax, name='api_notifications_count'),
    
    # Payment Admin
    path('admin/payments/', views.payment_admin_list_view, name='payment_admin_list'),
]
