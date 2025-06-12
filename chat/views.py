import datetime
import asyncio

from typing import AsyncGenerator

from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404 #, aget_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpRequest, StreamingHttpResponse, HttpResponse
from . import models
import json
from django.db.models import Q
from notifications.signals import notify
from .models import Message

import random

# def lobby(request: HttpRequest) -> HttpResponse:
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         if username:
#             request.session['username'] = username
#         else:
#             names = [
#                 "Horatio", "Benvolio", "Mercutio", "Lysander", "Demetrius", "Sebastian", "Orsino",
#                 "Malvolio", "Hero", "Bianca", "Gratiano", "Feste", "Antonio", "Lucius", "Puck", "Lucio",
#                 "Goneril", "Edgar", "Edmund", "Oswald"
#             ]
#             request.session['username'] = f"{random.choice(names)}-{hash(datetime.now().timestamp())}"
#
#         return redirect('chat')
#     else:
#         return render(request, 'lobby.html')

@login_required
def chat(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    # if not request.session.get('username'):
    #     return redirect('lobby')
    request.session['author'] = request.user.username
    recipient = kwargs.get('username') # User.objects.get(username=kwargs.get('username')). #get_object_or_404(User, username=kwargs.get('username'))
    request.session['recipient'] = recipient
    recipient = get_object_or_404(User, username=recipient)
    request.session['recipient_name'] = f'{recipient.profile.last_name} {recipient.profile.first_name}'
    return render(request, 'chat.html')

def create_message(request: HttpRequest, **kwargs) -> HttpResponse:
    content = request.POST.get("content")
    author = request.session.get("author")
    recipient = request.session.get("recipient")
    # print(content)
    # print(username)
    # print(recipient)

    if not author:
        return HttpResponse(status=403)

    author = get_object_or_404(User, username=author)
    recipient = get_object_or_404(User, username=recipient)
    #created_at = datetime.datetime.now()

    if content:
        msg = models.Message.objects.create(author=author, recipient=recipient, content=content)
        notify.send(author, recipient=recipient, verb='прислал(а) Вам новое сообщение.', action_object=msg)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=200)

async def stream_chat_messages(request: HttpRequest, *args, **kwargs) -> StreamingHttpResponse:
    """
    Streams chat messages to the client as we create messages.
    """
    async def event_stream():
        """
        We use this function to send a continuous stream of data
        to the connected clients.
        """
        async for message in get_existing_messages():
            yield message

        last_id = await get_last_message_id()
        author = await get_author()
        recipient = await get_recipient()

        # Continuously check for new messages
        while True:

            new_messages = models.Message.objects.filter(Q(author=author, recipient=recipient, id__gt=last_id) | Q(author=recipient, recipient=author, id__gt=last_id)).order_by('created_at').values(
                'id', 'author__profile__last_name', 'author__profile__first_name',  'content', 'created_at'
            )
            async for message in new_messages:
                yield f"data: {json.dumps(message, default=default)}\n\n"
                last_id = message['id']
            await asyncio.sleep(1)  # Adjust sleep time as needed to reduce db queries.

    async def get_existing_messages() -> AsyncGenerator:
        author = await get_author()
        recipient = await get_recipient()
        messages = models.Message.objects.filter(Q(author=author, recipient=recipient) | Q(author=recipient, recipient=author)).order_by('created_at').values( #author=request.session.get('author'), recipient=request.session.get('recipient')
            'id', 'author__profile__last_name', 'author__profile__first_name', 'content', 'created_at'
        )
        async for message in messages:
            yield f"data: {json.dumps(message, default=default)}\n\n"

    async def get_last_message_id() -> int:
        author = await get_author()
        recipient = await get_recipient()
        last_message = await models.Message.objects.filter(Q(author=author, recipient=recipient) | Q(author=recipient, recipient=author)).alast() #author=request.session.get('author'), recipient=request.session.get('recipient')
        return last_message.id if last_message else 0

    async def get_author() -> User:
        user = await sync_to_async(request.session.get)("author")
        author = await sync_to_async(models.User.objects.filter)(username=user)
        ret = await sync_to_async(author.first)()
        return ret

    async def get_recipient() -> User:
        # recipient = await models.User.objects.filter(username=request.session.recipient).first()
        user = await sync_to_async(request.session.get)("recipient")
        rec = await sync_to_async(models.User.objects.filter)(username=user)
        ret = await sync_to_async(rec.first)()
        return ret

    def default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat() #"#", "minutes"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')