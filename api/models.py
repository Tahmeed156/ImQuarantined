from django.contrib.gis.db import models
from django.utils import timezone


class Player (models.Model):
    user_name = models.CharField(max_length=128, blank=False, null=False)
    fire_token = models.CharField(max_length=2048, blank=False, null=False, unique=True)
    fire_uid = models.CharField(max_length=128, blank=False, null=False, unique=True)
    photo_url = models.CharField(max_length=256, blank=True, null=True)

    member_since = models.DateTimeField(editable=True)
    city = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.member_since = timezone.now()
        return super(Player, self).save(*args, **kwargs)

    def __str__(self):
        return self.user_name + ":" + self.fire_uid

    class Meta:
        verbose_name_plural = "Players"


class Score (models.Model):
    player = models.OneToOneField(Player, primary_key=True, on_delete=models.CASCADE)
    total_points = models.PositiveIntegerField(default=0)
    cur_streak = models.PositiveIntegerField(default=0)
    days_quarantined = models.PositiveIntegerField(default=0)
    highest_streak = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.player.user_name + ".score:" + str(self.total_points)

    class Meta:
        verbose_name_plural = 'Scores'


class Location (models.Model):
    player = models.OneToOneField(Player, primary_key=True, on_delete=models.CASCADE)
    latitude = models.DecimalField(decimal_places=10, max_digits=20, blank=True, null=True)
    longitude = models.DecimalField(decimal_places=10, max_digits=20, blank=True, null=True)
    altitude = models.DecimalField(decimal_places=10, max_digits=20, blank=True, null=True)
    last_updated = models.DateTimeField(editable=True)
    start_time = models.DateTimeField(editable=True)

    def check_quarantine(self, loc):

        if self.latitude == None and self.longitude == None and self.altitude == None:
            return True

        if abs(int(self.latitude * 10000) - int(loc['lat'] * 10000)) > 15:
            return False
        if abs(int(self.longitude * 10000) - int(loc['long'] * 10000)) > 15:
            return False
        # if abs(int(self.altitude * 10000) - int(loc['alti'] * 10000)) > 15:
        #     return False
        return True

    def save(self, *args, **kwargs):
        if not self.last_updated:
            self.last_updated = timezone.now()
            self.start_time = timezone.now()
        return super(Location, self).save(*args, **kwargs)

    def __str__(self):
        return self.player.user_name + ".location:" + \
               str(self.latitude) + ',' + str(self.longitude) + ', ' + str(self.altitude)

    class Meta:
        verbose_name_plural = 'Locations'

