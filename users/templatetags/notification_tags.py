from django import template

register = template.Library()


@register.filter
def unread_count(notifications):
    """Zwraca liczbę nieprzeczytanych powiadomień"""
    return notifications.filter(is_read=False).count()


@register.simple_tag
def get_unread_count(user):
    """Zwraca liczbę nieprzeczytanych powiadomień użytkownika"""
    if hasattr(user, 'notifications'):
        return user.notifications.filter(is_read=False).count()
    return 0
