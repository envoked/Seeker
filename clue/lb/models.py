from django.db import models

partners = ('citysearch', 'citysearch')

class ShineModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        abstract = True

class Shiner(ShineModel):
    name = models.CharField(max_length=255)
    partner = models.ChoiceField(choices=partners)
    partner_id = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    lat = models.FloatField(max_length)
    lon = models.FloatField(max_length)