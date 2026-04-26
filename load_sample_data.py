#!/usr/bin/env python
"""
Skrypt ładujący przykładowe dane do bazy
Uruchom: python load_sample_data.py
"""

import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import User, ClientProfile, ServiceProfile
from zgloszenia.models import DeviceCategory, DeviceType, ServiceRequest, ServiceOffer, Message, Review

def load_sample_data():
    print("Ładowanie przykładowych danych...")
    
    # ===== KLIENCI =====
    print("\n📋 Tworzenie klientów...")
    
    client1, _ = User.objects.get_or_create(
        username='jan_kowalski',
        defaults={'email': 'jan.kowalski@email.pl', 'role': 'client'}
    )
    cp1, _ = ClientProfile.objects.get_or_create(
        user=client1,
        defaults={
            'first_name': 'Jan',
            'last_name': 'Kowalski',
            'email': 'jan.kowalski@email.pl',
            'phone': '+48 123 456 789',
            'address': 'ul. Długa 15/4',
            'city': 'Warszawa',
            'postal_code': '00-123',
            'voivodeship': 'mazowieckie'
        }
    )
    print(f"  ✓ Jan Kowalski")
    
    client2, _ = User.objects.get_or_create(
        username='anna_nowak',
        defaults={'email': 'anna.nowak@email.pl', 'role': 'client'}
    )
    cp2, _ = ClientProfile.objects.get_or_create(
        user=client2,
        defaults={
            'first_name': 'Anna',
            'last_name': 'Nowak',
            'email': 'anna.nowak@email.pl',
            'phone': '+48 987 654 321',
            'address': 'ul. Krótka 8',
            'city': 'Kraków',
            'postal_code': '30-001',
            'voivodeship': 'małopolskie'
        }
    )
    print(f"  ✓ Anna Nowak")
    
    client3, _ = User.objects.get_or_create(
        username='piotr_wisniewski',
        defaults={'email': 'piotr.wisniewski@email.pl', 'role': 'client'}
    )
    cp3, _ = ClientProfile.objects.get_or_create(
        user=client3,
        defaults={
            'first_name': 'Piotr',
            'last_name': 'Wiśniewski',
            'email': 'piotr.wisniewski@email.pl',
            'phone': '+48 555 123 456',
            'address': 'ul. Szeroka 22',
            'city': 'Gdańsk',
            'postal_code': '80-001',
            'voivodeship': 'pomorskie'
        }
    )
    print(f"  ✓ Piotr Wiśniewski")
    
    # ===== SERWISY =====
    print("\n🔧 Tworzenie serwisów...")
    
    service1, _ = User.objects.get_or_create(
        username='electro_serwis',
        defaults={'email': 'kontakt@electroserwis.pl', 'role': 'service'}
    )
    sp1, _ = ServiceProfile.objects.get_or_create(
        user=service1,
        defaults={
            'company_name': 'ElectroSerwis Warszawa',
            'nip': '1234567890',
            'email': 'kontakt@electroserwis.pl',
            'phone': '+48 22 111 22 33',
            'address': 'ul. Techniczna 10',
            'city': 'Warszawa',
            'postal_code': '02-495',
            'voivodeship': 'mazowieckie',
            'description': 'Profesjonalny serwis RTV i AGD z 15-letnim doświadczeniem.',
            'specializes_in': 'TV, Smartfony, Tablety, Sprzęt Audio',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  ✓ ElectroSerwis Warszawa")
    
    service2, _ = User.objects.get_or_create(
        username='smart_fix',
        defaults={'email': 'biuro@smartfix.pl', 'role': 'service'}
    )
    sp2, _ = ServiceProfile.objects.get_or_create(
        user=service2,
        defaults={
            'company_name': 'SmartFix Kraków',
            'nip': '0987654321',
            'email': 'biuro@smartfix.pl',
            'phone': '+48 12 333 44 55',
            'address': 'ul. Naprawcza 5',
            'city': 'Kraków',
            'postal_code': '31-001',
            'voivodeship': 'małopolskie',
            'description': 'Autoryzowany serwis smartfonów i tabletów.',
            'specializes_in': 'Smartfony, Tablety, iPhone, iPad',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  ✓ SmartFix Kraków")
    
    service3, _ = User.objects.get_or_create(
        username='tv_master',
        defaults={'email': 'serwis@tvmaster.pl', 'role': 'service'}
    )
    sp3, _ = ServiceProfile.objects.get_or_create(
        user=service3,
        defaults={
            'company_name': 'TV-Master Gdańsk',
            'nip': '5678901234',
            'email': 'serwis@tvmaster.pl',
            'phone': '+48 58 777 88 99',
            'address': 'ul. Elektroniczna 12',
            'city': 'Gdańsk',
            'postal_code': '80-123',
            'voivodeship': 'pomorskie',
            'description': 'Specjalizujemy się w naprawie telewizorów wszystkich marek.',
            'specializes_in': 'TV LED, TV OLED, TV LCD, Monitory',
            'is_verified': True,
            'is_active': True
        }
    )
    print(f"  ✓ TV-Master Gdańsk")
    
    service4, _ = User.objects.get_or_create(
        username='mobile_pro',
        defaults={'email': 'kontakt@mobilepro.pl', 'role': 'service'}
    )
    sp4, _ = ServiceProfile.objects.get_or_create(
        user=service4,
        defaults={
            'company_name': 'MobilePro Wrocław',
            'nip': '4567890123',
            'email': 'kontakt@mobilepro.pl',
            'phone': '+48 71 222 33 44',
            'address': 'ul. Mobilna 7',
            'city': 'Wrocław',
            'postal_code': '50-001',
            'voivodeship': 'dolnośląskie',
            'description': 'Naprawa smartfonów i tabletów z dojazdem do klienta.',
            'specializes_in': 'Smartfony, Tablety, Konsole do gier',
            'is_verified': False,
            'is_active': True
        }
    )
    print(f"  ✓ MobilePro Wrocław")
    
    # ===== ZGŁOSZENIA =====
    print("\n📝 Tworzenie zgłoszeń...")
    
    tv_cat = DeviceCategory.objects.get(slug='telewizory')
    smartphone_cat = DeviceCategory.objects.get(slug='smartfony')
    tablet_cat = DeviceCategory.objects.get(slug='tablety')
    
    # Zgłoszenie 1 - TV nie działa
    req1, created = ServiceRequest.objects.get_or_create(
        title='Telewizor nie włącza się',
        defaults={
            'client': cp1,
            'description': 'Telewizor突然 przestał się włączać. Dioda standby miga na czerwono, ale ekran pozostaje czarny. Próbowałem różnych gniazdek, ale bez skutku.',
            'device_category': tv_cat,
            'device_brand': 'Samsung',
            'device_model': 'UE55NU7092',
            'priority': 'normal',
            'status': 'submitted',
            'voivodeship': 'mazowieckie',
            'city': 'Warszawa',
            'postal_code': '00-123',
            'address': 'ul. Długa 15/4',
            'is_mobile_service': False,
            'estimated_budget': 500.00,
            'submitted_at': '2024-04-10',
            'created_at': '2024-04-10',
        }
    )
    if created:
        print(f"  ✓ Zgłoszenie: {req1.title}")
    
    # Zgłoszenie 2 - iPhone zbita szybka
    req2, created = ServiceRequest.objects.get_or_create(
        title='iPhone 13 - zbita szybka',
        defaults={
            'client': cp2,
            'description': 'Telefon wypadł z ręki i szybka jest pęknięta. Ekran działa, ale pęknięcia utrudniają korzystanie. Czy jest możliwość wymiany na miejscu?',
            'device_category': smartphone_cat,
            'device_brand': 'Apple',
            'device_model': 'iPhone 13',
            'priority': 'high',
            'status': 'offers_received',
            'voivodeship': 'małopolskie',
            'city': 'Kraków',
            'postal_code': '30-001',
            'is_mobile_service': True,
            'estimated_budget': 800.00,
            'submitted_at': '2024-04-12',
            'created_at': '2024-04-12',
        }
    )
    if created:
        print(f"  ✓ Zgłoszenie: {req2.title}")
    
    # Zgłoszenie 3 - Tablet nie ładuje
    req3, created = ServiceRequest.objects.get_or_create(
        title='Tablet nie ładuje baterii',
        defaults={
            'client': cp3,
            'description': 'Tablet przestał ładować baterię. Podłączam ładowarkę ale ikona ładowania się nie pojawia. Próbowano różnych ładowarek - ten sam efekt.',
            'device_category': tablet_cat,
            'device_brand': 'Samsung',
            'device_model': 'Galaxy Tab S7',
            'priority': 'normal',
            'status': 'in_progress',
            'voivodeship': 'pomorskie',
            'city': 'Gdańsk',
            'postal_code': '80-001',
            'is_mobile_service': False,
            'estimated_budget': 300.00,
            'submitted_at': '2024-04-08',
            'created_at': '2024-04-08',
        }
    )
    if created:
        print(f"  ✓ Zgłoszenie: {req3.title}")
    
    # Zgłoszenie 4 - TV zielony ekran
    req4, created = ServiceRequest.objects.get_or_create(
        title='TV OLED - zielony pasek na ekranie',
        defaults={
            'client': cp1,
            'description': 'Na ekranie telewizora pojawił się zielony pionowy pasek po prawej stronie. Problem występuje na wszystkich źródłach sygnału.',
            'device_category': tv_cat,
            'device_type': DeviceType.objects.get(slug='tv-oled'),
            'device_brand': 'LG',
            'device_model': 'OLED55C1',
            'priority': 'normal',
            'status': 'submitted',
            'voivodeship': 'mazowieckie',
            'city': 'Warszawa',
            'postal_code': '00-123',
            'is_mobile_service': False,
            'estimated_budget': 1000.00,
            'warranty_status': True,
            'submitted_at': '2024-04-15',
            'created_at': '2024-04-15',
        }
    )
    if created:
        print(f"  ✓ Zgłoszenie: {req4.title}")
    
    # Zgłoszenie 5 - Smartfon zawiesza się
    req5, created = ServiceRequest.objects.get_or_create(
        title='Xiaomi - ciągłe zawieszanie się',
        defaults={
            'client': cp2,
            'description': 'Telefon co chwilę się zawiesza, wymaga restartu. Problem zaczął się po aktualizacji systemu. Czy to wina oprogramowania czy sprzętu?',
            'device_category': smartphone_cat,
            'device_type': DeviceType.objects.get(slug='android'),
            'device_brand': 'Xiaomi',
            'device_model': 'Redmi Note 10 Pro',
            'priority': 'low',
            'status': 'draft',
            'voivodeship': 'małopolskie',
            'city': 'Kraków',
            'postal_code': '30-001',
            'is_mobile_service': True,
            'estimated_budget': 200.00,
            'created_at': '2024-04-16',
        }
    )
    if created:
        print(f"  ✓ Zgłoszenie: {req5.title}")
    
    # ===== OFERTY =====
    print("\n💼 Tworzenie ofert...")
    
    # Oferta dla zgłoszenia 2
    offer1, created = ServiceOffer.objects.get_or_create(
        service_request=req2,
        service=sp2,
        defaults={
            'message': 'Jesteśmy autoryzowanym serwisem Apple. Wymiana szybki na oryginalną część z zachowaniem wodoodporności. Czas realizacji: 24h.',
            'price': 750.00,
            'estimated_time': '24 godziny',
            'warranty_period': '12 miesięcy',
            'status': 'pending',
            'created_at': '2024-04-12',
        }
    )
    if created:
        print(f"  ✓ Oferta SmartFix dla iPhone")
    
    offer2, created = ServiceOffer.objects.get_or_create(
        service_request=req2,
        service=sp1,
        defaults={
            'message': 'Oferujemy wymianę szybki w cenie konkurencyjnej. Używamy wysokiej jakości zamienników. Możliwy dojazd do klienta.',
            'price': 550.00,
            'estimated_time': '48 godzin',
            'warranty_period': '6 miesięcy',
            'status': 'pending',
            'created_at': '2024-04-13',
        }
    )
    if created:
        print(f"  ✓ Oferta ElectroSerwis dla iPhone")
    
    # Oferta dla zgłoszenia 3
    offer3, created = ServiceOffer.objects.get_or_create(
        service_request=req3,
        service=sp3,
        defaults={
            'message': 'Diagnoza wskazuje na uszkodzony port ładowania lub kontroler ładowania. Wymiana na miejscu.',
            'price': 250.00,
            'estimated_time': '2-3 dni robocze',
            'warranty_period': '6 miesięcy',
            'status': 'accepted',
            'created_at': '2024-04-09',
        }
    )
    if created:
        print(f"  ✓ Oferta TV-Master dla Tablet")
    
    # ===== WIADOMOŚCI =====
    print("\n💬 Tworzenie wiadomości...")
    
    Message.objects.get_or_create(
        service_request=req3,
        sender=service3,
        recipient=client3,
        defaults={
            'content': 'Dzień dobry, przystępujemy do naprawy. Po diagnozie okaże się czy to port ładowania czy kontroler. Pozdrawiam, TV-Master',
            'is_read': True,
            'created_at': '2024-04-09',
        }
    )
    
    Message.objects.get_or_create(
        service_request=req3,
        sender=client3,
        recipient=service3,
        defaults={
            'content': 'Dziękuję za informację. Czekam na diagnozę.',
            'is_read': True,
            'created_at': '2024-04-09',
        }
    )
    print(f"  ✓ 2 wiadomości w zgłoszeniu #3")
    
    # ===== OPINIE =====
    print("\n⭐ Tworzenie opinii...")
    
    # Opinia dla zakończonego zgłoszenia (symulacja)
    req_completed, _ = ServiceRequest.objects.get_or_create(
        title='Naprawa telewizora Sony - ZAKOŃCZONE',
        defaults={
            'client': cp3,
            'description': 'Telewizor nie uruchamiał się poprawnie.',
            'device_category': tv_cat,
            'device_brand': 'Sony',
            'device_model': 'KD-55X8000H',
            'priority': 'normal',
            'status': 'completed',
            'voivodeship': 'pomorskie',
            'city': 'Gdańsk',
            'postal_code': '80-001',
            'submitted_at': '2024-03-01',
            'completed_at': '2024-03-15',
            'created_at': '2024-03-01',
        }
    )
    
    Review.objects.get_or_create(
        service_request=req_completed,
        service=sp3,
        client=cp3,
        defaults={
            'rating': 5,
            'comment': 'Bardzo profesjonalna obsługa. Naprawa wykonana szybko i w dobrej cenie. Polecam!',
            'would_recommend': True,
            'created_at': '2024-03-16',
        }
    )
    print(f"  ✓ Opinia dla TV-Master (5/5)")
    
    print("\n✅ Przykładowe dane zostały załadowane!")
    print("\n📊 Podsumowanie:")
    print(f"  - Klienci: {ClientProfile.objects.count()}")
    print(f"  - Serwisy: {ServiceProfile.objects.count()}")
    print(f"  - Zgłoszenia: {ServiceRequest.objects.count()}")
    print(f"  - Oferty: {ServiceOffer.objects.count()}")
    print(f"  - Opinie: {Review.objects.count()}")
    
    print("\n🔐 Dane do logowania:")
    print("  - Administrator: admin / admin123")
    print("  - Klient: jan_kowalski / (ustaw hasło przez panel admina)")
    print("  - Serwis: electro_serwis / (ustaw hasło przez panel admina)")

if __name__ == '__main__':
    load_sample_data()
