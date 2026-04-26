from django import forms
from .models import ServiceRequest, ServiceOffer, Message, DeviceCategory, DeviceType, Payment


class ServiceRequestForm(forms.ModelForm):
    """Formularz zgłoszenia naprawy"""
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'device_category', 'device_type',
            'device_brand', 'device_model', 'serial_number', 'purchase_date',
            'warranty_status', 'priority', 'voivodeship', 'city', 'postal_code',
            'address', 'is_mobile_service', 'estimated_budget'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Opisz szczegółowo usterkę...'}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Jeśli wybrano kategorię, filtruj typy urządzeń
        if self.instance.pk and self.instance.device_category:
            self.fields['device_type'].queryset = DeviceType.objects.filter(
                category=self.instance.device_category
            )
        else:
            self.fields['device_type'].queryset = DeviceType.objects.none()


class ServiceOfferForm(forms.ModelForm):
    """Formularz oferty serwisu"""
    class Meta:
        model = ServiceOffer
        fields = ['price', 'estimated_time', 'warranty_period', 'message', 'additional_info']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Wiadomość do klienta...'}),
            'additional_info': forms.Textarea(attrs={'rows': 3}),
        }


class MessageForm(forms.ModelForm):
    """Formularz wiadomości"""
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Napisz wiadomość...'}),
        }


class ServiceRequestFilterForm(forms.Form):
    """Formularz filtrowania zgłoszeń dla serwisów"""
    VOIVODESHIP_CHOICES = [
        ('', 'Cała Polska'),
        ('dolnoslaskie', 'Dolnośląskie'),
        ('kujawsko-pomorskie', 'Kujawsko-pomorskie'),
        ('lubelskie', 'Lubelskie'),
        ('lubuskie', 'Lubuskie'),
        ('lodzkie', 'Łódzkie'),
        ('malopolskie', 'Małopolskie'),
        ('mazowieckie', 'Mazowieckie'),
        ('opolskie', 'Opolskie'),
        ('podkarpackie', 'Podkarpackie'),
        ('podlaskie', 'Podlaskie'),
        ('pomorskie', 'Pomorskie'),
        ('slaskie', 'Śląskie'),
        ('swietokrzyskie', 'Świętokrzyskie'),
        ('warminsko-mazurskie', 'Warmińsko-mazurskie'),
        ('wielkopolskie', 'Wielkopolskie'),
        ('zachodniopomorskie', 'Zachodniopomorskie'),
    ]
    
    voivodeship = forms.ChoiceField(choices=VOIVODESHIP_CHOICES, required=False)
    device_category = forms.ModelChoiceField(queryset=DeviceCategory.objects.all(), required=False, empty_label='Wszystkie kategorie')
    status = forms.ChoiceField(choices=[('', 'Wszystkie')] + list(ServiceRequest.STATUS_CHOICES), required=False)


class PaymentForm(forms.ModelForm):
    """Formularz płatności escrow"""
    class Meta:
        model = Payment
        fields = ['payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(),
        }


class PaymentReleaseForm(forms.Form):
    """Formularz zatwierdzania wypłaty dla administratora"""
    admin_fee_percentage = forms.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        initial=10, 
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100'})
    )
    admin_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label='Notatki administratora'
    )
