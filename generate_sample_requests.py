import os
import django
import random
from datetime import timedelta, datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import ClientProfile, ServiceProfile, User
from zgloszenia.models import ServiceRequest, DeviceCategory, DeviceType
from django.utils import timezone

# Dane testowe
TYTULY = [
    "Naprawa telewizora", "Serwis lodówki", "Naprawa pralki", "Serwis zmywarki",
    "Naprawa mikrofalówki", "Serwis piekarnika", "Naprawa odkurzacza", "Serwis suszarki",
    "Naprawa płyty indukcyjnej", "Serwis okapu", "Naprawa robota kuchennego", "Serwis ekspresu do kawy",
    "Naprawa konsoli do gier", "Serwis komputera", "Naprawa laptopa", "Serwis monitora",
    "Naprawa drukarki", "Serwis skanera", "Naprawa tabletu", "Serwis smartfona",
    "Naprawa radia", "Serwis wzmacniacza", "Naprawa kolumn głośnikowych", "Serwis projektora",
    "Naprawa kamery", "Serwis drona", "Naprawa smartwatcha", "Serwis routera",
]

OPISY = [
    "Urządzenie nie włącza się, brak reakcji na przyciski.",
    "Dziwne dźwięki podczas pracy, urządzenie wibruje.",
    "Nie działa jedna z funkcji, wymaga diagnostyki.",
    "Urządzenie wyłącza się samoistnie podczas pracy.",
    "Wyciek wody z urządzenia, konieczna naprawa.",
    "Przegrzewanie się urządzenia po krótkim czasie pracy.",
    "Uszkodzony wyświetlacz, brak obrazu.",
    "Nie działa pilot, urządzenie nie reaguje.",
    "Spalony bezpiecznik, potrzeba wymiany części.",
    "Kabel zasilający uszkodzony, iskrzenie.",
    "Nie działa grzałka, urządzenie nie grzeje.",
    "Silnik nie pracuje, konieczna wymiana.",
    "Płyta główna uszkodzona, diagnostyka wymagana.",
    "Bateria nie trzyma charge, szybkie rozładowywanie.",
    "Ekran miga, problemy z wyświetlaniem.",
    "Brak dźwięku, głośniki nie działają.",
    "Zacinanie się mechanizmu, nie działa poprawnie.",
    "Korozja elementów, zalanie urządzenia.",
    "Software error, konieczny reset lub flash.",
    "Mechaniczne uszkodzenie obudowy, elementy luźne.",
]

MIASTA = [
    "Warszawa", "Kraków", "Łódź", "Wrocław", "Poznań", "Gdańsk", "Szczecin", "Bydgoszcz",
    "Lublin", "Białystok", "Katowice", "Gdynia", "Częstochowa", "Radom", "Sosnowiec",
    "Toruń", "Kielce", "Rzeszów", "Olsztyn", "Bielsko-Biała",
]

WOJEWODZTWA = [
    "mazowieckie", "małopolskie", "łódzkie", "dolnośląskie", "wielkopolskie",
    "pomorskie", "zachodniopomorskie", "kujawsko-pomorskie", "lubelskie", "podlaskie",
    "śląskie", "pomorskie", "śląskie", "mazowieckie", "śląskie",
    "kujawsko-pomorskie", "świętokrzyskie", "podkarpackie", "warmińsko-mazurskie", "śląskie",
]

KOD_POCZTOWY_PREFIX = ["00", "01", "02", "03", "04", "05", "30", "31", "40", "41", "50", "51", "60", "61", "70", "71", "80", "81", "90", "91"]

STATUSY = ['draft', 'submitted', 'viewed_by_services', 'offers_received', 'in_progress', 'completed', 'cancelled']
STATUS_WAGI = [5, 25, 15, 15, 15, 20, 5]  # Rozkład statusów

PRIORYTETY = ['low', 'normal', 'high', 'urgent']
PRIORYTET_WAGI = [20, 50, 20, 10]  # Rozkład priorytetów

def generate_random_date(days_back=365):
    """Generuje losową datę z ostatnich days_back dni"""
    days_ago = random.randint(0, days_back)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    return timezone.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

def generate_postal_code():
    """Generuje losowy kod pocztowy"""
    prefix = random.choice(KOD_POCZTOWY_PREFIX)
    suffix = random.randint(100, 999)
    return f"{prefix}-{suffix:03d}"

def main():
    print("Ładowanie danych...")
    
    # Pobierz kategorie i typy
    categories = list(DeviceCategory.objects.all())
    if not categories:
        print("Brak kategorii urządzeń! Uruchom najpierw load_sample_data.py")
        return
    
    # Pobierz klientów
    clients = list(ClientProfile.objects.all())
    if not clients:
        print("Brak klientów! Uruchom najpierw load_sample_data.py")
        return
    
    print(f"Znaleziono {len(categories)} kategorii i {len(clients)} klientów")
    
    # Generuj zgłoszenia
    num_requests = 400
    created_count = 0
    
    print(f"Generowanie {num_requests} zgłoszeń...")
    
    for i in range(num_requests):
        client = random.choice(clients)
        category = random.choice(categories)
        
        # Losowe typy z kategorii
        types = list(category.device_types.all())
        device_type = random.choice(types) if types else None
        
        # Generuj dane
        title = random.choice(TYTULY) + f" #{i+1}"
        description = random.choice(OPISY)
        
        status = random.choices(STATUSY, weights=STATUS_WAGI)[0]
        priority = random.choices(PRIORYTETY, weights=PRIORYTET_WAGI)[0]
        
        city_idx = random.randint(0, len(MIASTA)-1)
        city = MIASTA[city_idx]
        voivodeship = WOJEWODZTWA[city_idx]
        
        # Losowe marki
        brands = ["Samsung", "LG", "Sony", "Bosch", "Siemens", "Whirlpool", "Philips", "Panasonic", "Xiaomi", "Apple"]
        brand = random.choice(brands)
        model = f"{random.choice(['X', 'A', 'B', 'C', 'E'])}{random.randint(100, 999)}"
        
        created_at = generate_random_date(365)
        
        # Utwórz zgłoszenie
        request = ServiceRequest.objects.create(
            client=client,
            title=title,
            description=description,
            device_category=category,
            device_type=device_type,
            device_brand=brand,
            device_model=model,
            serial_number=f"SN{random.randint(100000, 999999)}",
            purchase_date=generate_random_date(730).date() if random.random() > 0.3 else None,
            warranty_status=random.choice([True, False]),
            priority=priority,
            status=status,
            voivodeship=voivodeship,
            city=city,
            postal_code=generate_postal_code(),
            address=f"ul. Testowa {random.randint(1, 100)}" if random.random() > 0.5 else "",
            is_mobile_service=random.choice([True, False]),
            estimated_budget=random.choice([100, 150, 200, 250, 300, 400, 500, 600, 800, 1000]) if random.random() > 0.3 else None,
            created_at=created_at,
            updated_at=created_at + timedelta(hours=random.randint(1, 48)),
        )
        
        # Ustaw submitted_at dla zgłoszeń nie-będących szkicami
        if status != 'draft':
            request.submitted_at = created_at + timedelta(hours=random.randint(1, 12))
            request.save(update_fields=['submitted_at'])
        
        created_count += 1
        
        if (i + 1) % 50 == 0:
            print(f"  Utworzono {i + 1}/{num_requests} zgłoszeń...")
    
    print(f"\nGotowe! Utworzono {created_count} zgłoszeń.")
    
    # Statystyki
    print("\nStatystyki:")
    for status_key, status_label in ServiceRequest.STATUS_CHOICES:
        count = ServiceRequest.objects.filter(status=status_key).count()
        print(f"  {status_label}: {count}")
    
    print("\nRozkład priorytetów:")
    for priority_key, priority_label in ServiceRequest.PRIORITY_CHOICES:
        count = ServiceRequest.objects.filter(priority=priority_key).count()
        print(f"  {priority_label}: {count}")

if __name__ == '__main__':
    main()
