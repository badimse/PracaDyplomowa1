#!/usr/bin/env python
"""
Skrypt tworzący domyślnego administratora
Uruchom: python create_superuser.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import User

# Sprawdź czy administrator już istnieje
if User.objects.filter(username='admin').exists():
    print("Administrator 'admin' już istnieje!")
else:
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@serwis.pl',
        password='admin123',
        role='admin'
    )
    print("✓ Administrator został utworzony!")
    print("  Login: admin")
    print("  Hasło: admin123")
    print("  Email: admin@serwis.pl")
