from django.http.response import (
        Http404,
        HttpResponseRedirect,
        HttpResponseBadRequest)
from django.views.decorators.csrf import csrf_exempt
from .models import Game, User
from django.shortcuts import render
from django.db import connection


class HttpResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]
    status_code = 200


def create_user(game_id, username, session_id, host):
    query = '''
    INSERT INTO bunkerusers_user
        (game_id , session_id , username, host, showman)
    SELECT
        %s,
        %s,
        %s,
        %s::bool,
        %s::bool
    WHERE NOT EXISTS (
        SELECT
            1
        FROM bunkerusers_user
        WHERE
            username = %s AND
            game_id = %s
    )
    RETURNING  * ;
    '''
    data = [game_id, session_id, username, host, host, username, game_id]
    with connection.cursor() as cursor:
        cursor.execute(query, data)
        row = cursor.fetchone()
    return row


# Create your views here.
def login(request):
    if request.method != "POST":
        return Http404()
    username = request.POST['username']
    game_id = request.GET.get("game_id", '')
    game = None
    host = False
    if game_id:
        game = Game.objects.raw(
                "SELECT * FROM bunkergames_game WHERE id = %s",
                [game_id]
                )[0]
        if not game:
            return Http404("No game found with given game_id")
    else:
        game = Game.objects.create()
        game_id = game.id
        host = True

    query = '''
    SELECT
        *
    FROM bunkerusers_user
    WHERE game_id = %s AND session_id = %s
    '''

    user = User.objects.raw(query, [game_id, request.session.session_key])
    if len(user):
        return HttpResponseHXRedirect(redirect_to="/game?game_id="+game_id)

    # current session has no user in this game
    query = '''
    SELECT
        COUNT(*) as "count"
    FROM bunkerusers_user
    WHERE game_id = %s AND username = %s
    '''

    if not request.session.exists(request.session.session_key):
        request.session.create()

    user = create_user(game_id, username, request.session.session_key, host)
    if not user:
        context = {
            'taken': True,
            'username': username,
            'gameData': game
            }
        return render(request, "enter_lobby.html", context)

    # user: ok

    return HttpResponseHXRedirect(redirect_to="/game?game_id="+game_id)
