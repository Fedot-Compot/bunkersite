
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
from django.db import connection


def start_game_db(game_id):
    query = '''
    UPDATE bunkergames_game
    SET started = true
    WHERE id = %s
    RETURNING *;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query, [game_id])
        row = cursor.fetchone()
    return row


def update_user_ready(session_id, game_id, ready):
    query = '''
    UPDATE bunkerusers_user
    SET ready = %s
    WHERE session_id = %s AND game_id = %s
    RETURNING *;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query, [ready, session_id, game_id])
        row = cursor.fetchone()
    return row

# Create your views here.


def ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    if not user:
        return HttpResponseBadRequest()

    user = update_user_ready(user.session_id, user.game_id, True)

    game.can_start = all(game_user.ready for game_user in users)
    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange, ActionsGameStateChange"
    return response


def not_ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    if not user:
        return HttpResponseBadRequest()

    user = update_user_ready(user.session_id, user.game_id, False)

    game.can_start = all(game_user.ready for game_user in users)
    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange, ActionsGameStateChange"
    return response


def start_game(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    if not user:
        return HttpResponseBadRequest()

    if user.host:
        for game_user in users:
            if not game_user.ready:
                raise PermissionDenied("Users are not ready")

        start_game_db(game.id)
    else:
        raise PermissionDenied("User is not host")

    response = HttpResponse()
    response["HX-Trigger"] = "GameStateChange"
    return response


def game_state(request):
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    game.can_start = all(game_user.ready for game_user in users)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'game_view.html', context)
    return response


def game_actions(request):
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    game.can_start = all(game_user.ready for game_user in users)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'game_actions.html', context)
    return response


def user_list(request):
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        return Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    game.can_start = all(game_user.ready for game_user in users)

    context = {'gameData': game, 'users': users, 'user': user}

    response = render(request, 'user_list.html', context)
    return response
