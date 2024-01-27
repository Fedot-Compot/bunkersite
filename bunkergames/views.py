from telnetlib import GA
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from bunkergames.models import Game
from bunkerusers.models import User

# Create your views here.

@csrf_exempt
def ready(request):
    if(request.method != 'POST'):
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
    
    response = render(request, 'game_view.html', {'gameData': game, 'users': users, 'user': user})
    response["HX-Trigger"] = "game-user-state-change"
    return response

@csrf_exempt
def not_ready(request):
    if(request.method != 'POST'):
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
    
    response = render(request, 'game_view.html', {'gameData': game, 'users': users, 'user': user})
    response["HX-Trigger"] = "game-user-state-change"
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
    return render(request, 'user_list.html', {'gameData': game, 'users': users, 'user': user})