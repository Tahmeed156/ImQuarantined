from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('players', views.PlayersViewset)

urlpatterns = [

    path('', views.index, name='index'),

    # login
    path('login', views.PlayerLogin.asView(), name='player-login'),

    path('models/', include(router.urls))
]

