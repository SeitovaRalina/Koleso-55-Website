from django.utils import timezone
from django.db.models import Count, Sum
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import ExcursionView
from .serializers import (
    ExcursionViewStartSerializer,
    ExcursionViewHeartbeatSerializer,
    ExcursionViewEndSerializer,
    ExcursionViewSerializer
)
from .services import get_similar_excursions, get_user_recommendations, publish_recommendation_event
from excursions.models import Excursion
from excursions.serializers import ExcursionInternalSerializer
from bookings.models import TourOrder


@extend_schema(
    summary="Начать отслеживание просмотра экскурсии",
    description="Создает запись о начале просмотра экскурсии",
    request=ExcursionViewStartSerializer,
    responses={201: ExcursionViewSerializer}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def view_start(request):
    """
    POST /api/analytics/view/start/
    Создает запись о начале просмотра экскурсии
    """
    serializer = ExcursionViewStartSerializer(data=request.data)
    if serializer.is_valid():
        excursion_id = serializer.validated_data['excursion_id']
        session_id = serializer.validated_data['session_id']
        source = serializer.validated_data['source']
        
        # Получаем пользователя из запроса (если аутентифицирован)
        user = request.user if request.user.is_authenticated else None
        
        # Создаем запись о просмотре
        view = ExcursionView.objects.create(
            user=user,
            excursion_id=excursion_id,
            session_id=session_id,
            source=source
        )
        
        response_serializer = ExcursionViewSerializer(view)
        return Response(
            {'view_id': view.id, **response_serializer.data},
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Обновить длительность просмотра",
    description="Обновляет длительность просмотра по heartbeats",
    request=ExcursionViewHeartbeatSerializer,
    responses={200: {"type": "object", "properties": {"success": {"type": "boolean"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def view_heartbeat(request):
    """
    POST /api/analytics/view/heartbeat/
    Обновляет длительность просмотра
    """
    serializer = ExcursionViewHeartbeatSerializer(data=request.data)
    if serializer.is_valid():
        view_id = serializer.validated_data['view_id']
        elapsed_seconds = serializer.validated_data['elapsed_seconds']
        
        try:
            view = ExcursionView.objects.get(id=view_id)
            view.duration_seconds += elapsed_seconds
            view.save(update_fields=['duration_seconds'])
            
            return Response({'success': True}, status=status.HTTP_200_OK)
        except ExcursionView.DoesNotExist:
            return Response(
                {'error': 'Запись о просмотре не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Завершить просмотр экскурсии",
    description="Завершает просмотр и публикует событие в RabbitMQ если длительность > 3с",
    request=ExcursionViewEndSerializer,
    responses={200: {"type": "object", "properties": {"success": {"type": "boolean"}}}}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def view_end(request):
    """
    POST /api/analytics/view/end/
    Завершает просмотр и публикует событие в RabbitMQ
    """
    serializer = ExcursionViewEndSerializer(data=request.data)
    if serializer.is_valid():
        view_id = serializer.validated_data['view_id']
        
        try:
            view = ExcursionView.objects.get(id=view_id)
            
            # Публикуем событие только если просмотр длился более 3 секунд
            if view.duration_seconds > 3:
                publish_recommendation_event(
                    event_type='view' if view.duration_seconds <= 40 else 'long_view',
                    user_id=view.user.id if view.user else None,
                    session_id=view.session_id,
                    excursion_id=view.excursion.id,
                    duration_seconds=view.duration_seconds,
                    source=view.source,
                )
                
                # Помечаем как обработанное
                view.processed_for_recommendations = True
                view.save(update_fields=['processed_for_recommendations'])
            
            return Response({'success': True}, status=status.HTTP_200_OK)
            
        except ExcursionView.DoesNotExist:
            return Response(
                {'error': 'Запись о просмотре не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@extend_schema(
    summary="Получить все экскурсии для микросервиса",
    description="Внутренний API endpoint для микросервиса рекомендаций",
    responses={200: ExcursionInternalSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def internal_excursions(request):
    """
    GET /api/internal/excursions/
    Возвращает все активные экскурсии с полными описаниями
    """
    excursions = Excursion.objects.filter(is_active=True).select_related('category')
    serializer = ExcursionInternalSerializer(excursions, many=True)
    return Response(serializer.data)

@csrf_exempt
@extend_schema(
    summary="Получить популярность экскурсий",
    description="Возвращает количество заказов для каждой экскурсии (исключая отмененные)",
    responses={
        200: {
            "type": "object",
            "description": "Словарь с ID экскурсий и их количеством заказов",
            "example": {
                "1": 42,
                "2": 28,
                "3": 15
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def internal_popularity(request):
    """
    GET /api/internal/popularity/
    Возвращает {excursion_id: bookings_count}
    """
    # Получаем количество заказов для каждой экскурсии (исключая отмененные)
    popularity = {}
    
    orders_data = TourOrder.objects.exclude(
        status='cancelled'
    ).values('excursion_id').annotate(
        bookings_count=Count('id')
    ).order_by('-bookings_count')
    
    for item in orders_data:
        popularity[item['excursion_id']] = item['bookings_count']

    return Response(popularity)


@api_view(['GET'])
@permission_classes([AllowAny])
def recommendations_for_user(request, user_id):
    top_k = int(request.query_params.get('top_k', 20))
    return Response({"recommendations": get_user_recommendations(user_id, top_k=top_k)})


@api_view(['GET'])
@permission_classes([AllowAny])
def similar_for_excursion(request, excursion_id):
    top_k = int(request.query_params.get('top_k', 10))
    return Response({"similar_excursions": get_similar_excursions(excursion_id, top_k=top_k)})
