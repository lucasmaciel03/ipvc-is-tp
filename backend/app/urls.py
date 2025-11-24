"""
URL configuration for IPVC Integration System project.
"""
from django.contrib import admin
from django.urls import path, include
from app.core import views as core_views

urlpatterns = [
    path('', core_views.index, name='index'),
    path('dataset/<int:dataset_id>/', core_views.dataset_detail, name='dataset_detail'),
    path('admin/', admin.site.urls),
    path('api/', include('app.interfaces.rest.urls')),
]
