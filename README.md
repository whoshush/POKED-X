## 🔴 Pokedex - Django Multilayer Application

Un proyecto web Full-Stack desarrollado en **Python/Django** que permite buscar, filtrar y guardar Pokémon favoritos consumiendo una API externa.

Este proyecto fue estructurado aplicando una estricta **Arquitectura Multicapas (Multilayered Architecture)**, separando las responsabilidades de la lógica de negocio, la persistencia de datos y la interfaz de usuario para garantizar un código mantenible, escalable y limpio.

## 🚀 Tecnologías y Herramientas
* **Backend:** Python 3.14+, Django 4.2.10
* **Base de Datos:** SQLite3 (Integrada)
* **Frontend:** HTML5, CSS3, Bootstrap 5, Django Templates.
* **Consumo de API:** `requests` para HTTP (PokeAPI/API de imágenes externa).
* **Seguridad:** Sistema de bloqueo de cuentas tras intentos fallidos usando `django-axes` e implementación de login/logout seguro.

## 🏗️ Arquitectura Multicapas
El flujo de datos del proyecto se divide en las siguientes capas claramente delimitadas:
1.  **Views/Templates (UI):** Renderizan la interfaz y reciben peticiones HTTP.
2.  **Services (Lógica de Negocio):** El cerebro de la aplicación. Filtra datos y determina qué mostrar.
3.  **Transport (Consumo API):** Se encarga exclusivamente de las peticiones HTTP externas.
4.  **Persistence (Repositorios):** Maneja el ORM de Django (ABM) para leer y guardar favoritos en SQLite.
5.  **Utilities (Translators):** Mapean los JSON crudos en objetos DTO estandarizados (Cards).
"""
f = open('README.md', 'w', encoding='utf-8')
f.write(readme_profesional)
f.close()
print("✅ README.md actualizado con formato profesional.")
