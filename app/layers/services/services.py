from typing import List, Optional
from django.http import HttpRequest
from django.contrib.auth import get_user
from app.models import Favourite
from ..transport import transport
from ...config import config
from ..persistence import repositories
from ..utilities import translator

def get_all_images() -> list:
    """
    Obtiene un listado de imágenes crudas desde la API y las transforma en objetos Card.
    """
    raw_images = transport.getAllImages()
    return [translator.fromRequestIntoCard(raw_image) for raw_image in raw_images]

def filter_by_character(name: str) -> list:
    """
    Filtra el listado de cards buscando una coincidencia exacta por nombre.
    TODO: Implementar búsqueda difusa para sugerir resultados ("quizás quisiste decir...").
    """
    name_lower = name.lower()
    return [card for card in get_all_images() if card.name.lower() == name_lower]

def filter_by_type(type_filter: str) -> list:
    """
    Filtra las cards asegurando que el tipo buscado se encuentre entre los tipos del Pokémon.
    """
    type_filter_lower = type_filter.lower()
    return [card for card in get_all_images() if type_filter_lower in (t.lower() for t in card.types)]

def save_favourite(request: HttpRequest) -> bool:
    """
    Transforma el request en una Card y persiste el favorito en la base de datos
    para el usuario autenticado.
    """
    current_user = get_user(request)
    
    if not current_user.is_authenticated:
        # Nota: En producción, es mejor usar el módulo 'logging' en lugar de prints
        print("Error: Intento de guardar favorito por usuario no autenticado.")
        return False
        
    card = translator.fromTemplateIntoCard(request)
    
    favourite_entry_db = Favourite(
        user=current_user,
        name=card.name,
        id=card.id,
        height=card.height,
        weight=card.weight,
        base_experience=card.base,
        types=card.types,
        image=card.image
    )
    
    return repositories.save_favourite(favourite_entry_db)

def get_all_favourites(request: HttpRequest) -> list:
    """
    Retorna una lista de Cards con todos los favoritos del usuario actual.
    """
    current_user = get_user(request)
    
    if not current_user.is_authenticated:
        print("Error: El usuario no está autenticado.")
        return []

    favourite_list = repositories.get_all_favourites(current_user)
    return [translator.fromRepositoryIntoCard(favourite) for favourite in favourite_list]

def delete_favourite(request: HttpRequest) -> bool:
    """
    Elimina un favorito específico del usuario autenticado a través de su ID.
    """
    fav_id = request.POST.get('id')
    current_user = get_user(request)
    
    if not current_user.is_authenticated:
        print("Error: El usuario no está autenticado.")
        return False
        
    deleted_successfully = repositories.delete_favourite(fav_id, current_user)
    
    if deleted_successfully:
        print(f"Favorito con ID {fav_id} eliminado correctamente.")
    else:
        print(f"Error al eliminar el favorito con ID {fav_id}. Puede que no exista o no pertenezca al usuario.")
        
    return deleted_successfully

def get_type_icon_url_by_name(type_name: str) -> Optional[str]:
    """
    Obtiene la URL del ícono correspondiente a un tipo de Pokémon según su nombre.
    """
    type_id = config.TYPE_ID_MAP.get(type_name.lower())
    if not type_id:
        return None
    return transport.get_type_icon_url_by_id(type_id)