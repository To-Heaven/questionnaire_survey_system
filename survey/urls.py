from django.urls import path, include, re_path

from survey import views

urlpatterns = [
    re_path('^login/$', views.login)
]
