from django.contrib.gis.db import models
from django.utils import timezone


class Player (models.Model):
    user_name = models.CharField(max_length=128, blank=False, null=False)
    fire_token = models.CharField(max_length=2048, blank=False, null=False, unique=True)
    member_since = models.DateTimeField(editable=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.member_since = timezone.now()
        return super(Player, self).save(*args, **kwargs)

    def __str__(self):
        return self.user_name + ":" + self.city + ":" + self.fire_token

    class Meta:
        verbose_name_plural = "Players"


class Score (models.Model):
    player = models.OneToOneField(Player, primary_key=True, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField()
    cur_streak = models.PositiveIntegerField()
    days_quarantined = models.PositiveIntegerField()
    highest_streak = models.PositiveIntegerField

    def __str__(self):
        return self.player.user_name + ".score:" + str(self.total_points)

    class Meta:
        verbose_name_plural = 'Scores'


class Location (models.Model):
    player = models.OneToOneField(Player, primary_key=True, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=10, max_digits=20)
    longitude = models.DecimalField(decimal_places=10, max_digits=20)
    altitude = models.DecimalField(decimal_places=10, max_digits=20)
    last_updated = models.DateTimeField(editable=True)

    def save(self, *args, **kwargs):
        if not self.last_updated:
            self.last_updated = timezone.now()
        return super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return self.player.user_name + ".location:" + \
               str(self.latitude) + ',' + str(self.longitude) + ', ' + str(self.altitude)

    class Meta:
        verbose_name_plural = 'Locations'

