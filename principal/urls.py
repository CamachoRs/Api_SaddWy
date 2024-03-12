"""
URL configuration for principal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Documentación de la API de SaddWy",
      default_version='v01',
      description="API de SaddWy: Plataforma de aprendizaje en lógica de programación diseñada para ofrecer una experiencia educativa interactiva y accesible. Con un enfoque en el desarrollo lógico y algorítmico, SaddWy proporciona una amplia variedad de lecciones, ejercicios y desafíos diseñados para personas de todos los niveles de conocimiento en programación. Con una interfaz intuitiva y fácil de usar, nuestra API se esfuerza por mantener a los usuarios comprometidos y motivados en su viaje de aprendizaje.",
      contact=openapi.Contact(email="saddwy2003@gmail.com"),
      license=openapi.License(name="Licencia Propietaria"),
   ),
   public=True
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('documentation/swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('documentation/redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    path('api/', include('api.urls'))
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)