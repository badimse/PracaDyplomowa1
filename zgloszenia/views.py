from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import ServiceRequest, ServiceOffer, Message, DeviceCategory, DeviceType, ServiceRequestView, Review, Payment
from .forms import ServiceRequestForm, ServiceOfferForm, MessageForm, ServiceRequestFilterForm, PaymentForm, PaymentReleaseForm
from users.models import ClientProfile, ServiceProfile, Notification, User


@login_required
def request_create_view(request):
    """Tworzenie nowego zgłoszenia naprawy"""
    if request.user.role != 'client':
        messages.error(request, 'Tylko klient może tworzyć zgłoszenia.')
        return redirect('request_list')
    
    try:
        client_profile = request.user.client_profile
    except ClientProfile.DoesNotExist:
        messages.error(request, 'Najpierw uzupełnij dane profilu.')
        return redirect('profile_edit')
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.client = client_profile
            service_request.save()
            messages.success(request, 'Zgłoszenie zostało utworzone i zapisane jako szkic.')
            return redirect('request_detail', pk=service_request.pk)
    else:
        form = ServiceRequestForm()
    
    return render(request, 'zgloszenia/request_form.html', {'form': form, 'title': 'Nowe zgłoszenie'})


@login_required
def request_list_view(request):
    """Lista zgłoszeń - zależna od roli użytkownika"""
    if request.user.role == 'client':
        # Klient widzi swoje zgłoszenia
        try:
            client_profile = request.user.client_profile
            requests = ServiceRequest.objects.filter(client=client_profile).order_by('-created_at')
        except ClientProfile.DoesNotExist:
            requests = ServiceRequest.objects.none()
        
        # Statystyki dla klienta
        stats = {
            'total': client_profile.service_requests.count() if hasattr(client_profile, 'service_requests') else 0,
            'draft': client_profile.service_requests.filter(status='draft').count() if hasattr(client_profile, 'service_requests') else 0,
            'submitted': client_profile.service_requests.filter(status='submitted').count() if hasattr(client_profile, 'service_requests') else 0,
            'in_progress': client_profile.service_requests.filter(status='in_progress').count() if hasattr(client_profile, 'service_requests') else 0,
            'completed': client_profile.service_requests.filter(status='completed').count() if hasattr(client_profile, 'service_requests') else 0,
        }
        
        context = {
            'requests': requests,
            'title': 'Moje zgłoszenia',
            'is_client': True,
            'stats': stats,
        }
    
    elif request.user.role == 'service':
        # Serwis widzi dostępne zgłoszenia z filtrowaniem
        try:
            service_profile = request.user.service_profile
        except ServiceProfile.DoesNotExist:
            messages.error(request, 'Najpierw uzupełnij dane serwisu.')
            return redirect('profile_edit')
        
        # Zgłoszenia, na które serwis nie złożył oferty
        offered_ids = ServiceOffer.objects.filter(service=service_profile).values_list('service_request_id', flat=True)
        requests = ServiceRequest.objects.filter(
            status__in=['submitted', 'viewed_by_services', 'offers_received']
        ).exclude(id__in=offered_ids)
        
        # Filtrowanie
        form = ServiceRequestFilterForm(request.GET or None)
        if form.is_valid():
            voivodeship = form.cleaned_data.get('voivodeship')
            device_category = form.cleaned_data.get('device_category')
            status = form.cleaned_data.get('status')
            
            if voivodeship:
                requests = requests.filter(voivodeship=voivodeship)
            if device_category:
                requests = requests.filter(device_category=device_category)
            if status:
                requests = requests.filter(status=status)
        
        paginator = Paginator(requests, 20)
        page = request.GET.get('page')
        requests = paginator.get_page(page)
        
        context = {
            'requests': requests,
            'title': 'Dostępne zgłoszenia',
            'filter_form': form,
            'is_service': True,
        }
    
    else:
        # Administrator widzi wszystkie
        requests = ServiceRequest.objects.all().select_related('payment').order_by('-created_at')
        
        # Filtrowanie dla administratora
        device_category = request.GET.get('device_category', '')
        priority = request.GET.get('priority', '')
        status = request.GET.get('status', '')
        payment_status = request.GET.get('payment_status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if device_category:
            requests = requests.filter(device_category_id=device_category)
        if priority:
            requests = requests.filter(priority=priority)
        if status:
            requests = requests.filter(status=status)
        if payment_status:
            if payment_status == 'no_payment':
                requests = requests.filter(payment__isnull=True)
            else:
                requests = requests.filter(payment__status=payment_status)
        if date_from:
            requests = requests.filter(created_at__date__gte=date_from)
        if date_to:
            requests = requests.filter(created_at__date__lte=date_to)
        
        # Pobierz kategorie do filtra
        categories = DeviceCategory.objects.all()
        
        paginator = Paginator(requests, 50)
        page = request.GET.get('page')
        requests = paginator.get_page(page)
        
        context = {
            'requests': requests,
            'title': 'Wszystkie zgłoszenia',
            'is_admin': True,
            'categories': categories,
            'filter_device_category': device_category,
            'filter_priority': priority,
            'filter_status': status,
            'filter_payment_status': payment_status,
            'filter_date_from': date_from,
            'filter_date_to': date_to,
        }
    
    return render(request, 'zgloszenia/request_list.html', context)


@login_required
def request_detail_view(request, pk):
    """Szczegóły zgłoszenia"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    # Sprawdzanie uprawnień
    can_view = False
    can_offer = False
    
    if request.user.role == 'client' and service_request.client.user == request.user:
        can_view = True
    elif request.user.role == 'service':
        try:
            service_profile = request.user.service_profile
            can_view = True
            can_offer = not ServiceOffer.objects.filter(
                service_request=service_request, 
                service=service_profile
            ).exists()
            
            # Zarejestruj wyświetlenie
            ServiceRequestView.objects.get_or_create(
                service_request=service_request,
                service=service_profile
            )
        except ServiceProfile.DoesNotExist:
            pass
    elif request.user.role == 'admin':
        can_view = True
    
    if not can_view:
        messages.error(request, 'Brak uprawnień do wyświetlenia tego zgłoszenia.')
        return redirect('request_list')
    
    # Pobierz oferty
    offers = ServiceOffer.objects.filter(service_request=service_request).select_related('service')
    
    # Wiadomości
    chat_messages = Message.objects.filter(
        service_request=service_request
    ).select_related('sender').order_by('created_at')
    
    # Sprawdź czy istnieje opinia
    has_review = Review.objects.filter(service_request=service_request).exists()
    
    context = {
        'service_request': service_request,
        'offers': offers,
        'chat_messages': chat_messages,
        'can_offer': can_offer,
        'has_review': has_review,
    }
    
    return render(request, 'zgloszenia/request_detail.html', context)


@login_required
def request_submit_view(request, pk):
    """Zatwierdzenie zgłoszenia i wysłanie do serwisów"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    if request.user.role != 'client' or service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_list')
    
    if service_request.status != 'draft':
        messages.error(request, 'Zgłoszenie zostało już zatwierdzone.')
        return redirect('request_detail', pk=pk)
    
    # Walidacja - sprawdź czy wymagane pola są wypełnione
    if not service_request.title or not service_request.description:
        messages.error(request, 'Zgłoszenie musi mieć tytuł i opis usterki.')
        return redirect('request_detail', pk=pk)
    
    service_request.status = 'submitted'
    service_request.submitted_at = timezone.now()
    service_request.save()
    
    messages.success(request, 'Zgłoszenie zostało opublikowane i wysłane do serwisów.')
    return redirect('request_detail', pk=pk)


@login_required
def request_cancel_view(request, pk):
    """Anulowanie zgłoszenia"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    if request.user.role != 'client' or service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_list')
    
    if service_request.status in ['completed', 'cancelled']:
        messages.error(request, 'Nie można anulować tego zgłoszenia.')
        return redirect('request_detail', pk=pk)
    
    # Jeśli są oferty, poinformuj serwisy
    if service_request.offers.exists():
        # Można dodać wysyłanie powiadomień
        pass
    
    service_request.status = 'cancelled'
    service_request.save()
    
    messages.success(request, 'Zgłoszenie zostało anulowane.')
    return redirect('request_list')


@login_required
def offer_create_view(request, request_pk):
    """Składanie oferty przez serwis"""
    service_request = get_object_or_404(ServiceRequest, pk=request_pk)
    
    if request.user.role != 'service':
        messages.error(request, 'Tylko serwis może składać oferty.')
        return redirect('request_detail', pk=request_pk)
    
    try:
        service_profile = request.user.service_profile
    except ServiceProfile.DoesNotExist:
        messages.error(request, 'Najpierw uzupełnij dane serwisu.')
        return redirect('profile_edit')
    
    if ServiceOffer.objects.filter(service_request=service_request, service=service_profile).exists():
        messages.error(request, 'Już złożyłeś ofertę dla tego zgłoszenia.')
        return redirect('request_detail', pk=request_pk)
    
    if request.method == 'POST':
        form = ServiceOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.service_request = service_request
            offer.service = service_profile
            offer.save()
            
            # Aktualizuj status zgłoszenia
            service_request.status = 'offers_received'
            service_request.save()
            
            # Powiadomienie dla klienta
            Notification.create_notification(
                user=service_request.client.user,
                title='Nowa oferta naprawy',
                message=f'Serwis {service_profile.company_name} złożył ofertę na naprawę: {service_request.title}',
                type='info',
                link=f'/zgloszenia/{service_request.pk}/'
            )
            
            messages.success(request, 'Oferta została wysłana do klienta.')
            return redirect('request_detail', pk=request_pk)
    else:
        form = ServiceOfferForm()
    
    return render(request, 'zgloszenia/offer_form.html', {'form': form, 'service_request': service_request})


@login_required
def offer_accept_view(request, pk):
    """Akceptacja oferty przez klienta"""
    offer = get_object_or_404(ServiceOffer, pk=pk)
    
    if request.user.role != 'client' or offer.service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_detail', pk=offer.service_request.pk)
    
    offer.status = 'accepted'
    offer.save()
    
    # Odrzuć pozostałe oferty
    ServiceOffer.objects.filter(
        service_request=offer.service_request
    ).exclude(pk=pk).update(status='rejected')
    
    offer.service_request.status = 'in_progress'
    offer.service_request.save()
    
    messages.success(request, 'Oferta została zaakceptowana. Serwis został powiadomiony.')
    return redirect('request_detail', pk=offer.service_request.pk)


@login_required
def offer_reject_view(request, pk):
    """Odrzucenie oferty przez klienta"""
    offer = get_object_or_404(ServiceOffer, pk=pk)
    
    if request.user.role != 'client' or offer.service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_detail', pk=offer.service_request.pk)
    
    offer.status = 'rejected'
    offer.save()
    
    messages.success(request, 'Oferta została odrzucona.')
    return redirect('request_detail', pk=offer.service_request.pk)


@login_required
def request_complete_view(request, pk):
    """Zakończenie naprawy"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    # Tylko serwis lub klient może zakończyć
    can_complete = False
    if request.user.role == 'client' and service_request.client.user == request.user:
        can_complete = True
    elif request.user.role == 'service':
        try:
            service_profile = request.user.service_profile
            if ServiceOffer.objects.filter(
                service_request=service_request, 
                service=service_profile,
                status='accepted'
            ).exists():
                can_complete = True
        except ServiceProfile.DoesNotExist:
            pass
    
    if not can_complete:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_detail', pk=pk)
    
    service_request.status = 'completed'
    service_request.completed_at = timezone.now()
    service_request.save()
    
    messages.success(request, 'Naprawa została zakończona. Możesz dodać opinię o serwisie.')
    return redirect('request_detail', pk=pk)


@login_required
def review_create_view(request, request_pk):
    """Dodanie opinii o serwisie"""
    service_request = get_object_or_404(ServiceRequest, pk=request_pk)
    
    if request.user.role != 'client' or service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_detail', pk=request_pk)
    
    if service_request.status != 'completed':
        messages.error(request, 'Możesz dodać opinię dopiero po zakończeniu naprawy.')
        return redirect('request_detail', pk=request_pk)
    
    if Review.objects.filter(service_request=service_request).exists():
        messages.error(request, 'Już dodałeś opinię dla tego zgłoszenia.')
        return redirect('request_detail', pk=request_pk)
    
    try:
        service_profile = service_request.offers.filter(status='accepted').first().service
    except:
        messages.error(request, 'Nie znaleziono serwisu dla tego zgłoszenia.')
        return redirect('request_detail', pk=request_pk)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        would_recommend = request.POST.get('would_recommend') == 'on'
        
        if not rating or not rating.isdigit():
            messages.error(request, 'Wybierz ocenę.')
            return redirect('review_create', request_pk=request_pk)
        
        Review.objects.create(
            service_request=service_request,
            service=service_profile,
            client=request.user.client_profile,
            rating=int(rating),
            comment=comment,
            would_recommend=would_recommend
        )
        
        messages.success(request, 'Opinia została dodana. Dziękujemy!')
        return redirect('request_detail', pk=request_pk)
    
    return render(request, 'zgloszenia/review_form.html', {'service_request': service_request})


@login_required
def message_send_view(request, pk):
    """Wysłanie wiadomości w ramach zgłoszenia"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Najpierw ustal odbiorcę
            recipient = None
            
            if request.user.role == 'client':
                # Klient wysyła do serwisu
                try:
                    offer = service_request.offers.filter(status='accepted').first()
                    if offer:
                        recipient = offer.service.user
                    else:
                        messages.error(request, 'Brak aktywnego serwisu dla tego zgłoszenia.')
                        return redirect('request_detail', pk=pk)
                except Exception as e:
                    messages.error(request, f'Błąd podczas wysyłania wiadomości: {str(e)}')
                    return redirect('request_detail', pk=pk)
            else:
                # Serwis wysyła do klienta
                recipient = service_request.client.user
            
            # Utwórz wiadomość z odbiorcą
            message = Message.objects.create(
                service_request=service_request,
                sender=request.user,
                recipient=recipient,
                content=content
            )
            
            # Utwórz powiadomienie
            if request.user.role == 'client':
                Notification.create_notification(
                    user=recipient,
                    title='Nowa wiadomość',
                    message=f'Klient {request.user.username} wysłał wiadomość w zgłoszeniu: {service_request.title}',
                    type='info',
                    link=f'/zgloszenia/{service_request.pk}/'
                )
                messages.success(request, 'Wiadomość została wysłana do serwisu.')
            else:
                Notification.create_notification(
                    user=recipient,
                    title='Nowa wiadomość od serwisu',
                    message=f'Serwis {request.user.username} wysłał wiadomość w zgłoszeniu: {service_request.title}',
                    type='info',
                    link=f'/zgloszenia/{service_request.pk}/'
                )
                messages.success(request, 'Wiadomość została wysłana do klienta.')
            
            return redirect('request_detail', pk=pk)
    
    return redirect('request_detail', pk=pk)


# ===== API VIEWS =====

# ===== PAYMENT ESCROW VIEWS =====

@login_required
def payment_create_view(request, offer_pk):
    """Tworzenie płatności escrow po akceptacji oferty przez klienta"""
    offer = get_object_or_404(ServiceOffer, pk=offer_pk)
    
    if request.user.role != 'client' or offer.service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_detail', pk=offer.service_request.pk)
    
    if offer.status != 'accepted':
        messages.error(request, 'Możesz utworzyć płatność tylko dla zaakceptowanej oferty.')
        return redirect('request_detail', pk=offer.service_request.pk)
    
    # Sprawdź czy płatność już istnieje
    if hasattr(offer.service_request, 'payment'):
        messages.info(request, 'Płatność dla tego zgłoszenia już istnieje.')
        return redirect('payment_detail', pk=offer.service_request.payment.pk)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.service_request = offer.service_request
            payment.service_offer = offer
            payment.amount = offer.price
            payment.calculate_admin_fee(percentage=10)  # 10% prowizji
            payment.final_amount = payment.amount - payment.admin_fee
            payment.save()
            
            # Automatycznie oznacz jako opłaconą
            transaction_id = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{payment.pk}"
            payment.mark_as_paid(
                payment_method=payment.payment_method or 'bank_transfer',
                transaction_id=transaction_id
            )
            
            # Powiadomienie dla serwisu
            Notification.create_notification(
                user=offer.service.user,
                title='Otrzymano płatność escrow',
                message=f'Klient dokonał płatności escrow za naprawę: {offer.service_request.title}. Kwota: {payment.amount} zł. Środki są zabezpieczone.',
                type='success',
                link=f'/platnosci/{payment.pk}/'
            )
            
            messages.success(request, f'Płatność została dokonana! Kwota {payment.amount} zł jest teraz zabezpieczona w systemie escrow do czasu zakończenia naprawy.')
            return redirect('payment_detail', pk=payment.pk)
    else:
        form = PaymentForm()
    
    admin_fee_val = float(offer.price) * 0.10
    final_amount_val = float(offer.price) * 0.90
    
    return render(request, 'zgloszenia/payment_create.html', {
        'form': form,
        'offer': offer,
        'payment_amount': float(offer.price),
        'admin_fee': admin_fee_val,
        'final_amount': final_amount_val,
    })


@login_required
def payment_process_view(request, pk):
    """Proces płatności - symulacja płatności przez klienta"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.user.role != 'client' or payment.service_request.client.user != request.user:
        messages.error(request, 'Brak uprawnień.')
        return redirect('request_list')
    
    if payment.status != 'pending':
        messages.info(request, f'Płatność jest już w statusie: {payment.get_status_display()}.')
        return redirect('payment_detail', pk=payment.pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'pay':
            transaction_id = f"TXN-{timezone.now().strftime('%Y%m%d%H%M%S')}-{payment.pk}"
            payment.mark_as_paid(
                payment_method=payment.payment_method or 'bank_transfer',
                transaction_id=transaction_id
            )
            
            # Powiadomienia
            Notification.create_notification(
                user=payment.service_offer.service.user,
                title='Klient dokonał płatności',
                message=f'Klient dokonał płatności za naprawę: {payment.service_request.title}. Środki są zabezpieczone w escrow.',
                type='success',
                link=f'/platnosci/{payment.pk}/'
            )
            
            messages.success(request, 'Płatność została zrealizowana. Środki są zabezpieczone w systemie escrow.')
            return redirect('payment_detail', pk=payment.pk)
        
        elif action == 'cancel':
            payment.status = 'cancelled'
            payment.save()
            messages.info(request, 'Płatność została anulowana.')
            return redirect('request_detail', pk=payment.service_request.pk)
    
    return render(request, 'zgloszenia/payment_process.html', {'payment': payment})


@login_required
def payment_detail_view(request, pk):
    """Szczegóły płatności escrow"""
    payment = get_object_or_404(Payment, pk=pk)
    
    # Sprawdzenie uprawnień
    can_view = False
    if request.user.role == 'client' and payment.service_request.client.user == request.user:
        can_view = True
    elif request.user.role == 'service' and payment.service_offer.service.user == request.user:
        can_view = True
    elif request.user.role == 'admin':
        can_view = True
    
    if not can_view:
        messages.error(request, 'Brak uprawnień do wyświetlenia tej płatności.')
        return redirect('request_list')
    
    context = {
        'payment': payment,
        'can_release': request.user.role == 'admin' and payment.status == 'paid_to_admin',
    }
    
    return render(request, 'zgloszenia/payment_detail.html', context)


@login_required
def payment_release_view(request, pk):
    """Wypłata środków serwisowi - tylko administrator"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.user.role != 'admin':
        messages.error(request, 'Tylko administrator może wypłacić środki.')
        return redirect('payment_detail', pk=pk)
    
    if payment.status != 'paid_to_admin':
        messages.error(request, 'Płatność musi być najpierw opłacona przez klienta.')
        return redirect('payment_detail', pk=pk)
    
    if request.method == 'POST':
        form = PaymentReleaseForm(request.POST)
        if form.is_valid():
            admin_fee_percentage = form.cleaned_data.get('admin_fee_percentage')
            admin_notes = form.cleaned_data.get('admin_notes')
            
            # Przelicz prowizję jeśli zmieniono
            if admin_fee_percentage != 10:
                from decimal import Decimal
                payment.admin_fee = payment.amount * (Decimal(admin_fee_percentage) / Decimal('100'))
                payment.final_amount = payment.amount - payment.admin_fee
            
            payment.admin_notes = admin_notes
            payment.save()
            
            # Wypłać środki
            payment.release_to_service(released_by_user=request.user)
            
            messages.success(request, f'Środki zostały wypłacone serwisowi. Kwota: {payment.final_amount} zł')
            return redirect('payment_detail', pk=pk)
    else:
        form = PaymentReleaseForm(initial={'admin_fee_percentage': 10})
    
    return render(request, 'zgloszenia/payment_release.html', {
        'payment': payment,
        'form': form,
    })


@login_required
def payment_refund_view(request, pk):
    """Zwrot środków klientowi - tylko administrator"""
    payment = get_object_or_404(Payment, pk=pk)
    
    if request.user.role != 'admin':
        messages.error(request, 'Tylko administrator może zwrócić środki.')
        return redirect('payment_detail', pk=pk)
    
    if payment.status != 'paid_to_admin':
        messages.error(request, 'Można zwrócić tylko płatności opłacone.')
        return redirect('payment_detail', pk=pk)
    
    if request.method == 'POST':
        payment.refund_to_client()
        messages.success(request, f'Środki zostały zwrócone klientowi. Kwota: {payment.amount} zł')
        return redirect('payment_detail', pk=pk)
    
    return render(request, 'zgloszenia/payment_refund.html', {'payment': payment})


@login_required
def payment_admin_list_view(request):
    """Panel administratora do zarządzania płatnościami"""
    if request.user.role != 'admin':
        messages.error(request, 'Brak uprawnień.')
        return redirect('dashboard')
    
    payments = Payment.objects.all().select_related('service_request', 'service_offer__service').order_by('-created_at')
    
    # Filtrowanie
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    if status_filter:
        payments = payments.filter(status=status_filter)
    if search_query:
        payments = payments.filter(
            Q(service_request__title__icontains=search_query) |
            Q(service_offer__service__company_name__icontains=search_query)
        )
    if date_from:
        payments = payments.filter(created_at__date__gte=date_from)
    if date_to:
        payments = payments.filter(created_at__date__lte=date_to)
    
    # Statystyki
    payments_pending = Payment.objects.filter(status='pending').count()
    payments_held = Payment.objects.filter(status='paid_to_admin').count()
    payments_released = Payment.objects.filter(status='released').count()
    payments_refunded = Payment.objects.filter(status='refunded').count()
    
    # Suma kwot
    total_amount = Payment.objects.aggregate(total=Count('amount'))['total']
    
    paginator = Paginator(payments, 20)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
        'payments_pending': payments_pending,
        'payments_held': payments_held,
        'payments_released': payments_released,
        'payments_refunded': payments_refunded,
        'total_amount': sum(p.amount for p in Payment.objects.all()),
        'filter_status': status_filter,
        'search_query': search_query,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
    }
    
    return render(request, 'zgloszenia/payment_admin_list.html', context)


@login_required
def payment_list_view(request):
    """Lista płatności - zależna od roli użytkownika"""
    if request.user.role == 'client':
        try:
            client_profile = request.user.client_profile
            payments = Payment.objects.filter(
                service_request__client=client_profile
            ).order_by('-created_at')
        except ClientProfile.DoesNotExist:
            payments = Payment.objects.none()
        
        context = {
            'payments': payments,
            'title': 'Moje płatności',
            'is_client': True,
        }
    
    elif request.user.role == 'service':
        try:
            service_profile = request.user.service_profile
            payments = Payment.objects.filter(
                service_offer__service=service_profile
            ).order_by('-created_at')
        except ServiceProfile.DoesNotExist:
            payments = Payment.objects.none()
        
        context = {
            'payments': payments,
            'title': 'Płatności za naprawy',
            'is_service': True,
        }
    
    else:
        # Administrator widzi wszystkie
        payments = Payment.objects.all().order_by('-created_at')
        context = {
            'payments': payments,
            'title': 'Wszystkie płatności',
            'is_admin': True,
        }
    
    return render(request, 'zgloszenia/payment_list.html', context)


@login_required
@require_http_methods(["GET"])
def get_device_types_ajax(request):
    """API: Pobierz typy urządzeń dla wybranej kategorii"""
    category_id = request.GET.get('category_id')
    
    if not category_id:
        return JsonResponse({'error': 'Brak ID kategorii'}, status=400)
    
    try:
        device_types = DeviceType.objects.filter(category_id=category_id).values('id', 'name', 'slug')
        return JsonResponse({'device_types': list(device_types)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def search_requests_ajax(request):
    """API: Wyszukaj zgłoszenia"""
    query = request.GET.get('q', '')
    voivodeship = request.GET.get('voivodeship', '')
    category = request.GET.get('category', '')
    
    if request.user.role != 'service':
        return JsonResponse({'error': 'Brak uprawnień'}, status=403)
    
    try:
        service_profile = request.user.service_profile
        offered_ids = ServiceOffer.objects.filter(service=service_profile).values_list('service_request_id', flat=True)
        
        requests = ServiceRequest.objects.filter(
            status__in=['submitted', 'viewed_by_services', 'offers_received']
        ).exclude(id__in=offered_ids)
        
        if query:
            requests = requests.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) |
                Q(device_brand__icontains=query)
            )
        
        if voivodeship:
            requests = requests.filter(voivodeship=voivodeship)
        
        if category:
            requests = requests.filter(device_category_id=category)
        
        results = []
        for req in requests[:10]:
            results.append({
                'id': req.id,
                'title': req.title,
                'device': f"{req.device_brand} {req.device_model}",
                'city': req.city,
                'voivodeship': req.voivodeship,
                'priority': req.get_priority_display(),
                'created_at': req.created_at.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse({'results': results})
    except ServiceProfile.DoesNotExist:
        return JsonResponse({'error': 'Brak profilu serwisu'}, status=400)


@login_required
@require_http_methods(["GET"])
def dashboard_stats_ajax(request):
    """API: Statystyki dashboardu"""
    stats = {}
    
    if request.user.role == 'client':
        try:
            client_profile = request.user.client_profile
            stats = {
                'total_requests': client_profile.service_requests.count(),
                'draft': client_profile.service_requests.filter(status='draft').count(),
                'submitted': client_profile.service_requests.filter(status='submitted').count(),
                'in_progress': client_profile.service_requests.filter(status='in_progress').count(),
                'completed': client_profile.service_requests.filter(status='completed').count(),
                'cancelled': client_profile.service_requests.filter(status='cancelled').count(),
            }
        except ClientProfile.DoesNotExist:
            stats = {'total_requests': 0}
    
    elif request.user.role == 'service':
        try:
            service_profile = request.user.service_profile
            stats = {
                'total_offers': service_profile.offers.count(),
                'pending_offers': service_profile.offers.filter(status='pending').count(),
                'accepted_offers': service_profile.offers.filter(status='accepted').count(),
                'total_reviews': service_profile.reviews.count(),
                'average_rating': round(service_profile.reviews.aggregate(Avg('rating'))['rating__avg'] or 0, 2),
            }
        except ServiceProfile.DoesNotExist:
            stats = {'total_offers': 0}
    
    elif request.user.role == 'admin':
        stats = {
            'total_users': User.objects.count(),
            'clients': User.objects.filter(role='client').count(),
            'services': User.objects.filter(role='service').count(),
            'total_requests': ServiceRequest.objects.count(),
            'active_requests': ServiceRequest.objects.filter(status__in=['submitted', 'in_progress']).count(),
        }
    
    return JsonResponse(stats)


@login_required
def chat_view(request, request_pk):
    """Czat między klientem a serwisem dla danego zgłoszenia"""
    service_request = get_object_or_404(ServiceRequest, pk=request_pk)
    
    # Sprawdź uprawnienia
    can_access = False
    error_msg = 'Brak uprawnień'
    
    if request.user.role == 'client':
        try:
            client_profile = ClientProfile.objects.get(user=request.user)
            if service_request.client_id == client_profile.id:
                can_access = True
            else:
                error_msg = 'To nie jest Twoje zgłoszenie'
        except ClientProfile.DoesNotExist:
            error_msg = 'Nie masz profilu klienta'
    elif request.user.role == 'service':
        try:
            service_profile = ServiceProfile.objects.get(user=request.user)
            # Serwis może rozmawiać jeśli ma ofertę LUB zgłoszenie jest aktywne (może zadać pytanie przed ofertą)
            has_offer = ServiceOffer.objects.filter(service_request=service_request, service=service_profile).exists()
            is_active = service_request.status in ['submitted', 'viewed_by_services', 'offers_received', 'in_progress']
            if has_offer or is_active:
                can_access = True
            else:
                error_msg = 'Zgłoszenie jest już zakończone lub anulowane'
        except ServiceProfile.DoesNotExist:
            error_msg = 'Nie masz profilu serwisu'
    elif request.user.role == 'admin':
        can_access = True
    else:
        error_msg = f'Nieznana rola: {request.user.role}'
    
    if not can_access:
        messages.error(request, f'{error_msg}.')
        return redirect('dashboard')
    
    # Pobierz wiadomości
    messages_list = Message.objects.filter(service_request=service_request).order_by('created_at')
    
    # Kto jest odbiorcą?
    recipient_name = 'Użytkownik'
    if request.user.role == 'client':
        # Klient - pokaż nazwę serwisu
        accepted_offer = service_request.offers.filter(status='accepted').first()
        if accepted_offer:
            recipient_name = accepted_offer.service.company_name or accepted_offer.service.user.username
        else:
            recipient_name = 'Serwis'
    elif request.user.role == 'service':
        # Serwis - pokaż nazwę klienta
        recipient_name = f"{service_request.client.first_name} {service_request.client.last_name}"
    elif request.user.role == 'admin':
        recipient_name = 'Administrator'
    
    context = {
        'service_request': service_request,
        'messages': messages_list,
        'recipient_name': recipient_name,
    }
    
    return render(request, 'zgloszenia/chat.html', context)


@login_required
def get_messages_ajax(request, request_pk):
    """API: Pobierz wiadomości dla zgłoszenia"""
    service_request = get_object_or_404(ServiceRequest, pk=request_pk)
    
    # Sprawdź uprawnienia
    if request.user.role == 'client':
        try:
            client_profile = request.user.client_profile
            if service_request.client != client_profile:
                return JsonResponse({'error': 'Brak uprawnień'}, status=403)
        except ClientProfile.DoesNotExist:
            return JsonResponse({'error': 'Brak profilu'}, status=403)
    elif request.user.role == 'service':
        try:
            service_profile = request.user.service_profile
            if not ServiceOffer.objects.filter(service_request=service_request, service=service_profile).exists():
                return JsonResponse({'error': 'Brak uprawnień'}, status=403)
        except ServiceProfile.DoesNotExist:
            return JsonResponse({'error': 'Brak profilu'}, status=403)
    
    messages_list = Message.objects.filter(service_request=service_request).order_by('created_at')
    
    data = {
        'messages': [
            {
                'id': m.id,
                'content': m.content,
                'sender': m.sender.username,
                'sender_id': m.sender.id,
                'is_mine': m.sender.id == request.user.id,
                'created_at': m.created_at.strftime('%H:%M'),
            }
            for m in messages_list
        ]
    }
    
    return JsonResponse(data)


@login_required
def notifications_count_ajax(request):
    """API: Liczba nieprzeczytanych powiadomień"""
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count})
