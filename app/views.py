from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse

from .forms import RegisterUserForm, SubscribeForm
from .models import UserProfile
from .layers.services import services
from .layers.utilities import translator

###
LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION_MINUTES = 15

class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        username_attempted = form.cleaned_data.get('username')
        
        if username_attempted:
            try:
                user = User.objects.get(username=username_attempted)
                profile, created = UserProfile.objects.get_or_create(user=user)

                if profile.lockout_until and profile.lockout_until > timezone.now():
                    remaining_time = profile.lockout_until - timezone.now()
                    minutes = int(remaining_time.total_seconds() // 60)
                    seconds = int(remaining_time.total_seconds() % 60)
                    messages.error(self.request, f"Tu cuenta está bloqueada. Intenta de nuevo en {minutes} minutos y {seconds} segundos.")
                    return super().form_invalid(form)
                
                profile.failed_login_attempts += 1
                
                if profile.failed_login_attempts >= LOCKOUT_THRESHOLD:
                    from datetime import timedelta
                    profile.lockout_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                    messages.error(self.request, f"Demasiados intentos fallidos. Tu cuenta ha sido bloqueada por {LOCKOUT_DURATION_MINUTES} minutos.")
                else:
                    messages.error(self.request, "Nombre de usuario o contraseña incorrectos.")
                
                profile.save()

            except User.DoesNotExist:
                messages.error(self.request, "Nombre de usuario o contraseña incorrectos.")
        else:
            messages.error(self.request, "Por favor, ingresa tu nombre de usuario y contraseña.")

        return super().form_invalid(form)

###
def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username).exists():
                messages.error(request, "Error: El nombre de usuario ya está registrado.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Error: Este correo electrónico ya está registrado.")
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()

                messages.success(request, "¡Registro exitoso! Revisa tu correo electrónico.")

                # --- Lógica de Envío de Correo ---
                mail_subject = 'Bienvenido a POKEDEX - Tus credenciales de acceso'
                login_url = request.build_absolute_uri(reverse('login')) 

                email_body_template = render_to_string('welcome_email.txt', {
                    'username': username,
                    'password': password,
                    'login_url': login_url,
                })

                email_message = EmailMessage(
                    mail_subject,
                    email_body_template,
                    settings.EMAIL_HOST_USER,
                    [email]
                )
                
                try:
                    email_message.send()
                    messages.info(request, "Correo de bienvenida enviado.")
                except Exception as e:
                    messages.error(request, f"Error al enviar el correo. Detalle: {e}")
                
                return redirect('login') 
        else:
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    messages.error(request, f"Error en '{field}': {error}")
            
            if '__all__' in form.errors:
                for error in form.errors['__all__']:
                    messages.error(request, f"Error general: {error}")

    else:
        form = RegisterUserForm()

    return render(request, 'register.html', {'form': form}) 

###
def index_page(request: HttpRequest) -> HttpResponse:
    return render(request, 'index.html')

def home(request: HttpRequest) -> HttpResponse:
    """Renderiza la galería principal con todas las cards de Pokémon."""
    images = services.get_all_images()
    favourite_list = services.get_all_favourites(request)
    
    if favourite_list is None:
        favourite_list = []
        
    favourite_ids = {card.id for card in favourite_list}
    
    context = {
        'images': images,
        'favourite_list': favourite_list,
        'favourite_ids': favourite_ids,
    }
    return render(request, 'home.html', context)

def search(request: HttpRequest) -> HttpResponse:
    """Filtra los resultados de la galería por nombre de Pokémon."""
    name = request.POST.get('query', '')
    
    if name != '':
        images = services.filter_by_character(name)
        favourite_list = services.get_all_favourites(request)
        
        if favourite_list is None:
            favourite_list = []
            
        favourite_ids = {card.id for card in favourite_list}
        context = {
            'images': images,
            'favourite_list': favourite_list,
            'favourite_ids': favourite_ids,
        }               
        return render(request, 'home.html', context)
    else:
        return redirect('home')

def filter_by_type(request: HttpRequest) -> HttpResponse:
    """Filtra los resultados de la galería según el tipo de Pokémon."""
    pokemon_type = request.POST.get('type', '')

    if pokemon_type != '':
        images = services.filter_by_type(pokemon_type)
        favourite_list = services.get_all_favourites(request)
        
        if favourite_list is None:
            favourite_list = []
            
        favourite_ids = {card.id for card in favourite_list}
        context = {
            'images': images,
            'favourite_list': favourite_list,
            'favourite_ids': favourite_ids,
        }
        return render(request, 'home.html', context)
    else:
        return redirect('home')

@login_required
def get_all_favourites_by_user(request: HttpRequest) -> HttpResponse:
    favourite_list = services.get_all_favourites(request)
    if favourite_list is None:
        favourite_list = []
    return render(request, 'favourites.html', {'favourite_list': favourite_list})

@login_required
def save_favourite(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST': 
        success = services.save_favourite(request)
        if not success:
            print("Error al guardar el favorito.")      
        else:
            print('Éxito al agregar el favorito')
        
        next_url = request.POST.get('next')
        return redirect(next_url if next_url else 'home')
    else:
        print("Error: Método no permitido. Se esperaba POST.")
        return redirect('home')
    
@login_required
def delete_favourite(request: HttpRequest) -> HttpResponse:
    next_url = request.POST.get('next')
    
    if request.method == 'POST':
        success = services.delete_favourite(request)
        if not success:
            print('Error al eliminar el favorito')
        else:
            print('Éxito al eliminar el favorito')
    else:
        print("Error: Método no permitido. Se esperaba POST.")
        
    return redirect(next_url) if next_url else redirect('home')

@login_required
def exit(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect('home')