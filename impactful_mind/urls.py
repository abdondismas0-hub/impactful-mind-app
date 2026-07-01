"""
URL configuration for impactful_mind project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from library import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('maktaba/', views.maktaba,name='maktaba'),
    path('kozi/',views.online_courses,name='online_courses'),
    path('kozi/<int:course_id>/', views.course_detail,name='course_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard',views.dashboard_view,name='dashboard'),
    path('kuhusu_sisi',views.kuhusu_sisi_view,name='kuhusu_sisi'),
    path('mawasiliano',views.mawasiliano_view,name='mawasiliano'),
    path('gundua_zaidi',views.gundua_zaidi_view,name='gundua_zaidi'),
    path("course/<int:course_id>",views.course_detail,name="course_detail"),
    path('checkout/<int:course_id>',views.checkout,name='checkout'),

    path('', views.home_view, name='home'),
    path('maktaba/', views.maktaba, name='maktaba'),
    path('kozi/', views.online_courses, name='online_courses'),
    
    # Mabadiliko haya hapa chini ndiyo yenye umuhimu kwa kazi yako mpya
    path('kozi/<int:course_id>/', views.course_detail, name='course_detail'),
    
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Hii ndio link mpya ya malipo utaifungulia dirisha la malipo hapa
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    # Kazi zingine...,
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
