from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Niestandardowy model użytkownika z rolami"""
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('client', 'Klient'),
        ('service', 'Serwis'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='client', db_column='rola')
    phone = models.CharField(max_length=20, blank=True, null=True, db_column='telefon')
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')

    class Meta:
        verbose_name = 'Użytkownik'
        verbose_name_plural = 'Użytkownicy'
        db_table = 'uzytkownicy'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def unread_notifications_count(self):
        """Liczba nieprzeczytanych powiadomień"""
        return self.notifications.filter(is_read=False).count()


class ClientProfile(models.Model):
    """Profil klienta - osoba zgłaszająca usterkę"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile', db_column='uzytkownik_id')
    first_name = models.CharField(max_length=100, db_column='imie')
    last_name = models.CharField(max_length=100, db_column='nazwisko')
    email = models.EmailField(db_column='email')
    phone = models.CharField(max_length=20, db_column='telefon')
    address = models.TextField(blank=True, db_column='adres')
    city = models.CharField(max_length=100, db_column='miasto')
    postal_code = models.CharField(max_length=10, db_column='kod_pocztowy')
    voivodeship = models.CharField(max_length=100, blank=True, db_column='wojewodztwo')
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    updated_at = models.DateTimeField(auto_now=True, db_column='data_aktualizacji')

    class Meta:
        verbose_name = 'Klient'
        verbose_name_plural = 'Klienci'
        db_table = 'klienci'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ServiceProfile(models.Model):
    """Profil serwisu - firma lub osoba naprawiająca"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='service_profile', db_column='uzytkownik_id')
    company_name = models.CharField(max_length=200, db_column='nazwa_firmy')
    nip = models.CharField(max_length=20, blank=True, db_column='nip')
    email = models.EmailField(db_column='email')
    phone = models.CharField(max_length=20, db_column='telefon')
    address = models.TextField(db_column='adres')
    city = models.CharField(max_length=100, db_column='miasto')
    postal_code = models.CharField(max_length=10, db_column='kod_pocztowy')
    voivodeship = models.CharField(max_length=100, db_column='wojewodztwo')
    description = models.TextField(blank=True, db_column='opis')
    specializes_in = models.CharField(max_length=500, blank=True, help_text="Specjalizacje, np. TV, Smartfony, Tablety", db_column='specjalizacje')
    is_verified = models.BooleanField(default=False, db_column='czy_zweryfikowany')
    is_active = models.BooleanField(default=True, db_column='czy_aktywny')
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    updated_at = models.DateTimeField(auto_now=True, db_column='data_aktualizacji')

    class Meta:
        verbose_name = 'Serwis'
        verbose_name_plural = 'Serwisy'
        db_table = 'serwisy'

    def __str__(self):
        return self.company_name
    
    def average_rating(self):
        """Średnia ocena serwisu"""
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return 0


class Notification(models.Model):
    """Powiadomienia dla użytkowników"""
    TYPE_CHOICES = (
        ('info', 'Informacja'),
        ('warning', 'Ostrzeżenie'),
        ('success', 'Sukces'),
        ('error', 'Błąd'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', db_column='uzytkownik_id')
    title = models.CharField(max_length=200, db_column='tytul')
    message = models.TextField(db_column='tresc')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='info', db_column='typ')
    link = models.URLField(blank=True, help_text="Opcjonalny link do szczególow", db_column='link')
    is_read = models.BooleanField(default=False, db_column='czy_przeczytane')
    created_at = models.DateTimeField(auto_now_add=True, db_column='data_utworzenia')
    
    class Meta:
        verbose_name = 'Powiadomienie'
        verbose_name_plural = 'Powiadomienia'
        ordering = ['-created_at']
        db_table = 'powiadomienia'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    @classmethod
    def create_notification(cls, user, title, message, type='info', link=''):
        """Utwórz powiadomienie dla użytkownika"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            type=type,
            link=link
        )
