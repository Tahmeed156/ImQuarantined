from django.contrib.auth.models import User, Group
from rest_framework.serializers import ModelSerializer
from .models import *


class DynamicFieldsModelSerializer(ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ScoreSerializer(ModelSerializer):

    class Meta:
        model = Score
        fields = ('total_points', 'cur_streak', 'days_quarantined', 'highest_streak')


class LocationSerializer(ModelSerializer):

    class Meta:
        model = Location
        fields = ('latitude', 'longitude', 'altitude', 'last_updated')


class PlayerSerializer(ModelSerializer):

    score = ScoreSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ('user_name', 'fire_token', 'member_since', 'city', 'country',
                  'score', 'location')


