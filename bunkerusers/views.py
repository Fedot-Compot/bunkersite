from django.shortcuts import render
from django.http.response import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from requests import session
from .models import Game, User, Session

class HTTPResponseHXRedirect(HttpResponseRedirect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self["HX-Redirect"] = self["Location"]

    status_code = 200
    
# Create your views here.


@csrf_exempt
def login(request):
    if(request.method != "POST"):
        return Http404()
    username = request.POST['username']
    game_id = request.GET.get("game_id", '')
    game = None
    host = False
    if game_id:
        try:
            game = Game.objects.get(id=game_id)
            game_id = game.id
        except Game.DoesNotExist:
            return Http404("No game found with given game_id")
    else:
        game = Game.objects.create()
        game_id = game.id
        host = True
    
    # game: ok, found or created
    if not request.session.exists(request.session.session_key):
        request.session.create() 
    session = Session.objects.get(session_key = request.session.session_key)
    try:
        User.objects.get(game_id=game, session_key=session)
        return HTTPResponseHXRedirect(redirect_to="/game?game_id=" + game_id)
    except User.DoesNotExist:
        pass
    
    # current session has no user in this game
    
    try:
        User.objects.create(game_id=game, username=username, host=host, session_key = session)
    except IntegrityError:
        return HttpResponseBadRequest()
    
    # user: ok
    
    return HTTPResponseHXRedirect(redirect_to="/game?game_id=" + game_id)