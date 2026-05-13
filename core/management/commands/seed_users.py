from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import MealRecord

class Command(BaseCommand):
    help = 'Seeds the initial users and meal records'

    def handle(self, *args, **options):
        # New user list with fixed passwords
        user_data = {
            'Pallob': '0012',
            'Naim': '7745',
            'Yousuf': '4577',
            'Swadhin': '1200',
            'Rion': '0999',
            'Labib': '9990',
            'Zonaid': '1222',
            'Nazmul': '2221'
        }

        # Clear existing users to avoid confusion if names changed
        # (Optional: remove if you want to keep old users)
        # User.objects.all().delete()

        for username, password in user_data.items():
            user, created = User.objects.get_or_create(username=username)
            user.set_password(password)
            user.save()
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated user: {username}'))
            
            MealRecord.objects.get_or_create(user=user)
        
        self.stdout.write(self.style.SUCCESS('Seeding completed!'))
