from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import PlayerSerializer
from .models import Player


def index(request):
    return HttpResponse("Hello, plebs. Welcome to my API!")


class PlayerLogin(APIView):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request):
        # end_users = EndUser.objects.select_related('address').filter(user_type='repairer').all()
        # serializer = EndUserSerializer(end_users,
        # fields=[constants.Default.COL_ID, constants.EndUser.COL_ADDR],
        # many=True)
        # return Response(serializer.data)
        pass


# Testing database models

class PlayerViewSet(viewsets.ModelViewSet):

    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
