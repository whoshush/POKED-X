# capa de servicio/lógica de negocio
from app.models import Favourite
from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator
from django.contrib.auth import get_user


# función que devuelve un listado de cards. Cada card representa una imagen de la API de Pokemon
def getAllImages() :
    # debe ejecutar los siguientes pasos:
    raw_images = transport.getAllImages() #1) traer un listado de imágenes crudas desde la API (ver transport.py)
    cards = []# 2) convertir cada img. en una card.
    for raw_image in raw_images :
        card = translator.fromRequestIntoCard(raw_image)
        cards.append(card)# 3) añadirlas a un nuevo listado que, finalmente, se retornará con todas las card encontradas.
    return cards # 4) retornar el listado de cards


# función que filtra según el nombre del pokemon.
def filterByCharacter(name) :
    filtered_cards = []
    cards = getAllImages()
    for card in cards :
        if name.lower() == card.name.lower() :
            filtered_cards.append(card)
    return filtered_cards
##aca later estaria bueno implementar el tipico de "quizas quisiste decir" y mostrar un listado de cards que coincidan parcialmente con el nombre buscado.

# función que filtra las cards según su tipo.
def filterByType(type_filter):
    type_filter = type_filter.lower()
    filtered_cards = []
    cards = getAllImages()
    for card in cards :
        if type_filter in [t.lower() for t in card.types] :
            filtered_cards.append(card)
    return filtered_cards

# añadir favoritos (usado desde el template 'home.html')
def saveFavourite(request) :
    card = translator.fromTemplateIntoCard(request) # transformamos el request en una Card (ver translator.py)
    current_user = get_user(request)
    if not current_user.is_authenticated :
        print("Error: Intento de guardar favorito por usuario no autenticado.")
        return False
    # Creo una instancia del modelo 'Favourite' de la base de datos,
    # asignando el usuario actual y los detalles del Pokémon de la 'card'.
    favourite_entry_db = Favourite(
        user = current_user,  # Usuario autenticado
        name = card.name,  # Nombre del Pokémon
        id = card.id,  # ID del Pokémon
        height = card.height,  # Altura del Pokémon
        weight = card.weight,  # Peso del Pokémon
        base_experience = card.base,  # Experiencia base del Pokémon
        types = card.types,  # Tipos del Pokémon
        image = card.image  # Imagen del Pokémon
    )
    return repositories.save_favourite(favourite_entry_db) # lo mando para repositories en forma de instacia(es un elemento espeficio de django para manejar grupos de datos)(lo qu espera repositories) para que se guarde en la BD.
    

# usados desde el template 'favourites.html'
def getAllFavourites(request):
    current_user = get_user(request)
    if not current_user.is_authenticated :
        print("El usuario no esta autenticado.")
        return None

    favourite_list = repositories.get_all_favourites(current_user) # buscamos desde el repositories.py TODOS Los favoritos del usuario (variable 'user').
    mapped_favourites = []

    for favourite in favourite_list :
            card = translator.fromRepositoryIntoCard(favourite) # convertimos cada favorito en una Card, y lo almacenamos en el listado de mapped_favourites que luego se retorna.
            mapped_favourites.append(card)
    return mapped_favourites

def deleteFavourite(request) :
    favId = request.POST.get('id')
    current_user = get_user(request)
    if not current_user.is_authenticated:
        print("El usuario no esta autenticado.")
        return False
    
    deleted_successfully = repositories.delete_favourite(favId, current_user) # borramos un favorito por su ID
    if deleted_successfully :
        print(f"Favorito con ID {favId} eliminado correctamente.")
    else:
        print(f"Error al eliminar el favorito con ID {favId}. Puede que no exista o no pertenezca al usuario.")
    return deleted_successfully

#obtenemos de TYPE_ID_MAP el id correspondiente a un tipo segun su nombre
def get_type_icon_url_by_name(type_name):
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)