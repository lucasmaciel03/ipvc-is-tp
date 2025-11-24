"""
REST API URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet, DataRecordViewSet
from .xpath_views import XPathQueryViewSet

# Create router
router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'records', DataRecordViewSet, basename='record')
router.register(r'xpath', XPathQueryViewSet, basename='xpath')

urlpatterns = [
    path('', include(router.urls)),
]
