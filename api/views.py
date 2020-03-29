from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from imquarantined.settings import BASE_DIR
from .serializers import PlayerSerializer
from .models import Player

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials


def index(request):
    cred = credentials.Certificate(BASE_DIR + "/imquarantined-firebase.json")
    default_app = firebase_admin.initialize_app(cred, name='Firebaseeee')

    # Creating a custom_token
    uid = "CRqlOwGCj4ctUKULlFyNKXdkvC72"
    additional_claims = {
        "premiumAccount": True
    }
    custom_token = auth.create_custom_token(uid, additional_claims, app=default_app)

    # Verifying an id_token
    # decoded_token = auth.verify_id_token(id_token, default_app)
    # uid = decoded_token['uid']

    uid = 'CRqlOwGCj4ctUKULlFyNKXdkvC72'
    user = auth.get_user(uid, default_app)

    return HttpResponse(f'Fetched data from {user.user_metadata} - {user.display_name}, {user.email}, and also image {user.photo_url}')


class PlayerLogin(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):

        id_token = request.POST['id_token']

        # Setting up firebase_app
        cred = credentials.Certificate(BASE_DIR + "imquarantined-firebase.json")
        firebase = firebase_admin.initialize_app(cred, name='firebase')

        # Verifying an id_token
        decoded_token = auth.verify_id_token(id_token, firebase)
        uid = decoded_token['uid']
        user = auth.get_user(uid, firebase)

        response = {
            "success": True,
            'message': 'Working on it!',
            'data': {
                'id_token': id_token,
                'uid': user.uid,
                'photo': user.photo_url,
                'phone': user.phone_number,
                'name': user.display_name,
                'email': user.email,
                'base': BASE_DIR
            }
        }
        return Response(response)


class UpdateLocation(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):

        id_token = request.POST['id_token']

        # Setting up firebase_app
        cred = credentials.Certificate("/media/tmdfx/Stuff/Code/imquarantined/imquarantined-firebase.json")
        firebase = firebase_admin.initialize_app(cred, name='firebase')

        # Verifying an id_token
        decoded_token = auth.verify_id_token(id_token, firebase)
        uid = decoded_token['uid']
        user = auth.get_user(uid, firebase)

        response = {
            "success": True,
            'message': 'Working on it!',
            'data': {
                'id_token': id_token,
                'uid': user.uid,
                'photo': user.photo_url,
                'phone': user.phone_number,
                'name': user.display_name,
                'email': user.email
            }
        }
        return Response(response)

# Testing database models

class PlayersViewSet(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
