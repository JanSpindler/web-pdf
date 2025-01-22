import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Session
from .serializers import SessionSerializer


@api_view(['POST'])
def create_session(request):
    time = datetime.datetime.now()
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    session = Session.objects.create(start_time=time_str)
    session.save()
    return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)


def get_session(request, id):
    try:
        session = Session.objects.get(id=id)
        return Response(SessionSerializer(session).data, status=status.HTTP_200_OK)
    except Session.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


def delete_session(request, id):
    try:
        session = Session.objects.get(id=id)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Session.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'DELETE'])
def session_detail(request, id):
    if request.method == 'GET':
        return get_session(request, id)
    elif request.method == 'DELETE':
        return delete_session(request, id)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
