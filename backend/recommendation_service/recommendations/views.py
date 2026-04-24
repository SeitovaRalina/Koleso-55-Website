import os
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
import chromadb
from chromadb.config import Settings
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from django.shortcuts import get_object_or_404
from .models import User, Excursion, UserExcursion
from .serializers import UserSerializer, ExcursionSerializer, UserExcursionSerializer, MarkVisitedSerializer

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.chroma_client = None
        self.collection = None
        self.init_chromadb()
    
    def init_chromadb(self):
        chromadb_url = os.getenv('CHROMADB_URL', 'http://localhost:8000')
        
        # Use Settings to disable authentication
        settings = chromadb.config.Settings(
            allow_reset=False,
            anonymized_telemetry=False
        )
        
        self.chroma_client = chromadb.HttpClient(
            host=chromadb_url.split('//')[1].split(':')[0], 
            port=int(chromadb_url.split(':')[-1]),
            settings=settings
        )
        try:
            self.collection = self.chroma_client.get_or_create_collection("excursions")
        except Exception as e:
            print(f"Error creating/getting collection: {e}")
            self.collection = self.chroma_client.create_collection("excursions")
    
    def get_user_visited_excursions(self, user_id):
        """Get all excursions visited by a user"""
        try:
            user_excursions = UserExcursion.objects.filter(user_id=user_id)
            visited_ids = [ue.excursion_id for ue in user_excursions]
            print(f"DEBUG: User {user_id} visited excursions: {visited_ids}")
            return visited_ids
        except Exception as e:
            print(f"DEBUG: Error getting user visited excursions: {e}")
            return []
    
    def get_cosine_similarity(self, visited_ids, candidate_ids):
        """Calculate cosine similarity between visited and candidate excursions"""
        try:
            print(f"DEBUG: Calculating cosine similarity for visited: {visited_ids}, candidates: {candidate_ids}")
            
            # Get vectors for visited excursions
            visited_results = self.collection.get(
                ids=[str(id) for id in visited_ids],
                include=['embeddings', 'metadatas']
            )
            
            # Get vectors for candidate excursions
            candidate_results = self.collection.get(
                ids=[str(id) for id in candidate_ids],
                include=['embeddings', 'metadatas']
            )
            
            print(f"DEBUG: Visited results: {len(visited_results['embeddings'] or [])} embeddings")
            print(f"DEBUG: Candidate results: {len(candidate_results['embeddings'] or [])} embeddings")
            
            if not visited_results['embeddings'] or not candidate_results['embeddings']:
                print("DEBUG: No embeddings found, returning zero similarities")
                # Return zero similarities if no embeddings
                similarities = {}
                for candidate_id in candidate_ids:
                    similarities[candidate_id] = 0.0
                return similarities
            
            # Calculate average vector of visited excursions
            visited_vectors = np.array(visited_results['embeddings'])
            avg_visited_vector = np.mean(visited_vectors, axis=0)
            
            # Calculate similarity with each candidate
            similarities = {}
            candidate_vectors = np.array(candidate_results['embeddings'])
            candidate_ids_str = [str(id) for id in candidate_ids]
            
            for i, candidate_vector in enumerate(candidate_vectors):
                candidate_id = int(candidate_ids_str[i])
                # Reshape vectors for cosine_similarity
                similarity = cosine_similarity(avg_visited_vector.reshape(1, -1), candidate_vector.reshape(1, -1))[0][0]
                similarities[candidate_id] = float(similarity)
                print(f"DEBUG: Cosine similarity for candidate {candidate_id}: {similarity}")
            
            print(f"DEBUG: Cosine similarity results: {similarities}")
            return similarities
        except Exception as e:
            print(f"DEBUG: Error calculating cosine similarity: {e}")
            # Return zero similarities as fallback
            similarities = {}
            for candidate_id in candidate_ids:
                similarities[candidate_id] = 0.0
            return similarities
    
    def get_matrix_similarity(self, user_id, candidate_ids):
        """Calculate matrix similarity using IALS (Implicit ALS)"""
        print(f"DEBUG: IALS: Starting calculation for user {user_id}, candidates: {candidate_ids}")
        
        # Simple fallback for now - return basic similarity based on shared users
        try:
            print(f"DEBUG: IALS: Getting user interactions")
            # Get user's visited excursions
            visited_ids = self.get_user_visited_excursions(user_id)
            user_visits = set(visited_ids)
            
            print(f"DEBUG: IALS: User {user_id} visited: {user_visits}")
            
            # Get all users and their visited excursions
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT user_id, excursion_id 
                    FROM excursions_userexcursion 
                    WHERE user_id != %s
                """, [user_id])
                all_visits = cursor.fetchall()
            
            print(f"DEBUG: IALS: Found {len(all_visits)} visits from other users")
            
            similarities = {}
            for candidate_id in candidate_ids:
                similarity_score = 0
                users_with_candidate = 0
                
                for other_user_id, other_excursion_id in all_visits:
                    if other_excursion_id == candidate_id:
                        users_with_candidate += 1
                        
                        # Get this user's other visits with new cursor
                        with connection.cursor() as inner_cursor:
                            inner_cursor.execute("""
                                SELECT excursion_id 
                                FROM excursions_userexcursion 
                                WHERE user_id = %s
                            """, [other_user_id])
                            other_user_visits = set(row[0] for row in inner_cursor.fetchall())
                        
                        # Calculate Jaccard similarity
                        intersection = len(user_visits & other_user_visits)
                        union = len(user_visits | other_user_visits)
                        
                        if union > 0:
                            jaccard_similarity = intersection / union
                            similarity_score += jaccard_similarity
                
                # Normalize by number of users who visited this candidate
                if users_with_candidate > 0:
                    similarity_score = similarity_score / users_with_candidate
                else:
                    similarity_score = 0.0
                
                similarities[candidate_id] = float(similarity_score)
                print(f"DEBUG: IALS similarity for candidate {candidate_id}: {similarity_score}")
            
            print(f"DEBUG: IALS similarity results: {similarities}")
            return similarities
            
        except Exception as e:
            print(f"DEBUG: IALS Error: {e}")
            import traceback
            traceback.print_exc()
            return {candidate_id: 0.0 for candidate_id in candidate_ids}
    
    def get_recommendations(self, user_id, limit=10, similarity_threshold=0.0):
        """Get recommendations for a user"""
        # Get user's visited excursions
        visited_ids = self.get_user_visited_excursions(user_id)
        
        # Get all excursions not visited by user
        all_excursions = Excursion.objects.filter(is_active=True)
        candidate_ids = [exc.id for exc in all_excursions if exc.id not in visited_ids]
        
        if not candidate_ids:
            return []
        
        # If user has no visited excursions, return popular excursions
        if not visited_ids:
            print(f"User {user_id} has no visited excursions, returning popular ones")
            # Get most popular excursions (most visited)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT excursion_id, COUNT(*) as visit_count
                    FROM recommendations_userexcursion 
                    GROUP BY excursion_id 
                    ORDER BY visit_count DESC
                    LIMIT %s
                """, [limit])
                popular_ids = [row[0] for row in cursor.fetchall()]
            
            # If no visits at all, return random excursions
            if not popular_ids:
                popular_ids = candidate_ids[:limit]
            
            recommended_excursions = Excursion.objects.filter(id__in=popular_ids)
            return [{
                'id': excursion.id,
                'title': excursion.title,
                'description': excursion.description,
                'short_description': excursion.short_description,
                'location': excursion.location,
                'duration': excursion.duration,
                'price': str(excursion.price),
                'score': 1.0  # Popular excursions get max score
            } for excursion in recommended_excursions]
        
        # Calculate similarities
        print(f"DEBUG: Starting similarity calculations for user {user_id}")
        cosine_similarities = self.get_cosine_similarity(visited_ids, candidate_ids)
        print(f"DEBUG: Cosine similarities calculated: {cosine_similarities}")
        matrix_similarities = self.get_matrix_similarity(user_id, candidate_ids)
        print(f"DEBUG: Matrix similarities calculated: {matrix_similarities}")
        
        # Calculate final scores using weighted sum
        final_scores = {}
        for candidate_id in candidate_ids:
            cosine_score = cosine_similarities.get(candidate_id, 0)
            matrix_score = matrix_similarities.get(candidate_id, 0)
            
            # Weighted sum: 0.35 * cosine + 0.65 * matrix
            final_score = 0.35 * cosine_score + 0.65 * matrix_score
            final_scores[candidate_id] = final_score
        
        print(f"DEBUG: Final scores before filtering: {final_scores}")
        
        # Filter by similarity threshold (default 0.0 means no filtering)
        if similarity_threshold > 0:
            filtered_candidates = {id: score for id, score in final_scores.items() if score >= similarity_threshold}
            print(f"DEBUG: Filtered candidates with threshold {similarity_threshold}: {filtered_candidates}")
        else:
            filtered_candidates = final_scores
        
        # If no candidates pass threshold, return top candidates anyway
        if not filtered_candidates and similarity_threshold > 0:
            print(f"No candidates passed threshold {similarity_threshold}, returning top candidates anyway")
            filtered_candidates = dict(sorted(final_scores.items(), key=lambda x: x[1], reverse=True)[:limit])
        
        # Sort by score and get top recommendations
        sorted_candidates = sorted(filtered_candidates.items(), key=lambda x: x[1], reverse=True)
        top_ids = [id for id, score in sorted_candidates[:limit]]
        
        # Get excursion details
        recommended_excursions = Excursion.objects.filter(id__in=top_ids)
        
        # Create response with scores
        recommendations = []
        for excursion in recommended_excursions:
            recommendations.append({
                'id': excursion.id,
                'title': excursion.title,
                'description': excursion.description,
                'short_description': excursion.short_description,
                'location': excursion.location,
                'duration': excursion.duration,
                'price': str(excursion.price),
                'score': round(final_scores.get(excursion.id, 0), 3)
            })
        
        # Sort by final score
        recommendations_with_scores = [(rec, final_scores[rec['id']]) for rec in recommendations]
        recommendations_with_scores.sort(key=lambda x: x[1], reverse=True)
        recommendations = [rec for rec, score in recommendations_with_scores]
        
        print(f"DEBUG: Returning {len(recommendations)} recommendations")
        return recommendations


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'},
                'recommendations': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'title': {'type': 'string'},
                            'description': {'type': 'string'},
                            'short_description': {'type': 'string'},
                            'location': {'type': 'string'},
                            'duration': {'type': 'integer'},
                            'price': {'type': 'string'},
                            'score': {'type': 'number'}
                        }
                    }
                },
                'count': {'type': 'integer'}
            }
        }
    }
)
@api_view(['GET'])
def get_recommendations(request, user_id):
    """Get recommendations for a user"""
    print(f"VIEW CALLED: get_recommendations for user_id: {user_id}")
    logger.info(f"DEBUG: get_recommendations called for user_id: {user_id}")
    
    # Get similarity_threshold from query params (default 0.0)
    similarity_threshold = float(request.GET.get('similarity_threshold', 0.0))
    limit = int(request.GET.get('limit', 10))
    
    try:
        engine = RecommendationEngine()
        logger.info(f"DEBUG: RecommendationEngine created")
        recommendations = engine.get_recommendations(user_id, limit, similarity_threshold)
        logger.info(f"DEBUG: Got {len(recommendations)} recommendations with threshold {similarity_threshold}")
        
        return Response({
            'user_id': user_id,
            'recommendations': recommendations,
            'count': len(recommendations),
            'similarity_threshold': similarity_threshold
        })
    except Exception as e:
        logger.error(f"DEBUG: Exception in get_recommendations: {e}")
        return Response({'error': str(e)}, status=500)


@extend_schema(
    responses={200: {'type': 'object', 'properties': {'status': {'type': 'string'}}}}
)
@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'healthy'})


@extend_schema(
    responses={200: {'type': 'array', 'items': UserSerializer}}
)
@api_view(['GET'])
def list_users(request):
    """List all users"""
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@extend_schema(
    responses={200: {'type': 'array', 'items': ExcursionSerializer}}
)
@api_view(['GET'])
def list_excursions(request):
    """List all excursions"""
    excursions = Excursion.objects.filter(is_active=True)
    serializer = ExcursionSerializer(excursions, many=True)
    return Response(serializer.data)


@extend_schema(
    responses={
        200: {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'},
                'visited_excursions': {'type': 'array', 'items': {'type': 'string'}}
            }
        }
    }
)
@api_view(['GET'])
def get_user_visited_excursions(request, user_id):
    """Get all visited excursions by user with short descriptions"""
    try:
        user_excursions = UserExcursion.objects.filter(user_id=user_id).select_related('excursion')
        
        visited_data = {}
        for user_excursion in user_excursions:
            excursion = user_excursion.excursion
            if user_id not in visited_data:
                visited_data[user_id] = []
            visited_data[user_id].append(excursion.short_description)
        
        return Response(visited_data)
    except Exception as e:
        logger.error(f"Error getting user visited excursions: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def mark_visited(request):
    """Mark an excursion as visited by a user"""
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


# Test if module is loaded
print("MODULE LOADED: recommendations/views.py")
logger.critical("MODULE LOADED: recommendations/views.py")
