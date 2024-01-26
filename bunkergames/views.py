from django.http import HttpResponseRedirect
from django.shortcuts import render

from bunkergames.models import Game
from bunkerusers.models import User

# Create your views here.
def game(request):
    gameData = None
    try:
        gameData = Game.objects.get(id=request.GET.get("game_id", ""))
    except Game.DoesNotExist:
        return HttpResponseRedirect("/game/404.html")
    users = User.objects.filter(game_id=gameData.id)
    user = None
    try:
        user = users.get(session_key=request.session.session_key)
    except User.DoesNotExist:
        pass
    context = {'gameData': gameData, 'users': users, 'user': user }
    print(context, gameData.started)
    return render(request, "game.html", context)