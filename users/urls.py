from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('admin-panel/', views.admin_panel_view, name='admin_panel'),
    path('admin-panel/user/create/', views.admin_user_create_view, name='admin_user_create'),
    path('admin-panel/user/<int:user_id>/delete/', views.admin_user_delete_view, name='admin_user_delete'),
    path('notifications/', views.notifications_list_view, name='notifications_list'),
    path('notification/<int:notification_id>/read/', views.notification_mark_as_read_view, name='notification_read'),
    path('notifications/mark-all/', views.notification_mark_all_as_read_view, name='notification_mark_all'),
]
