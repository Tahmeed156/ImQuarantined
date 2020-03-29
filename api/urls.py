from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('players', views.PlayersViewSet)

urlpatterns = [
    path('', views.HomeScreen.as_view(), name='home-screen'),
    path('auth', views.PlayerLogin.as_view(), name='player-login'),
    path('location/update', views.UpdateLocation.as_view(), name='location-update'),
    path('profile', views.PlayerProfile.as_view(), name='profile'),
    path('leaderboard/', views.Leaderboard.as_view(), name='leaderboard'),

    path('models/', include(router.urls))
]

