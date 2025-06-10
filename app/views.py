
from django.shortcuts import redirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
from .forms import RegisterUserForm, SubscribeForm
from .layers.services import services
from .layers.utilities import translator
from .forms import RegisterUserForm
from .forms import SubscribeForm
from django.utils import timezone
from .models import UserProfile
from django.contrib.auth.views import LoginView

###
LOCKOUT_THRESHOLD = 5 # Número de intentos fallidos antes del bloqueo
LOCKOUT_DURATION_MINUTES = 15 # Duración del bloqueo en minutos

class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True # Redirige si el usuario ya está logueado
    
    def form_invalid(self, form):
        username_attempted = form.cleaned_data.get('username')
        
        if username_attempted:
            try:
                user = User.objects.get(username=username_attempted)
                profile, created = UserProfile.objects.get_or_create(user=user)

                # Si la cuenta está bloqueada, muestra el mensaje y no proceses el login
                if profile.lockout_until and profile.lockout_until > timezone.now(): # Usa timezone.now()
                    remaining_time = profile.lockout_until - timezone.now()
                    minutes = int(remaining_time.total_seconds() // 60)
                    seconds = int(remaining_time.total_seconds() % 60)
                    messages.error(self.request, f"Tu cuenta está bloqueada. Intenta de nuevo en {minutes} minutos y {seconds} segundos.")
                    return super().form_invalid(form) # Devuelve la respuesta predeterminada para form_invalid
                
                # Incrementa los intentos fallidos
                profile.failed_login_attempts += 1
                
                if profile.failed_login_attempts >= LOCKOUT_THRESHOLD:
                    profile.lockout_until = timezone.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES) # Usa timezone.now()
                    messages.error(self.request, f"Demasiados intentos de sesión fallidos. Tu cuenta ha sido bloqueada por {LOCKOUT_DURATION_MINUTES} minutos.")
                else:
                    messages.error(self.request, "Nombre de usuario o contraseña incorrectos.")
                
                profile.save()

            except User.DoesNotExist:
                # Si el usuario no existe, sigue mostrando un mensaje genérico para no dar pistas
                messages.error(self.request, "Nombre de usuario o contraseña incorrectos.")
        else:
            # Si el campo de usuario está vacío o no se procesó, muestra un error genérico
            messages.error(self.request, "Por favor, ingresa tu nombre de usuario y contraseña.")

        # Llama al método original para que la plantilla se renderice de nuevo con los errores del formulario
        return super().form_invalid(form)
###
def register(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Validar si el nombre de usuario ya existe
            if User.objects.filter(username=username).exists():
                messages.error(request, "Error: El nombre de usuario ya está registrado.")
            # Validar si el correo electrónico ya existe
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Error: Este correo electrónico ya está registrado.")
            else:
                # Crear el nuevo usuario
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                user.save()

                messages.success(request, "¡Registro exitoso! Revisa tu correo electrónico para las credenciales.")

                # --- Lógica de Envío de Correo de Bienvenida ---
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
                    messages.error(request, f"Error al enviar el correo. Por favor, verifica la configuración de email. Detalle: {e}")
                
                return redirect('login') 
        else:
            # Si el formulario no es válido, mostramos los errores
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
'''
def subscribe(request):
    form = SubscribeForm()
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            subject = 'Confirmación de Suscripción POKEDEX'
            message_body = 'Gracias por suscribirte a las novedades de POKEDEX. ¡Pronto recibirás más información!'
            recipient = form.cleaned_data.get('email')
            
            try:
                send_mail(subject, 
                          message_body, 
                          settings.EMAIL_HOST_USER, 
                          [recipient], 
                          fail_silently=False)
                messages.success(request, '¡Suscripción exitosa! Revisa tu correo.')
            except Exception as e:
                messages.error(request, f'Error al enviar el correo de confirmación: {e}.')
            
            return redirect('subscribe')
    return render(request, 'subscribe.html', {'form': form})
'''
###

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados: uno de las imágenes de la API y otro de favoritos, ambos en formato Card, y los dibuja en el template 'home.html'.
def home(request) :
    images = services.getAllImages()  # obtiene todas las imágenes de la API de Pokemon.
    favourite_list = services.getAllFavourites(request)  # obtiene los favoritos del usuario actual, si está logueado.
    if favourite_list is None :
        favourite_list = []   
    favourite_ids = {card.id for card in favourite_list}# si el usuario no está logueado, favourite_list será None, por lo que lo inicializamos como una lista vacía.
    context = {'images': images,
               'favourite_list': favourite_list,
               'favourite_ids': favourite_ids,
               }
    return render(request, 'home.html', context)
# 1. 'render' toma la 'request' para entender el contexto de la petición.             # render(request, ...)
# 2. Carga el contenido del archivo 'home.html'.                                    # 'home.html'
# 3. Toma el diccionario de contexto y "inyecta" esos datos dentro de la plantilla HTML. # { 'images': images, 'favourite_list': favourite_list }
# 4. Genera una respuesta HTTP completa con el HTML renderizado.                    # render(...)
# 5. Finalmente, 'return' envía esa respuesta HTTP de vuelta al navegador del usuario, lo que resulta en la visualización de la página web. # return render(...)

# función utilizada en el buscador.
def search(request) :
    name = request.POST.get('query', '') # Esto obtiene la lista de objetos Card de favoritos 
    # si el usuario ingresó algo en el buscador, se deben filtrar las imágenes por dicho ingreso.
    if (name != '') :
        images = services.filterByCharacter(name)
        favourite_list = services.getAllFavourites(request)
        if favourite_list is None :
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

# función utilizada para filtrar por el tipo del Pokemon
def filter_by_type(request) :
    type = request.POST.get('type', '')

    if type != '' :
        images = services.filterByType(type) # debe traer un listado filtrado de imágenes, segun si es o contiene ese tipo.
        favourite_list = services.getAllFavourites(request)
        if favourite_list is None :
            favourite_list = []
        favourite_ids = {card.id for card in favourite_list}
        context = {'images': images,
                   'favourite_list': favourite_list,
                   'favourite_ids': favourite_ids,
                   }
        return render(request, 'home.html', context)
    else:
        return redirect('home')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = services.getAllFavourites(request)
    if favourite_list is None:
        favourite_list = []
    return render(request, 'favourites.html', {'favourite_list': favourite_list})

@login_required
def saveFavourite(request) :
    if request.method == 'POST' : 
        succes = services.saveFavourite(request)  # Guardar el favorito usando los datos del POST.
        if not succes :
            print("Error al guardar el favorito.")      
        else :
            print('Exito al agregar el favorito')
        
        next_url = request.POST.get('next')
        return redirect(next_url if next_url else 'home')
    else :
        print("Error: Método no permitido. Se esperaba POST.")
        return redirect('home')
    
@login_required
def deleteFavourite(request) :
    if request.method == 'POST' :
        succes = services.deleteFavourite(request)
        if not succes :
            print('Error al eliminar el favorito')
        else :
            print('Exito al eliminar el favorito')
            
        next_url = request.POST.get('next')
    else :
        print("Error: Método no permitido. Se esperaba POST.")
    return (redirect (next_url) if next_url else redirect('home'))

@login_required
def exit(request):
    logout(request)
    return redirect('home')