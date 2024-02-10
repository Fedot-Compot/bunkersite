from django.db import models
from django.core.validators import MinLengthValidator
import uuid


def generate_id():
    return str(uuid.uuid4()).replace('-', '')


class Game(models.Model):
    id = models.CharField(
            max_length=32,
            primary_key=True,
            default=generate_id,
            validators=[MinLengthValidator(32)])
    started = models.BooleanField(default=False)
