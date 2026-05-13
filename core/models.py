from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    color = models.CharField(max_length=7, default='#f0c040')
    emoji = models.CharField(max_length=10, default='👤')

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'emoji': instance.username[:2].upper()})

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)

class MealRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meal_records')
    date = models.DateField(default=timezone.now)
    lunch = models.BooleanField(null=True, blank=True)
    dinner = models.BooleanField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')

    def __str__(self):
        return f"{self.user.username}'s Meal Record for {self.date}"

class BazarList(models.Model):
    content = models.TextField(blank=True, default="")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Shared Bazar List"
