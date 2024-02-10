from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponse
)
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from bunkerusers.models import User
from . import helpers

# Create your views here.


def ready(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    context = helpers.get_game_context(request)

    if not context['user']:
        return HttpResponseBadRequest()

    context['user'] = helpers.update_user_ready(
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
        context = helpers.get_game_context(request)
    except Http404:
        return Http404()

    if not context['user']:
        return HttpResponseBadRequest()

    context['user'] = helpers.update_user_ready(
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
        context = helpers.get_game_context(request)
    except Http404:
        return Http404()

    if not context['user']:
        return HttpResponseBadRequest()

    if context['user'].host:
        hasShowman = False
        for game_user in context['users']:
            if not game_user.ready:
                raise PermissionDenied("Users are not ready")
            if game_user.showman:
                hasShowman = True
        if not hasShowman:
            raise PermissionDenied("Game must have a host")

        helpers.start_game_db(context['gameData'].id)
    else:
        raise PermissionDenied("User is not host")

    response = HttpResponse()
    response["HX-Trigger"] = "GameStateChange"
    return response


def make_user_showman(request):
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

    success = helpers.change_showman_db(
            request.GET.get('game_id', ''),
            request.GET.get('username', ''))

    print(success)
    if not success:
        return HttpResponseBadRequest()

    response = HttpResponse()
    response["HX-Trigger"] = "UserGameStateChange"
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

    kicked_user = helpers.kick_user_from_lobby(
            request.GET.get('game_id', ''),
            request.GET.get('username', ''))

    if not kicked_user:
        return HttpResponseBadRequest()

    response = HttpResponse()
    response["HX-Trigger"] = "UserGameStateChange"
    return response


def game_state(request):
    try:
        context = helpers.get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'game_view.html', context)
    return response


def game_actions(request):
    try:
        context = helpers.get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'game_actions.html', context)
    return response


def user_list(request):
    try:
        context = helpers.get_game_context(request)
    except Http404:
        return Http404()

    response = render(request, 'user_list.html', context)
    return response
