from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import pika
import json
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from .models import User, Excursion, UserExcursion
from .serializers import (UserSerializer, ExcursionSerializer, 
                         UserExcursionSerializer, AddExcursionSerializer, 
                         MarkVisitedSerializer)


@extend_schema(
    request=UserSerializer,
    responses={201: UserSerializer}
)
@api_view(['POST'])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@extend_schema(
    request=AddExcursionSerializer,
    responses={201: ExcursionSerializer}
)
@api_view(['POST'])
def add_excursion(request):
    serializer = AddExcursionSerializer(data=request.data)
    if serializer.is_valid():
        excursion = serializer.save()
        
        # Send task to RabbitMQ for vectorization
        try:
            connection = pika.BlockingConnection(
                pika.URLParameters('amqp://guest:guest@rabbitmq:5672/')
            )
            channel = connection.channel()
            channel.queue_declare(queue='excursion_vectorization', durable=True)
            
            message = {
                'excursion_id': excursion.id,
                'short_description': excursion.short_description
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='excursion_vectorization',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                ))
            connection.close()
        except Exception as e:
            print(f"Error sending message to RabbitMQ: {e}")
        
        return Response(ExcursionSerializer(excursion).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_excursions(request):
    excursions = Excursion.objects.filter(is_active=True)
    serializer = ExcursionSerializer(excursions, many=True)
    return Response(serializer.data)


@extend_schema(
    request=MarkVisitedSerializer,
    responses={200: UserExcursionSerializer}
)
@api_view(['POST'])
def mark_visited(request):
    serializer = MarkVisitedSerializer(data=request.data)
    if serializer.is_valid():
        user_id = serializer.validated_data['user_id']
        excursion_id = serializer.validated_data['excursion_id']
        
        user = get_object_or_404(User, id=user_id)
        excursion = get_object_or_404(Excursion, id=excursion_id)
        
        user_excursion, created = UserExcursion.objects.get_or_create(
            user=user,
            excursion=excursion
        )
        
        return Response(UserExcursionSerializer(user_excursion).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_user_excursions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_excursions = UserExcursion.objects.filter(user=user)
    serializer = UserExcursionSerializer(user_excursions, many=True)
    return Response(serializer.data)
