from django.http import HttpResponseRedirect
from django.shortcuts import render
from bunkergames.models import Game
from bunkerusers.models import User
from django.contrib.sessions.models import Session
 
# Create your views here.
def index(request):
    session = None
    try:
        session = Session.objects.get(session_key=request.session.session_key)
    except Session.DoesNotExist:
        return render(request, "index.html")

    users = User.objects.filter(session_key=session)
    
    games = []

    for user in users:
        games.append(user.game_id)
    
    context = {
        'games': games
    }
    
    return render(request, "index.html", context)

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
    return render(request, "game.html", context)