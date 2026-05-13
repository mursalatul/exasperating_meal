from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update_meal/', views.update_meal, name='update_meal'),
    path('update_bazar/', views.update_bazar, name='update_bazar'),
    path('update_profile/', views.update_profile, name='update_profile'),
]
