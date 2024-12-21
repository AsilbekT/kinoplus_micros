from django.http import Http404

from catalog_service.settings import SERVICES
from video_app.models import UserSubscription
from video_app.utils import standardResponse
from .serializers import MegagoContentDetails, MegagoPopularSerializer
from .utils import MEGAGO_PARTNER_KEY, get_content_details, get_megogo_content, get_megogo_token, get_popular_contents_megago, subscribe_megogo_user
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from django.utils import timezone


class GetPopularMegagoFilms(APIView):

    def get(self, request, format=None):
        category_id = request.GET.get('category_id', 16)
        limit = int(request.GET.get('size', 10))
        page = int(request.GET.get('page', 1))

        offset = (page - 1) * limit

        params = {
            "category_id": category_id,
            "limit": limit,
            "offset": offset
        }
        movies = get_popular_contents_megago(params)

        if 'data' in movies and 'total' in movies['data']:
            total_items = int(movies['data']['total'])
            total_pages = (total_items + limit - 1) // limit
        else:
            total_pages = 0

        serializer = MegagoPopularSerializer(movies)
        serializer_data = serializer.data
        serializer_data['data']['total_pages'] = total_pages
        serializer_data['data']['limit'] = limit
        serializer_data['data']['offset'] = offset

        return Response(serializer_data)


class GetContentDetailsMegago(APIView):
    def validate_token(self, request):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
            if len(auth_header) != 2 or auth_header[0].lower() != 'bearer':
                return False, None, None

            token = auth_header[1]
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                SERVICES['authservice'] + '/auth/verify-token', headers=headers)
            print(response.json())
            if response.status_code == 200:
                return True, response.json()['data'], token
            else:
                return False, None, None
        except Exception as e:
            # Log the exception if necessary
            return False, None, None

    def get(self, request, format=None):
        video_id = request.GET.get('video_id')
        user_id = request.GET.get('user_id')
        if not video_id or not user_id:
            return Response({'error': 'Please provide both video_id and user_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # if not subscribe_megogo_user(user_id):
        #     return Response({'error': 'Subscription failed.'}, status=status.HTTP_403_FORBIDDEN)

        token = get_megogo_token(str(user_id), MEGAGO_PARTNER_KEY)
        if not token:
            return Response({'error': 'Failed to authenticate.'}, status=status.HTTP_403_FORBIDDEN)

        movie_details = get_content_details({"id": video_id})
        if not movie_details:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)

        trailer_url = get_megogo_content(
            movie_details['data']['trailer_id'], token)

        data = MegagoContentDetails(movie_details['data']).data
        data['trailer_url'] = trailer_url
        data['main_content_url'] = None

        # Validate token for viewing main content
        auth_status, user_info, _ = self.validate_token(request)
        if auth_status and self.user_has_access_to_content(user_info['username']):
            main_content_url = get_megogo_content(video_id, token)
            data['main_content_url'] = main_content_url
        return Response(data)

    def user_has_access_to_content(self, username):
        try:
            today = timezone.now().date()
            user_sub = UserSubscription.objects.filter(
                username=username,
                status='Active',
                start_date__lte=today,
                end_date__gte=today,
                # subscription_plan_name="Megogo"
            )
            for i in user_sub:
                if i.subscription_plan_name == "Barcha kinolar" or i.subscription_plan_name == "Megogo":
                    return True
            return False

        except UserSubscription.DoesNotExist:
            return False
