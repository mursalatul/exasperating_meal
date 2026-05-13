from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import MealRecord
import datetime

def can_edit_lunch():
    now = timezone.localtime(timezone.now())
    # Deadline: 5:00 AM (30 min before 5:30 AM)
    deadline = now.replace(hour=5, minute=0, second=0, microsecond=0)
    return now < deadline

def can_edit_dinner():
    now = timezone.localtime(timezone.now())
    # Deadline: 4:00 PM (16:00)
    deadline = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return now < deadline

@login_required
def index(request):
    today = timezone.localtime(timezone.now()).date()
    users = User.objects.all().order_by('id')
    
    # Ensure every user has a record for today
    for user in users:
        MealRecord.objects.get_or_create(user=user, date=today)
        
    meal_records = MealRecord.objects.filter(date=today).select_related('user').order_by('user_id')
    
    context = {
        'meal_records': meal_records,
        'can_edit_lunch': can_edit_lunch(),
        'can_edit_dinner': can_edit_dinner(),
        'lunch_deadline': "5:00 AM",
        'dinner_deadline': "4:00 PM",
    }
    return render(request, 'index.html', context)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid password',
                'users': User.objects.all(),
                'selected_username': username
            })
            
    return render(request, 'login.html', {
        'users': User.objects.all()
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def update_meal(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    
    meal_type = request.POST.get('meal_type') # 'lunch' or 'dinner'
    value = request.POST.get('value') == 'true'
    today = timezone.localtime(timezone.now()).date()
    
    if meal_type == 'lunch':
        if not can_edit_lunch():
            return JsonResponse({'error': 'Lunch editing is closed'}, status=400)
        record, _ = MealRecord.objects.get_or_create(user=request.user, date=today)
        record.lunch = value
        record.save()
    elif meal_type == 'dinner':
        if not can_edit_dinner():
            return JsonResponse({'error': 'Dinner editing is closed'}, status=400)
        record, _ = MealRecord.objects.get_or_create(user=request.user, date=today)
        record.dinner = value
        record.save()
    else:
        return JsonResponse({'error': 'Invalid meal type'}, status=400)
    
    return JsonResponse({'success': True})
