
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponse
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from bunkergames.models import Game
from bunkerusers.models import User
from django.db import connection


def get_game_context(request):
    game = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get('game_id', '')])[0]

    if not game:
        raise Http404()

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [game.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    game.can_start = all(game_user.ready for game_user in users)

    return {
        'gameData': game,
        'users': users,
        'user': user
    }


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


def kick_user_from_lobby(game_id, username):
    query = '''
    DELETE FROM bunkerusers_user
    USING bunkergames_game
    WHERE
        bunkergames_game.id = bunkerusers_user.game_id AND
        game_id = %s AND
        username = %s AND
        NOT bunkergames_game.started
    RETURNING bunkerusers_user.*;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query, [game_id, username])
        row = cursor.fetchone()

    return row

# Create your views here.


def ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    if not context['user']:
        return HttpResponseBadRequest()

    context['user'] = update_user_ready(
            context['user'].session_id,
            context['gameData'].id,
            True)

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange, ActionsGameStateChange"
    return response


def not_ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    if not context['user']:
        return HttpResponseBadRequest()

    context['user'] = update_user_ready(
            context['user'].session_id,
            context['gameData'].id,
            False)

    response = render(request, 'ready_button.html', context)
    response["HX-Trigger"] = "UserGameStateChange, ActionsGameStateChange"
    return response


def start_game(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    if not context['user']:
        return HttpResponseBadRequest()

    if context['user'].host:
        for game_user in context['users']:
            if not game_user.ready:
                raise PermissionDenied("Users are not ready")

        start_game_db(context['gameData'].id)
    else:
        raise PermissionDenied("User is not host")

    response = HttpResponse()
    response["HX-Trigger"] = "GameStateChange"
    return response


def kick_user(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    user = User.objects.raw(
            '''
            SELECT
                *
            FROM bunkerusers_user
            WHERE game_id = %s AND session_id = %s AND host
            ''',
            [request.GET.get('game_id', ''), request.session.session_key])[0]

    if not user:
        raise PermissionDenied("User not authorized")

    kicked_user = kick_user_from_lobby(
            request.GET.get('game_id', ''),
            request.GET.get('username', ''))

    if not kicked_user:
        return HttpResponseBadRequest()

    response = HttpResponse()
    response["HX-Trigger"] = "GameStateChange"
    return response


def game_state(request):
    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'game_view.html', context)
    return response


def game_actions(request):
    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'game_actions.html', context)
    return response


def user_list(request):
    try:
        context = get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'user_list.html', context)
    return response
