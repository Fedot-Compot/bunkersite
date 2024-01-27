from django.urls import path


from . import views

urlpatterns = [
    path('ready', views.ready),
    path('not-ready', views.not_ready),
    path('user_list', views.user_list)
]