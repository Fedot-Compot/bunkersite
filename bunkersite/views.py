from django.http import HttpResponseRedirect
from django.shortcuts import render
from bunkergames.models import Game
from bunkerusers.models import User


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
    gameData = Game.objects.raw(
            "SELECT * FROM bunkergames_game WHERE id = %s",
            [request.GET.get("game_id", "")])[0]

    if not gameData:
        return HttpResponseRedirect("/game/404.html")

    users = User.objects.raw(
            "SELECT * FROM bunkerusers_user WHERE game_id = %s",
            [gameData.id])
    user = None

    for other in users:
        if other.session_id == request.session.session_key:
            user = other

    gameData.can_start = all(game_user.ready for game_user in users)

    context = {'gameData': gameData, 'users': users, 'user': user}
    return render(request, "game.html", context)
