from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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
