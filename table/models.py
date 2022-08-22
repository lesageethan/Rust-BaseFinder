from django.db import models

# Create your models here.

class base(models.Model):
    name = models.CharField(max_length=32)
    link = models.CharField(max_length=64)
    creator = models.CharField(max_length=32)
    group_size = models.IntegerField()

    build_cost_stone = models.IntegerField()
    build_cost_frags = models.IntegerField()
    build_cost_hqm = models.IntegerField()
    build_cost_scrap = models.IntegerField()

    upkeep_cost_stone = models.IntegerField()
    upkeep_cost_frags = models.IntegerField()
    upkeep_cost_hqm = models.IntegerField()
    upkeep_cost_scrap = models.IntegerField()

    raid_cost = models.IntegerField()
    efficiency_score = models.FloatField()

    feature_1 = models.CharField(max_length=32)
    feature_2 = models.CharField(max_length=32)
    feature_3 = models.CharField(max_length=32)

    fortify_link = models.CharField(max_length=32)

class hit(models.Model):
    page = models.CharField(max_length=16)
    time = models.TimeField(auto_now=True)

class rating(models.Model):
    base_foreign = models.IntegerField(default=1)
    account_foreign = models.IntegerField()
    stars = models.IntegerField()
    content = models.CharField(max_length=512)