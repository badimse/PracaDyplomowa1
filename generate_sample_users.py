import os
import django
import random
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import ClientProfile, ServiceProfile, User
from zgloszenia.models import ServiceRequest, ServiceOffer

# Dane testowe
IMIONA_MESKIE = [
    "Adam", "Andrzej", "Bartosz", "Dawid", "Grzegorz", "Jakub", "Jan", "Kacper",
    "Krzysztof", "Marcin", "Michał", "Paweł", "Piotr", "Rafał", "Robert", "Stanisław",
    "Szymon", "Tomasz", "Wojciech", "Zbigniew"
]

IMIONA_ZENSKIE = [
    "Agnieszka", "Aleksandra", "Anna", "Barbara", "Beata", "Dorota", "Ewa", "Grażyna",
    "Joanna", "Katarzyna", "Kinga", "Krystyna", "Magdalena", "Małgorzata", "Maria",
    "Marta", "Monika", "Patrycja", "Teresa", "Zofia"
]

NAZWISKA = [
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński", "Lewandowski",
    "Zieliński", "Szymański", "Woźniak", "Dąbrowski", "Kozłowski", "Jankowski", "Mazur",
    "Kwiatkowski", "Krawczyk", "Piotrowski", "Grabowski", "Pawłowski", "Michalski",
    "Nowicki", "Marciniak", "Walczak", "Stępień", "Jaworski", "Górski", "Zając",
    "Włodarczyk", "Pawlik", "Wróbel"
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

NAZWY_FIRM = [
    "Serwis", "Naprawa", "Tech", "Elektronika", "RTV", "AGD", "Service", "Fix", "Pro", "Expert",
    "Master", "Plus", "Max", "Super", "Multi", "Ultra", "Mega", "Best", "Top", "Premium"
]

def generate_username(first_name, last_name):
    """Generuje unikalny username"""
    base = f"{first_name.lower()}.{last_name.lower()}"
    suffix = random.randint(1, 9999)
    return f"{base}{suffix}"

def generate_email(first_name, last_name):
    """Generuje email"""
    domains = ["gmail.com", "onet.pl", "wp.pl", "interia.pl", "o2.pl", "outlook.com"]
    base = f"{first_name.lower()}.{last_name.lower()}"
    suffix = random.randint(1, 9999)
    domain = random.choice(domains)
    return f"{base}{suffix}@{domain}"

def generate_password():
    """Generuje losowe hasło"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def generate_postal_code(city_idx):
    """Generuje kod pocztowy dla miasta"""
    prefixes = ["00", "01", "02", "03", "04", "30", "31", "40", "41", "50", "51", "60", "61", "70", "71", "80", "81", "90", "91", "20"]
    prefix = prefixes[city_idx] if city_idx < len(prefixes) else random.choice(prefixes)
    suffix = random.randint(100, 999)
    return f"{prefix}-{suffix:03d}"

def main():
    print("Ładowanie danych...")
    
    num_clients = 300
    num_services = 100
    
    created_clients = 0
    created_services = 0
    
    # Generuj klientów
    print(f"\nGenerowanie {num_clients} klientów...")
    
    for i in range(num_clients):
        first_name = random.choice(IMIONA_MESKIE if random.random() > 0.5 else IMIONA_ZENSKIE)
        last_name = random.choice(NAZWISKA)
        city_idx = random.randint(0, len(MIASTA)-1)
        city = MIASTA[city_idx]
        voivodeship = WOJEWODZTWA[city_idx]
        
        username = generate_username(first_name, last_name)
        email = generate_email(first_name, last_name)
        password = generate_password()
        
        # Sprawdź czy username istnieje
        if User.objects.filter(username=username).exists():
            continue
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='client'
        )
        
        ClientProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=f"+48 {random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}",
            city=city,
            postal_code=generate_postal_code(city_idx),
            voivodeship=voivodeship,
        )
        
        created_clients += 1
        
        if (created_clients + 1) % 50 == 0:
            print(f"  Utworzono {created_clients} klientów...")
    
    print(f"\nUtworzono {created_clients} klientów.")
    
    # Generuj serwisy
    print(f"\nGenerowanie {num_services} serwisów...")
    
    for i in range(num_services):
        first_name = random.choice(IMIONA_MESKIE)
        last_name = random.choice(NAZWISKA)
        city_idx = random.randint(0, len(MIASTA)-1)
        city = MIASTA[city_idx]
        voivodeship = WOJEWODZTWA[city_idx]
        
        company_name = f"{random.choice(NAZWY_FIRM)} {first_name} {last_name}"
        username = f"serwis_{i+1}_{random.randint(1000, 9999)}"
        email = generate_email(first_name, last_name)
        password = generate_password()
        
        # Sprawdź czy username istnieje
        if User.objects.filter(username=username).exists():
            continue
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='service'
        )
        
        ServiceProfile.objects.create(
            user=user,
            company_name=company_name,
            email=email,
            phone=f"+48 {random.randint(100,999)}-{random.randint(100,999)}-{random.randint(100,999)}",
            city=city,
            postal_code=generate_postal_code(city_idx),
            voivodeship=voivodeship,
            is_verified=random.choice([True, False]),
            description=f"Profesjonalny serwis RTV i AGD. Działamy od {random.randint(1990, 2020)} roku.",
        )
        
        created_services += 1
        
        if (created_services + 1) % 25 == 0:
            print(f"  Utworzono {created_services} serwisów...")
    
    print(f"\nUtworzono {created_services} serwisów.")
    
    # Statystyki
    print("\nStatystyki:")
    print(f"  Łącznie użytkowników: {User.objects.count()}")
    print(f"  Klientów: {User.objects.filter(role='client').count()}")
    print(f"  Serwisów: {User.objects.filter(role='service').count()}")
    print(f"  Administratorów: {User.objects.filter(role='admin').count()}")

if __name__ == '__main__':
    main()
