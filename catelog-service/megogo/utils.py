import hashlib
import requests
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

MEGAGO_PRIVATE_KEY = "fad7befbe3"
MEGAGO_PUBLIC_KEY = "_panda_uz_test"
MEGAGO_SERVICE_ID = "testuzsvod"
MEGAGO_PARTNER_KEY = "testprod_uz"
MEGAGO_SALT = "6qlTHlFxvOUpoXKT"


def generate_md5_hash(data: str) -> str:
    """Generate an MD5 hash for the given data."""
    hasher = hashlib.md5()
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()


def generate_sign_for_megago(params) -> str:
    sorted_params = params.items()
    concatenated_params = "".join(
        f"{key}={value}" for key, value in sorted_params)
    string_to_hash = concatenated_params + MEGAGO_PRIVATE_KEY
    md5_hash = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()
    signature = md5_hash + MEGAGO_PUBLIC_KEY

    return signature


def get_popular_contents_megago(params) -> dict:

    sign = generate_sign_for_megago(params)

    request_params = params.copy()
    request_params['sign'] = sign

    base_url = "https://api.megogo.net/v1/video"
    try:
        response = requests.get(base_url, params=request_params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from MEGOGO API: {e}")
        return {}


def transform_video_data(video_data) -> dict:
    return {
        'id': video_data.get('id', None),
        'genre': [{'id': genre_id} for genre_id in video_data.get('genres', [])],
        'director': None,  
        'rating': video_data.get('rating_imdb', None),
        'thumbnail_image': video_data.get('image', {}).get('original', None),
        'year': video_data.get('year', None),
        'title': video_data.get('title', None),
        'is_premiere': False,
        'description': video_data.get('description', None),
        'trailer_url': video_data.get('trailer_url', None),
        'is_free': video_data.get('is_free', False),
        'is_favorited': video_data.get('is_favorited', False),
        'release_date': video_data.get('release_date', None),
        'widescreen_thumbnail_image': video_data.get('image', {}).get('fullscreen', None)
    }


def get_content_details(params) -> dict:

    sign = generate_sign_for_megago(params)

    request_params = params.copy()
    request_params['sign'] = sign
    base_url = "https://api.megogo.net/v1/video/info"

    try:
        response = requests.get(base_url, params=request_params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch data from MEGOGO API: {e}")
        return {}


def subscribe_megogo_user(user_id: int) -> bool:
    try:
        url = "https://billing.megogo.net/partners/testprod_uz/subscription/subscribe"
        params = {"userId": user_id, "serviceId": MEGAGO_SERVICE_ID}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Failed to subscribe user {user_id}: {e}")
        return False

# https://api.megogo.net/v1/auth/by_partners?isdn=123321&partner_key=testprod_uz&token=466f67d760df5633b0dbae80fef363c7&sign=4c5fe11b111dcebb68e584747fd77ec7_panda_uz_test


def get_megogo_token(isdn: str, partner_key: str) -> str:
    try:
        url = "https://api.megogo.net/v1/auth/by_partners"
        token = generate_md5_hash(f"{isdn}{partner_key}{MEGAGO_SALT}")
        # token = "a800e303a1f244f27a811944498503a6"
        sign = generate_sign_for_megago(
            {'isdn': isdn, 'partner_key': partner_key, 'token': token}
        )
        params = {"isdn": isdn, "partner_key": partner_key,
                  "token": token, "sign": sign}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {}).get('tokens', '').get('access_token', '')
    except requests.RequestException as e:
        logging.error(f"Failed to get token for ISDN {isdn}: {e}")
        return ""
# https://api.megogo.net/v1/stream?
# video_id=2217921&access_token=MToxNjA1MTAwMzY3OjE3MTMxODUzODM6OjkxZTkyMjA4NDYwMmMwMTU3MjdhMzFjNGI5MDA1MDIy&sign=9d1efe5b96c2cecc879778750500b993_panda_uz_test


def get_megogo_content(video_id: int, access_token: str) -> str:
    try:
        url = "https://api.megogo.net/v1/stream"
        params = {"video_id": video_id,
                  "access_token": access_token, "lang": "ru"}
        sign = generate_sign_for_megago(
            params
        )
        params['sign'] = sign
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('data', '').get('src', '')
    except requests.RequestException as e:
        logging.error(f"Failed to get content for video {video_id}: {e}")
        return ""
