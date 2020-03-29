import json
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from firebase_admin.auth import ExpiredIdTokenError
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from imquarantined.settings import BASE_DIR
from .serializers import PlayerSerializer
from .models import Player, Location, Score

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials


class HomeScreen(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        response = {
            "success": True,
            'message': '',
            'data': {}
        }

        token_string = request.META['HTTP_AUTHORIZATION']
        id_token = token_string.split()[1]
        player = Player.objects.filter(fire_token=id_token).first()

        if player is not None:
            time_diff = player.location.last_updated - player.location.start_time
            secs = time_diff.seconds
            response['data'] = {
                'hr': (secs // 3600),
                'min': (secs // 60) % 60,
                'sec': secs % 60,
                'cur_streak': str(player.score.cur_streak),
                'progress': str(int(secs*100/86400)),
            }
        else:
            response['success'] = False
            response['message'] = 'No user has this id token'
            response['data']['id_token'] = id_token

        return Response(response)


class PlayerLogin(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        response = {
            "success": True,
            'message': 'Still at home',
            'data': {}
        }

        id_token = request.POST['id_token']

        # Setting up firebase_app
        cred = credentials.Certificate(BASE_DIR + "/imquarantined-firebase.json")
        firebase = firebase_admin.initialize_app(cred, name='firebase')

        try:
            # Verifying an id_token
            decoded_token = auth.verify_id_token(id_token, firebase)
            uid = decoded_token['uid']
            user = auth.get_user(uid, firebase)

            # Pushing user to database
            player = Player(
                user_name=user.display_name,
                fire_token=id_token,
                photo_url=user.photo_url
            )
            player.save()
            print("Here 1")

            loc = Location(player=player)
            score = Score(player=player)
            print("Here 2")
            loc.save()
            score.save()
            print("Here 3")

            response['message'] = 'Successfully Authenticated User!'
            response['data']['user_name'] = user.display_name

        except ExpiredIdTokenError:
            response['success'] = False
            response['message'] = 'Id Token Expired'

        except IntegrityError as e:
            response['success'] = False
            response['message'] = str(e)
            response['data']['id_token'] = id_token

        finally:
            # Deleting app instance
            firebase_admin.delete_app(firebase)

        return Response(response)


class UpdateLocation(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        response = {
            "success": True,
            'message': '',
            'data': {
                'failed_at': ''
            }
        }
        token_string = request.META['HTTP_AUTHORIZATION']
        id_token = token_string.split()[1]
        player = Player.objects.get(fire_token=id_token)

        locations_string = request.POST['locations']
        locations = json.loads(locations_string)
        for count, loc in enumerate(locations):
            quarantine = player.location.check_quarantine(loc)
            new_loc = Location.objects.get(player=player)
            if not quarantine:
                new_loc.latitude = loc['lat']
                new_loc.longitude = loc['long']
                new_loc.altitude = loc['alti']
                new_loc.start_time = datetime.strptime(loc['date_time'], "%m/%d/%Y %H:%M:%S")
                response['success'] = False
                if response['data']['failed_at'] == '':
                    response['data']['failed_at'] = loc['date_time']

            new_loc.last_updated = datetime.strptime(loc['date_time'], "%m/%d/%Y %H:%M:%S")
            new_loc.save()

        return Response(response)


class PlayerProfile(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        response = {
            "success": True,
            'message': 'Obtained User Profile!',
            'data': {}
        }

        token_string = request.META['HTTP_AUTHORIZATION']
        id_token = token_string.split()[1]
        player = Player.objects.filter(fire_token=id_token).first()
        if player is not None:
            response['data'] = {
                'id': player.id,
                'user_name': player.user_name,
                'photo_url': player.photo_url,
                'member_since': str(player.member_since),
                'city': player.city,
                'country': player.country,
                'total_points': str(player.score.total_points),
                'cur_streak': str(player.score.cur_streak),
                'days_quarantined': str(player.score.days_quarantined),
                'highest_streak': str(player.score.highest_streak),
                'last_updated': str(player.location.last_updated),
                'start_time': str(player.location.start_time),
            }
        else:
            response['success'] = False
            response['message'] = 'No user has this id token'
            response['data']['id_token'] = id_token

        return Response(response)


class Leaderboard(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        response = {
            "success": True,
            'message': 'Obtained User Profile!',
            'data': {}
        }

        token_string = request.META['HTTP_AUTHORIZATION']
        id_token = token_string.split()[1]

        score_arr = Score.objects.order_by('-total_points').all()[:5]
        response['data']['top'] = []
        for position, score in enumerate(score_arr):
            new_score = {
                'id': score.player.id,
                'user_name': score.player.user_name,
                'photo_url': score.player.photo_url,
                'total_points': str(score.total_points),
                'cur_streak': str(score.cur_streak),
                'days_quarantined': str(score.days_quarantined),
                'highest_streak': str(score.highest_streak),
                'last_updated': str(score.player.location.last_updated),
                'is_user': True if score.player.fire_token == id_token else False,
                'position': position
            }
            response['data']['top'].append(new_score)

        return Response(response)


# Testing database models

class PlayersViewSet(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
