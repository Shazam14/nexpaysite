"""
URL configuration for nexpaysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.routers import DefaultRouter
from nexpay_forexapp.views import ExchangeRateViewSet

router = DefaultRouter()
router.register(r'exchange-rate', ExchangeRateViewSet, basename='exchange-rate')

urlpatterns = router.urls


urlpatterns = [
    # path("nexpay_forexapp/", include("nexpay_forexapp.urls")),
    path('admin/', admin.site.urls),
    path('api/', include("nexpay_forexapp.urls")),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
