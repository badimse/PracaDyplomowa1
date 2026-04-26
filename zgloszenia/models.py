from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import ClientProfile, ServiceProfile


class DeviceCategory(models.Model):
    """Kategorie urządzeń"""
    name = models.CharField(max_length=100, db_column='nazwa')
    slug = models.SlugField(unique=True, db_column='slug')
    
    class Meta:
        verbose_name = 'Kategoria urządzenia'
        verbose_name_plural = 'Kategorie urządzeń'
        ordering = ['name']
        db_table = 'kategorie_urzadzen'

    def __str__(self):
        return self.name


class DeviceType(models.Model):
    """Typy urządzeń"""
    category = models.ForeignKey(DeviceCategory, on_delete=models.CASCADE, related_name='device_types', db_column='kategoria_id')
    name = models.CharField(max_length=100, db_column='nazwa')
    slug = models.SlugField(unique=True, db_column='slug')
    
    class Meta:
        verbose_name = 'Typ urządzenia'
        verbose_name_plural = 'Typy urządzeń'
        ordering = ['name']
        db_table = 'typy_urzadzen'

    def __str__(self):
        return f"{self.category.name} - {self.name}"


class ServiceRequest(models.Model):
    """Zgłoszenie naprawy"""
    STATUS_CHOICES = (
        ('draft', 'Szkic'),
        ('submitted', 'Zgłoszone'),
        ('viewed_by_services', 'Wyświetlone przez serwisy'),
        ('offers_received', 'Otrzymano oferty'),
        ('in_progress', 'W naprawie'),
        ('completed', 'Zakończone'),
        ('cancelled', 'Anulowane'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Niski'),
        ('normal', 'Normalny'),
        ('high', 'Wysoki'),
        ('urgent', 'Pilny'),
    )
    
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='service_requests', db_column='klient_id')
    title = models.CharField(max_length=200, db_column='tytul')
    description = models.TextField(help_text="Opis usterki", db_column='opis')
    device_category = models.ForeignKey(DeviceCategory, on_delete=models.SET_NULL, null=True, db_column='kategoria_urzadzenia_id')
    device_type = models.ForeignKey(DeviceType, on_delete=models.SET_NULL, null=True, blank=True, db_column='typ_urzadzenia_id')
    device_brand = models.CharField(max_length=100, db_column='marka_urzadzenia')
    device_model = models.CharField(max_length=100, blank=True, db_column='model_urzadzenia')
    serial_number = models.CharField(max_length=100, blank=True, db_column='numer_seryjny')
    purchase_date = models.DateField(null=True, blank=True, db_column='data_zakupu')
    warranty_status = models.BooleanField(default=False, help_text="Czy urządzenie jest na gwarancji?", db_column='czy_gwarancja')
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', db_column='priorytet')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_column='status')
    
    # Lokalizacja - możliwość filtrowania po województwie
    voivodeship = models.CharField(max_length=100, help_text="Województwo - dla filtrowania serwisów", db_column='wojewodztwo')
    city = models.CharField(max_length=100, db_column='miasto')
    postal_code = models.CharField(max_length=10, db_column='kod_pocztowy')
    address = models.TextField(blank=True, db_column='adres')
    
    # Czy serwis ma dojechać do klienta
    is_mobile_service = models.BooleanField(default=False, help_text="Czy serwis ma dojechać do klienta?", db_column='czy_serwis_mobile')
    
    # Zdjęcia usterki
    photos = models.JSONField(default=list, blank=True, help_text="Lista URL do zdjęć", db_column='zdjecia')
    
    # Cena orientacyjna podana przez klienta
    estimated_budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='szacowany_budzet')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    updated_at = models.DateTimeField(auto_now=True, db_column='data_aktualizacji')
    submitted_at = models.DateTimeField(null=True, blank=True, db_column='data_zgloszenia')
    completed_at = models.DateTimeField(null=True, blank=True, db_column='data_zakonczenia')
    
    class Meta:
        verbose_name = 'Zgłoszenie naprawy'
        verbose_name_plural = 'Zgłoszenia napraw'
        ordering = ['-created_at']
        db_table = 'zgloszenia_naprawy'

    def __str__(self):
        return f"{self.title} - {self.client}"


class ServiceOffer(models.Model):
    """Oferta od serwisu na naprawę"""
    STATUS_CHOICES = (
        ('pending', 'Oczekująca'),
        ('accepted', 'Zaakceptowana'),
        ('rejected', 'Odrzucona'),
        ('withdrawn', 'Wycofana'),
    )
    
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='offers', db_column='zgloszenie_id')
    service = models.ForeignKey(ServiceProfile, on_delete=models.CASCADE, related_name='offers', db_column='serwis_id')
    
    message = models.TextField(help_text="Wiadomość od serwisu do klienta", db_column='wiadomosc')
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='cena')
    estimated_time = models.CharField(max_length=100, help_text="Szacowany czas naprawy", db_column='szacowany_czas')
    warranty_period = models.CharField(max_length=100, blank=True, help_text="Okres gwarancji na naprawę", db_column='okres_gwarancji')
    additional_info = models.TextField(blank=True, db_column='dodatkowe_info')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_column='status')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    updated_at = models.DateTimeField(auto_now=True, db_column='data_aktualizacji')
    
    class Meta:
        verbose_name = 'Oferta serwisu'
        verbose_name_plural = 'Oferty serwisów'
        ordering = ['-created_at']
        unique_together = ['service_request', 'service']
        db_table = 'oferty_serwisow'

    def __str__(self):
        return f"{self.service.company_name} - {self.price} zł"


class ServiceRequestView(models.Model):
    """Śledzenie kto wyświetlił zgłoszenie"""
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='views', db_column='zgloszenie_id')
    service = models.ForeignKey(ServiceProfile, on_delete=models.CASCADE, db_column='serwis_id')
    viewed_at = models.DateTimeField(auto_now_add=True, db_column='data_wyswietlenia')
    
    class Meta:
        verbose_name = 'Wyświetlenie zgłoszenia'
        verbose_name_plural = 'Wyświetlenia zgłoszeń'
        unique_together = ['service_request', 'service']
        db_table = 'wyswietlenia_zgloszen'


class Message(models.Model):
    """Wiadomości między klientem a serwisem"""
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='messages', db_column='zgloszenie_id')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='nadawca_id')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', db_column='odbiorca_id')
    content = models.TextField(db_column='tresc')
    is_read = models.BooleanField(default=False, db_column='czy_przeczytana')
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    
    class Meta:
        verbose_name = 'Wiadomość'
        verbose_name_plural = 'Wiadomości'
        ordering = ['created_at']
        db_table = 'wiadomosci'

    def __str__(self):
        return f"{self.sender} -> {self.recipient}"


class Review(models.Model):
    """Opinia o serwisie"""
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='review', db_column='zgloszenie_id')
    service = models.ForeignKey(ServiceProfile, on_delete=models.CASCADE, related_name='reviews', db_column='serwis_id')
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='reviews', db_column='klient_id')
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], db_column='ocena')
    comment = models.TextField(blank=True, db_column='komentarz')
    would_recommend = models.BooleanField(default=True, db_column='czy_poleca')
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    
    class Meta:
        verbose_name = 'Opinia'
        verbose_name_plural = 'Opinie'
        db_table = 'opinie'

    def __str__(self):
        return f"{self.client} -> {self.service} ({self.rating}/5)"


class Payment(models.Model):
    """Płatność za naprawę - system escrow"""
    STATUS_CHOICES = (
        ('pending', 'Oczekująca'),
        ('paid_to_admin', 'Opłacone - u administratora'),
        ('released_to_service', 'Wypłacone serwisowi'),
        ('refunded', 'Zwrócone klientowi'),
        ('cancelled', 'Anulowane'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('bank_transfer', 'Przelew bankowy'),
        ('card', 'Karta płatnicza'),
        ('paypal', 'PayPal'),
        ('cash', 'Gotówka'),
    )
    
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='payment', db_column='zgloszenie_id')
    service_offer = models.ForeignKey(ServiceOffer, on_delete=models.CASCADE, related_name='payments', db_column='oferta_id')
    
    # Kwoty
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Kwota naprawy", db_column='kwota')
    admin_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Prowizja administratora", db_column='prowizja')
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Kwota dla serwisu (amount - admin_fee)", db_column='kwota_koncowa')
    
    # Status płatności
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_column='status')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, db_column='metoda_platnosci')
    
    # Daty
    paid_at = models.DateTimeField(null=True, blank=True, help_text="Kiedy klient zapłacił", db_column='data_zaplaty')
    released_at = models.DateTimeField(null=True, blank=True, help_text="Kiedy wypłacono serwisowi", db_column='data_wyplaty')
    refunded_at = models.DateTimeField(null=True, blank=True, help_text="Kiedy zwrócono klientowi", db_column='data_zwrotu')
    
    # Informacje o transakcji
    transaction_id = models.CharField(max_length=100, blank=True, help_text="ID transakcji zewnętrznej", db_column='id_transakcji')
    admin_notes = models.TextField(blank=True, help_text="Notatki administratora", db_column='notatki')
    
    # Kto zatwierdził wypłatę
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='released_payments',
        help_text="Administrator który zatwierdził wypłatę",
        db_column='zatwierdzony_przez_id'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    updated_at = models.DateTimeField(auto_now=True, db_column='data_aktualizacji')
    
    class Meta:
        verbose_name = 'Płatność'
        verbose_name_plural = 'Płatności'
        ordering = ['-created_at']
        db_table = 'platnosci'

    def __str__(self):
        return f"Płatność #{self.pk} - {self.service_request.title} - {self.status}"
    
    def calculate_admin_fee(self, percentage=10):
        """Oblicz prowizję administratora (domyślnie 10%)"""
        self.admin_fee = self.amount * (percentage / 100)
        self.final_amount = self.amount - self.admin_fee
        return self.admin_fee
    
    def mark_as_paid(self, payment_method='bank_transfer', transaction_id=''):
        """Oznacz jako opłacone przez klienta"""
        self.status = 'paid_to_admin'
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.paid_at = timezone.now()
        self.save()
    
    def release_to_service(self, released_by_user):
        """Wypłać pieniądze serwisowi"""
        if self.status != 'paid_to_admin':
            raise ValueError("Płatność musi być najpierw opłacona przez klienta")
        
        self.status = 'released_to_service'
        self.released_at = timezone.now()
        self.released_by = released_by_user
        self.save()
        
        # Powiadom serwis
        from users.models import Notification
        Notification.create_notification(
            user=self.service_offer.service.user,
            title='Wypłata środków',
            message=f'Srodki za naprawę "{self.service_request.title}" zostały wypłacone. Kwota: {self.final_amount} zł',
            type='success',
            link=f'/zgloszenia/{self.service_request.pk}/'
        )
    
    def refund_to_client(self):
        """Zwróć pieniądze klientowi"""
        if self.status != 'paid_to_admin':
            raise ValueError("Można zwrócić tylko płatności opłacone")
        
        self.status = 'refunded'
        self.refunded_at = timezone.now()
        self.save()
        
        # Powiadom klienta
        from users.models import Notification
        Notification.create_notification(
            user=self.service_request.client.user,
            title='Zwrot środków',
            message=f'Srodki za naprawę "{self.service_request.title}" zostały zwrócone. Kwota: {self.amount} zł',
            type='info',
            link=f'/zgloszenia/{self.service_request.pk}/'
        )
