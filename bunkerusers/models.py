from django.db import models
from bunkergames.models import Game
from django.contrib.sessions.models import Session


# Create your models here.
class User(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    username = models.CharField(max_length=32)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    host = models.BooleanField(db_default=False, default=False)
    showman = models.BooleanField(db_default=False, default=False)
    ready = models.BooleanField(db_default=False, default=False)
    data = models.JSONField(blank=True, null=True)

    class Meta:
        unique_together = (
            ('game', 'username'),
            ('game', 'session')
        )
