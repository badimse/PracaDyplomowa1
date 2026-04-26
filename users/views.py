from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, ClientProfile, ServiceProfile, Notification
from .forms import UserRegistrationForm, ClientProfileForm, ServiceProfileForm, LoginForm


def register_view(request):
    """Rejestracja nowego użytkownika"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()
            
            # Utwórz odpowiedni profil
            if user.role == 'client':
                ClientProfile.objects.create(
                    user=user,
                    first_name='',
                    last_name='',
                    email=user.email,
                    phone='',
                    city='',
                    postal_code=''
                )
            elif user.role == 'service':
                ServiceProfile.objects.create(
                    user=user,
                    company_name='',
                    email=user.email,
                    phone='',
                    city='',
                    postal_code='',
                    voivodeship=''
                )
            
            login(request, user)
            messages.success(request, 'Konto zostało utworzone! Uzupełnij dane profilu.')
            return redirect('profile_edit')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Logowanie użytkownika"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Witaj {user.username}!')
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """Wylogowanie użytkownika"""
    logout(request)
    messages.info(request, 'Zostałeś wylogowany.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Panel główny - dashboard"""
    context = {}
    
    if request.user.role == 'client':
        # Klient widzi swoje zgłoszenia
        try:
            client_profile = request.user.client_profile
            from zgloszenia.models import ServiceRequest
            context['requests'] = ServiceRequest.objects.filter(client=client_profile).order_by('-created_at')[:10]
            context['profile'] = client_profile
        except ClientProfile.DoesNotExist:
            ClientProfile.objects.create(user=request.user)
            context['profile'] = None
    elif request.user.role == 'service':
        # Serwis widzi dostępne zgłoszenia
        try:
            service_profile = request.user.service_profile
            from zgloszenia.models import ServiceRequest, ServiceOffer
            context['profile'] = service_profile
            
            # Zgłoszenia, na które serwis nie złożył oferty
            offered_ids = ServiceOffer.objects.filter(service=service_profile).values_list('service_request_id', flat=True)
            context['available_requests'] = ServiceRequest.objects.filter(
                status='submitted'
            ).exclude(id__in=offered_ids).order_by('-created_at')[:10]
            
            # Oferty serwisu
            context['my_offers'] = ServiceOffer.objects.filter(service=service_profile).order_by('-created_at')[:10]
        except ServiceProfile.DoesNotExist:
            ServiceProfile.objects.create(user=request.user)
            context['profile'] = None
    else:
        # Administrator
        context['users_count'] = User.objects.count()
        context['clients_count'] = User.objects.filter(role='client').count()
        context['services_count'] = User.objects.filter(role='service').count()
        
        # Płatności oczekujące
        from zgloszenia.models import Payment, ServiceRequest
        context['payments_pending'] = Payment.objects.filter(status='paid_to_admin').count()
        
        # Aktywne zgłoszenia
        context['active_requests'] = ServiceRequest.objects.filter(status__in=['submitted', 'in_progress', 'offers_received']).count()
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile_view(request):
    """Wyświetlanie profilu"""
    context = {}
    
    if request.user.role == 'client':
        try:
            profile = request.user.client_profile
            context['profile'] = profile
            context['in_progress_count'] = profile.service_requests.filter(status='in_progress').count()
            context['completed_count'] = profile.service_requests.filter(status='completed').count()
        except ClientProfile.DoesNotExist:
            context['profile'] = None
            context['in_progress_count'] = 0
            context['completed_count'] = 0
    elif request.user.role == 'service':
        try:
            profile = request.user.service_profile
            context['profile'] = profile
            # Oblicz średnią ocenę
            reviews = profile.reviews.all()
            if reviews.exists():
                total_rating = sum(r.rating for r in reviews)
                context['average_rating'] = round(total_rating / reviews.count())
            else:
                context['average_rating'] = 0
        except ServiceProfile.DoesNotExist:
            context['profile'] = None
            context['average_rating'] = 0
    else:
        context['profile'] = None
    
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edycja profilu"""
    if request.user.role == 'client':
        profile, created = ClientProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = ClientProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil został zaktualizowany.')
                return redirect('profile')
        else:
            form = ClientProfileForm(instance=profile)
    elif request.user.role == 'service':
        profile, created = ServiceProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = ServiceProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil został zaktualizowany.')
                return redirect('profile')
        else:
            form = ServiceProfileForm(instance=profile)
    else:
        messages.error(request, 'Administrator nie ma profilu.')
        return redirect('dashboard')
    
    return render(request, 'users/profile_edit.html', {'form': form})


@login_required
def admin_panel_view(request):
    """Panel administratora"""
    if request.user.role != 'admin':
        messages.error(request, 'Brak uprawnień.')
        return redirect('dashboard')
    
    users = User.objects.all().order_by('-created_at')
    
    # Filtrowanie
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Filtrowanie po dacie rejestracji
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if date_from:
        users = users.filter(created_at__date__gte=date_from)
    if date_to:
        users = users.filter(created_at__date__lte=date_to)
    
    # Filtrowanie po statusie weryfikacji (dla serwisów)
    verified_filter = request.GET.get('verified', '')
    if verified_filter == 'yes':
        users = users.filter(service_profile__is_verified=True)
    elif verified_filter == 'no':
        users = users.filter(service_profile__is_verified=False)
    
    # Filtrowanie po województwie
    voivodeship_filter = request.GET.get('voivodeship', '')
    if voivodeship_filter:
        users = users.filter(
            Q(client_profile__voivodeship__icontains=voivodeship_filter) |
            Q(service_profile__voivodeship__icontains=voivodeship_filter)
        )
    
    # Pobierz dane z profili dla każdego użytkownika
    users_data = []
    for user_item in users:
        voivodeship = ''
        status = 'Aktywny'
        is_verified = False
        
        if user_item.role == 'client':
            try:
                profile = user_item.client_profile
                voivodeship = profile.voivodeship or '-'
            except ClientProfile.DoesNotExist:
                voivodeship = '-'
        elif user_item.role == 'service':
            try:
                profile = user_item.service_profile
                voivodeship = profile.voivodeship or '-'
                is_verified = profile.is_verified
                status = 'Zweryfikowany' if is_verified else 'Oczekuje'
            except ServiceProfile.DoesNotExist:
                voivodeship = '-'
        else:
            voivodeship = '-'
        
        users_data.append({
            'user': user_item,
            'voivodeship': voivodeship,
            'status': status,
            'is_verified': is_verified,
        })
    
    context = {
        'users_data': users_data,
        'users_count': len(users_data),
        'role_filter': role_filter,
        'search_query': search_query,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'filter_verified': verified_filter,
        'filter_voivodeship': voivodeship_filter,
    }
    
    return render(request, 'users/admin_panel.html', context)


@login_required
def admin_user_create_view(request):
    """Administrator tworzy użytkownika"""
    if request.user.role != 'admin':
        messages.error(request, 'Brak uprawnień.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.is_staff = (user.role == 'admin')
            user.save()
            
            # Utwórz profil
            if user.role == 'client':
                ClientProfile.objects.create(
                    user=user,
                    first_name=request.POST.get('first_name', ''),
                    last_name=request.POST.get('last_name', ''),
                    email=user.email,
                )
            elif user.role == 'service':
                ServiceProfile.objects.create(
                    user=user,
                    company_name=request.POST.get('company_name', ''),
                    email=user.email,
                )
            
            messages.success(request, 'Użytkownik został utworzony.')
            return redirect('admin_panel')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/admin_user_create.html', {'form': form})


@login_required
def admin_user_delete_view(request, user_id):
    """Administrator usuwa użytkownika"""
    if request.user.role != 'admin':
        messages.error(request, 'Brak uprawnień.')
        return redirect('dashboard')
    
    user = get_object_or_404(User, pk=user_id)
    if user == request.user:
        messages.error(request, 'Nie możesz usunąć samego siebie.')
        return redirect('admin_panel')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'Użytkownik został usunięty.')
        return redirect('admin_panel')
    
    return render(request, 'users/admin_user_delete.html', {'user': user})


@login_required
def notifications_list_view(request):
    """Lista powiadomień użytkownika"""
    # Oznacz wszystkie jako przeczytane
    request.user.notifications.update(is_read=True)
    
    notifications = request.user.notifications.all().order_by('-created_at')
    
    return render(request, 'users/notifications.html', {'notifications': notifications})


@login_required
def notification_mark_as_read_view(request, notification_id):
    """Oznacz powiadomienie jako przeczytane"""
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # Jeśli ma link, przekieruj
    if notification.link:
        return redirect(notification.link)
    
    return redirect('notifications_list')


@login_required
def notification_mark_all_as_read_view(request):
    """Oznacz wszystkie powiadomienia jako przeczytane"""
    request.user.notifications.update(is_read=True)
    messages.success(request, 'Wszystkie powiadomienia zostały oznaczone jako przeczytane.')
    return redirect('dashboard')
