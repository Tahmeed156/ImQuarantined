from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('players', views.PlayersViewSet)

urlpatterns = [

    path('', views.index, name='index'),

    # login
    path('auth', views.PlayerLogin.as_view(), name='player-login'),
    path('location/update', views.UpdateLocation.as_view(), name='location-update'),

    path('models/', include(router.urls))
]

