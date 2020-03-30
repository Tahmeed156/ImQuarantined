import json
from datetime import datetime, timezone

import pytz
from django.db import IntegrityError
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
            reverse_secs = 86400 - secs
            response['data'] = {
                'hr': (reverse_secs // 3600),
                'min': (reverse_secs // 60) % 60,
                'sec': reverse_secs % 60,
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
            player = Player.objects.filter(fire_uid=uid).first()
            if not player:
                # Doesn't exist, create new one
                player = Player(
                    user_name=user.display_name,
                    fire_uid=uid,
                    photo_url=user.photo_url
                )
            # Updating token, regardless of user existence
            player.fire_token = id_token
            player.save()

            loc = Location(player=player)
            score = Score(player=player)
            loc.save()
            score.save()

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
        loc_arr = json.loads(locations_string)

        for count, loc in enumerate(loc_arr):
            quarantine = player.location.check_quarantine(loc)
            local_tz = pytz.timezone("UTC")
            utc_dt = datetime.utcfromtimestamp(loc['date_time']).replace(tzinfo=pytz.utc)
            new_time = local_tz.normalize(utc_dt.astimezone(local_tz))

            if not quarantine:
                # Renew location and timing attributes
                player.location.latitude = loc['lat']
                player.location.longitude = loc['long']
                player.location.altitude = loc['alti']
                player.location.start_time = new_time

                # Return failed status & first failure time
                response['success'] = False
                if response['data']['failed_at'] == '':
                    response['data']['failed_at'] = loc['date_time']

                player.score.cur_streak = 0
                player.score.confirmations_today = 0
            else:
                # Checking if score will increase
                time_diff = new_time - player.location.start_time
                if time_diff.seconds > 86400 * (player.score.cur_streak + 1):
                    # Another day has passed!
                    player.score.cur_streak += 1
                    player.score.total_points += 50 + (10 * player.score.cur_streak)
                    player.score.days_quarantined += 1

                    if player.score.confirmations_today < 3:
                        player.score.total_points += 0
                    if player.score.confirmations_today < 5:
                        player.score.total_points += 30
                    elif player.score.confirmations_today < 10:
                        player.score.total_points += 60
                    else:
                        player.score.total_points += 100
                    player.score.confirmations_today = 0

                    if player.score.cur_streak > player.score.highest_streak:
                        player.score.highest_streak = player.score.cur_streak
                    player.score.save()

            player.location.last_updated = new_time
            player.location.save()
            player.score.save()

        return Response(response)


class PlayerConfirmation(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        response = {
            "success": True,
            'message': 'New confirmation added!',
            'data': {}
        }

        token_string = request.META['HTTP_AUTHORIZATION']
        id_token = token_string.split()[1]
        player = Player.objects.filter(fire_token=id_token).first()

        time_string = request.POST['date-time']
        new_time = datetime.strptime(time_string, "%d/%m/%Y %H:%M:%S")
        time_diff = new_time - player.score.last_confirmed

        if time_diff.seconds > 3600:
            player.score.confirmations_today += 1
            player.score.last_confirmed = new_time
            player.score.save()
        else:
            response['success'] = False
            response['message'] = 'New Confirmation Not Possible'
            response['data']['time_passed'] = {
                'min': (time_diff.seconds // 60) % 60,
                'sec': time_diff.seconds % 60
            }

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
