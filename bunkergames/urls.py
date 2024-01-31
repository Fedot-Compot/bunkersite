from django.urls import path


from . import views

urlpatterns = [
    path('ready', views.ready),
    path('not-ready', views.not_ready),
    path('start', views.start_game),
    path('user_list', views.user_list),
    path('state', views.game_state),
    path('actions', views.game_actions),
    path('kick', views.kick_user)
]
