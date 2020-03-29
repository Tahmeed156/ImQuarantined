import json

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from imquarantined.settings import BASE_DIR
from .serializers import PlayerSerializer
from .models import Player, Location

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials


def index(request):
    return HttpResponse(f'wow')


class PlayerLogin(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        message = ''
        success = True
        data = {}

        id_token = request.POST['id_token']

        # Setting up firebase_app
        cred = credentials.Certificate(BASE_DIR + "/imquarantined-firebase.json")
        firebase = firebase_admin.initialize_app(cred, name='firebase')

        try:
            # Verifying an id_token
            decoded_token = auth.verify_id_token(id_token, firebase)
            uid = decoded_token['uid']
            user = auth.get_user(uid, firebase)
            data = {
                'id_token': id_token,
                'uid': user.uid,
                'photo': user.photo_url,
                'phone': user.phone_number,
                'name': user.display_name,
                'email': user.email,
                'base': BASE_DIR
            }
        except firebase_admin.auth.ExpiredIdTokenError:
            success = False
            message = 'Id Token Expired'

        # Deleting app instance
        firebase_admin.delete_app(firebase)

        response = {
            "success": success,
            'message': message,
            'data': data
        }
        return Response(response)


class UpdateLocation(APIView):
    
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        response = {
            "success": True,
            'message': 'Still at home',
            'data': {}
        }

        locations_string = request.POST['locations']
        locations = json.loads(locations_string)
        for count, loc in enumerate(locations):
            lat = loc['lat']
            long = loc['long']
            alti = loc['alti']
            new_loc = Location(
                latitude=loc['lat'],
                longitude=loc['long'],
                altitude=loc['alti']
            )
            # new_loc.save()
            response['data'][count] = loc

        return Response(response)


# Testing database models

class PlayersViewSet(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
