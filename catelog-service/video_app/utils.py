import requests
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from PIL import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import jwt
from jwt.exceptions import InvalidTokenError
from catalog_service.settings import SERVICES
from rest_framework import status as http_status

# from .models import SubscriptionPlan
SECRET_KEY = 'VpwI_yUDuQuhA1VEB0c0f9qki8JtLeFWh3lA5kKvyGnHxKrZ-M59cA'
ALGORITHM = "HS256"


BILLING_SERVICE_URL = "https://gateway.pandatv.uz/billingservice/"



def standardResponse(status, message, data, pagination=None):
    response = {
        'status': status,
        'message': message,
        'data': data
    }
    if pagination:
        response['pagination'] = pagination
    return Response(response)


def paginate_queryset(queryset, request):
    page_number = request.query_params.get('page', 1)
    page_size = request.query_params.get('size', 10)

    paginator = Paginator(queryset, page_size)

    try:
        paginated_queryset = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_queryset = paginator.page(1)
        page_number = 1
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        paginated_queryset = paginator.page(paginator.num_pages)
        page_number = paginator.num_pages

    # Create pagination response
    pagination_data = {
        'total': paginator.count,
        'page_size': page_size,
        'current_page': int(page_number),
        'total_pages': paginator.num_pages,
        'next': paginated_queryset.has_next(),
        'previous': paginated_queryset.has_previous(),
    }

    return paginated_queryset, pagination_data


def validate_file_size(value):
    filesize = value.size

    if filesize > 2048000:
        raise ValidationError(
            "The maximum file size that can be uploaded is 2 MB")
    else:
        return value


def validate_image_file(value):
    try:
        image = Image.open(value)
        image.verify()
    except:
        raise ValidationError("Invalid image format")


def user_has_active_plan(username, token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(SERVICES['billingservice'] +
                            f'/billing/{username}/subscriptions/', headers=headers)

    if response.status_code == 200:
        return True
    return False


def decode_token(token):
    """
    Decodes a JWT token.

    :param token: The JWT token to decode.
    :param secret_key: The secret key used to decode the token.
    :param algorithms: List of algorithms to use for decoding. Default is ['HS256'].
    :return: The decoded token payload if the token is valid, None otherwise.
    """
    try:
        # The token usually comes in the format "Bearer <token>". We split to get the token part.
        token = token.split(' ')[1] if ' ' in token else token
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    except InvalidTokenError:
        # Handle invalid token cases here (e.g., expired, malformed)
        return None


def convert_to_https(url):
    if url and url.startswith("http://"):
        return url.replace("http://", "https://")
    return url


def ensure_https(url):
    if not url.startswith('https://'):
        return url.replace('http://', 'https://')
    return url
