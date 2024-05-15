from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import scholarship_list, central, state, private, international, edit_view, confirm_delete
from .views import central_result, state_result, private_result, international_result
from .views import search_result, central_search_result, state_search_result, private_search_result, international_search_result, open_applications_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home,name="home"),
    path('index/',views.index,name="index"),
    path('signup/',views.signup,name="signup"),
    path('signin/',views.signin,name="signin"),
    path('edit/', edit_view, name='edit_page'),
    path('guide/',views.guide,name='guide'),
    path('open-applications/', open_applications_view, name='open_applications'),
    path('edit/confirm_delete/', confirm_delete, name='confirm_delete'),
    path('signout',views.signout,name="signout"),
    path('central/', central, name='central_view'),
    path('state/', state, name='state_view'),
    path('private/', private, name='private_view'),
    path('international/', international, name='international_view'),
    path('activate/<uidb64>/<token>/',views.activate,name="activate"),
    path('scholarships/', scholarship_list, name='scholarship_list'),
    path('central/result/', central_result, name='central_result'),
    path('state/result/', state_result, name='state_result'),
    path('private/result/', private_result, name='private_result'),
    path('international/result/', international_result, name='international_result'),
    path('search_result/', search_result, name='search_result'),
    path('central_search_result/',central_search_result, name='central_search_result'),
    path('state_search_result/',state_search_result, name='state_search_result'),
    path('private_search_result/',private_search_result, name='private_search_result'),
    path('international_search_result/',international_search_result, name='international_search_result'),
    path('password_reset/',auth_views.PasswordResetView.as_view(),name='password_reset'), 
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/done/',auth_views.PasswordResetCompleteView.as_view(),name='password_reset_complete'),
    re_path(r'^static/(?P<path>.*)$',serve,{'document_root':settings.STATIC_ROOT}),
   
] 



    