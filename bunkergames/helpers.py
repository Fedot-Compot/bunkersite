from django.http import (
    Http404,
)
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

    game.can_start = all(game_user.ready for game_user in users) and \
        any(game_user.showman for game_user in users)

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


def change_showman_db(game_id, username):
    query = '''
    UPDATE bunkerusers_user
    SET showman = CASE WHEN username = %s THEN true ELSE false END
    WHERE game_id = %s
    '''
    with connection.cursor() as cursor:
        try:
            cursor.execute(query, [username, game_id])
        except Exception:
            return False

    return True


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

