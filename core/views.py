from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import MealRecord, BazarList, Profile
import datetime

def get_target_dates():
    now = timezone.localtime(timezone.now())
    # Lunch switches to tomorrow at 6:00 AM
    lunch_date = now.date()
    if now.hour >= 6:
        lunch_date += datetime.timedelta(days=1)
    
    # Dinner switches to tomorrow at 6:00 PM (18:00)
    dinner_date = now.date()
    if now.hour >= 18:
        dinner_date += datetime.timedelta(days=1)
        
    return lunch_date, dinner_date

@login_required
def index(request):
    now = timezone.localtime(timezone.now())
    lunch_date, dinner_date = get_target_dates()
    
    # Ensure every user has a profile and records for relevant dates
    users = User.objects.all().order_by('id')
    for user in users:
        # 1. Profile check
        Profile.objects.get_or_create(user=user, defaults={'emoji': user.username[:2].upper()})
        
        # 2. Meal records check (today/tomorrow)
        for d in [now.date(), now.date() + datetime.timedelta(days=1)]:
            record, created = MealRecord.objects.get_or_create(user=user, date=d)
            if created:
                prev_record = MealRecord.objects.filter(user=user, date__lt=d).order_by('-date').first()
                if prev_record:
                    record.lunch = prev_record.lunch
                    record.dinner = prev_record.dinner
                    record.save()

    # Refetch with select_related now that profiles exist
    users = User.objects.all().order_by('id').select_related('profile')
    display_records = []
    for user in users:
        l_rec = MealRecord.objects.get(user=user, date=lunch_date)
        d_rec = MealRecord.objects.get(user=user, date=dinner_date)
        display_records.append({
            'user': user,
            'profile': user.profile,
            'lunch': l_rec.lunch,
            'dinner': d_rec.dinner,
        })
        
    bazar_list, _ = BazarList.objects.get_or_create(id=1)
    
    context = {
        'meal_records': display_records,
        'bazar_list': bazar_list,
        'lunch_date': lunch_date,
        'dinner_date': dinner_date,
        'is_lunch_tomorrow': lunch_date > now.date(),
        'is_dinner_tomorrow': dinner_date > now.date(),
        'user_profile': request.user.profile,
    }
    return render(request, 'index.html', context)

# ... (login/logout views)

@login_required
def update_profile(request):
    if request.method == 'POST':
        color = request.POST.get('color')
        emoji = request.POST.get('emoji')
        old_pass = request.POST.get('old_password')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        profile, _ = Profile.objects.get_or_create(user=request.user)
        
        # Password change logic
        if old_pass or new_pass:
            if not old_pass or not new_pass or not confirm_pass:
                return JsonResponse({'success': False, 'error': 'All fields required! Don\'t be lazy. 🥱'}, status=400)
            if not request.user.check_password(old_pass):
                return JsonResponse({'success': False, 'error': 'Nice try, impostor! That\'s not your password. 🕵️‍♂️'}, status=400)
            if new_pass != confirm_pass:
                return JsonResponse({'success': False, 'error': 'Passwords don\'t match! Did you have too much sugar? 🍬'}, status=400)
            
            request.user.set_password(new_pass)
            request.user.save()
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, request.user)

        if color:
            profile.color = color
        if emoji:
            profile.emoji = emoji
        profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

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
    
    lunch_date, dinner_date = get_target_dates()
    
    if meal_type == 'lunch':
        record, _ = MealRecord.objects.get_or_create(user=request.user, date=lunch_date)
        record.lunch = value
        record.save()
        # To keep "Carry Forward" working for future days, we could update the latest record
        # But for now, just following the user's date logic
    elif meal_type == 'dinner':
        record, _ = MealRecord.objects.get_or_create(user=request.user, date=dinner_date)
        record.dinner = value
        record.save()
    else:
        return JsonResponse({'error': 'Invalid meal type'}, status=400)
    
    return JsonResponse({'success': True})

@login_required
def update_bazar(request):
    if request.method == 'POST':
        content = request.POST.get('content', '')
        bazar_list, _ = BazarList.objects.get_or_create(id=1)
        bazar_list.content = content
        bazar_list.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
