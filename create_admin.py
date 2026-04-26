#!/usr/bin/env python
"""
Skrypt tworzący użytkownika administratora
Uruchom: python create_admin.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import User, ClientProfile, ServiceProfile

def create_admin():
    username = input("Podaj nazwę użytkownika administratora: ")
    email = input("Podaj email administratora: ")
    password = input("Podaj hasło administratora: ")
    
    if User.objects.filter(username=username).exists():
        print(f"Użytkownik '{username}' już istnieje!")
        return
    
    admin = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        role='admin',
        is_staff=True,
        is_superuser=True
    )
    
    print(f"\n✓ Administrator '{username}' został utworzony!")
    print(f"  Email: {email}")
    print(f"\nMożesz się teraz zalogować na stronie /users/login/")
    print(f"Lub użyć panelu Django Admin na stronie /admin/")

if __name__ == '__main__':
    create_admin()
