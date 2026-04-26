import os
import django
import random
from datetime import timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serwisRTV.settings')
django.setup()

from users.models import ClientProfile, ServiceProfile, User
from zgloszenia.models import ServiceRequest, ServiceOffer, Payment
from django.utils import timezone

def main():
    print("Ładowanie danych...")
    
    # Najpierw utwórz oferty dla zgłoszeń in_progress i completed które nie mają ofert
    requests_no_offers = ServiceRequest.objects.filter(
        status__in=['in_progress', 'completed']
    )
    
    services = list(ServiceProfile.objects.all())
    if not services:
        print("Brak serwisów!")
        return
    
    offers_created = 0
    print("Tworzenie ofert dla zgłoszeń...")
    
    for request in requests_no_offers:
        # Sprawdź czy ma już ofertę
        if ServiceOffer.objects.filter(service_request=request).exists():
            continue
        
        # Utwórz ofertę
        service = random.choice(services)
        price = Decimal(random.choice([100, 150, 200, 250, 300, 400, 500, 600, 800]))
        
        offer = ServiceOffer.objects.create(
            service_request=request,
            service=service,
            price=price,
            estimated_time=f"{random.randint(1, 14)} dni",
            message="Oferta wygenerowana automatycznie",
            status='accepted' if request.status == 'in_progress' else 'accepted',
        )
        offers_created += 1
    
    print(f"Utworzono {offers_created} ofert")
    
    # Teraz utwórz płatności
    requests_ids = ServiceOffer.objects.values_list('service_request_id', flat=True)
    requests = ServiceRequest.objects.filter(id__in=requests_ids, status__in=['in_progress', 'completed'])
    
    print(f"\nZnaleziono {requests.count()} zgłoszeń z ofertami (in_progress/completed)")
    
    created_count = 0
    
    print("\nGenerowanie płatności...")
    
    for request in requests:
        # Sprawdź czy już istnieje płatność
        if Payment.objects.filter(service_request=request).exists():
            continue
        
        # Pobierz zaakceptowaną ofertę
        offer = ServiceOffer.objects.filter(service_request=request, status='accepted').first()
        if not offer:
            offer = ServiceOffer.objects.filter(service_request=request).first()
        
        if not offer:
            continue
        
        # Losowy status płatności
        status_choices = ['pending', 'paid', 'paid_to_admin', 'released']
        status_weights = [10, 30, 40, 20]
        status = random.choices(status_choices, weights=status_weights)[0]
        
        admin_fee = offer.price * Decimal('0.1')
        final_amount = offer.price - admin_fee
        
        # Zawsze ustaw transaction_id (MySQL nie pozwala na NULL)
        transaction_id = f"TXN{random.randint(1000000, 9999999)}"
        
        # Utwórz płatność
        payment = Payment.objects.create(
            service_request=request,
            service_offer=offer,
            amount=offer.price,
            admin_fee=admin_fee,
            final_amount=final_amount,
            status=status,
            payment_method=random.choice(['bank_transfer', 'card', 'blik']),
            transaction_id=transaction_id,
        )
        
        # Ustaw paid_at dla opłaconych
        if status != 'pending':
            payment.paid_at = timezone.now() - timedelta(days=random.randint(0, 30))
            if status == 'released':
                payment.released_at = timezone.now() - timedelta(days=random.randint(0, 20))
            payment.save(update_fields=['paid_at', 'released_at'])
        
        created_count += 1
        
        if created_count % 10 == 0:
            print(f"  Utworzono {created_count} płatności...")
    
    print(f"\nGotowe! Utworzono {created_count} płatności.")
    
    # Statystyki
    print("\nStatystyki płatności:")
    for status_key, status_label in Payment.STATUS_CHOICES:
        count = Payment.objects.filter(status=status_key).count()
        print(f"  {status_label}: {count}")

if __name__ == '__main__':
    main()
