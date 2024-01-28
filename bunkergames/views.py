
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponse
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.contrib.sessions.models import Session
from bunkergames.models import Game
from bunkerusers.models import User

# Create your views here.


def ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    session = Session.objects.get(session_key=request.session.session_key)
    try:
        game = Game.objects.get(id=request.GET.get('game_id', ''))
    except Game.DoesNotExist:
        return Http404()
    try:
        user = User.objects.get(game_id=game, session_key=session)
    except User.DoesNotExist:
        return Http404()
    user.ready = True
    user.save()

    users = User.objects.filter(game_id=game)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange"
    return response


def not_ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    session = Session.objects.get(session_key=request.session.session_key)
    try:
        game = Game.objects.get(id=request.GET.get('game_id', ''))
    except Game.DoesNotExist:
        return Http404()
    try:
        user = User.objects.get(game_id=game, session_key=session)
    except User.DoesNotExist:
        return Http404()
    user.ready = False
    user.save()

    users = User.objects.filter(game_id=game)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange"
    return response


def start_game(request):

    if request.method != 'POST':
        return HttpResponseBadRequest()
    session = Session.objects.get(session_key=request.session.session_key)
    try:
        game = Game.objects.get(id=request.GET.get('game_id', ''))
    except Game.DoesNotExist:
        return Http404()

    try:
        user = User.objects.get(game_id=game, session_key=session)
    except User.DoesNotExist:
        raise PermissionDenied("User not registered")

    if user.host:
        game.started = True
        game.save()
    else:
        raise PermissionDenied("User is not host")

    response = HttpResponse()
    response["HX-Trigger"] = "GameStateChange"
    return response


def game_state(request):
    session = Session.objects.get(session_key=request.session.session_key)
    try:
        game = Game.objects.get(id=request.GET.get('game_id', ''))
    except Game.DoesNotExist:
        return Http404()

    user = None

    try:
        user = User.objects.get(game_id=game, session_key=session)
    except User.DoesNotExist:
        pass

    users = User.objects.filter(game_id=game)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'game_view.html', context)
    return response


def user_list(request):
    session = Session.objects.get(session_key=request.session.session_key)
    try:
        game = Game.objects.get(id=request.GET.get('game_id', ''))
    except Game.DoesNotExist:
        return Http404()

    user = None

    try:
        user = User.objects.get(game_id=game, session_key=session)
    except User.DoesNotExist:
        pass

    users = User.objects.filter(game_id=game)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'user_list.html', context)
    return response
