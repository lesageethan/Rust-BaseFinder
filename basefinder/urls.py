from django.contrib import admin
from django.urls import path
from table import views
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('about/', views.about),
    path('submit/', views.submit),
    path('efficiency_leaderboard/', views.efficiency_leaderboard),
    path('defense_leaderboard/', views.defense_leaderboard),
    path('all_bases/', views.all_bases),
    path('base_id/<id>/', views.base_id),
    path('sponsor/', views.sponsor),
    path('sign_up/', views.sign_up),
    path('log_in/', views.log_in),
    path('log_out/', views.log_out),
    path("ads.txt", RedirectView.as_view(url=staticfiles_storage.url("ads.txt")))
]
