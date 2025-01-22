from django.db import models

# Create your models here.
class Session(models.Model):
    start_time = models.DateTimeField()


    def __str__(self):
        return f'{self.start_time}'
