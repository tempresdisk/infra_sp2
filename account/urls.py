from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/email/', views.send_confirm_code, name='send_code'),
    path('v1/auth/token/', views.get_access_token, name='get_access_token')
]
