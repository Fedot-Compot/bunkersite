from django.shortcuts import render
from bunkerusers.models import User
from bunkergames.helpers import get_game_context


# Create your views here.
def index(request):
    query = '''
    SELECT
        bunkergames_game.*
    FROM bunkergames_game
    JOIN bunkerusers_user
        ON bunkerusers_user.game_id = bunkergames_game.id
    WHERE bunkerusers_user.session_id = %s
    '''

    games = User.objects.raw(query, [request.session.session_key])

    context = {
        'games': games
    }

    return render(request, "index.html", context)


def game(request):
    context = get_game_context(request)
    return render(request, "game.html", context)
