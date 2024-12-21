from rest_framework import serializers

class SafeFloatField(serializers.FloatField):
    def to_internal_value(self, data):
        if data in ['', None]:
            return None
        try:
            return float(data)
        except (TypeError, ValueError):
            raise serializers.ValidationError("This field must be a valid float.")
    
    def to_representation(self, value):
        if value in ['', None]:
            return None
        return super().to_representation(value)
        
class ImageSerializer(serializers.Serializer):
    big = serializers.URLField(allow_blank=True, required=False)
    small = serializers.URLField(allow_blank=True, required=False)
    original = serializers.URLField(allow_blank=True, required=False)
    original_wide = serializers.URLField(allow_blank=True, required=False)
    fullscreen = serializers.URLField(allow_blank=True, required=False)
    image_470x270 = serializers.URLField(allow_blank=True, required=False)
    image_215x120 = serializers.URLField(allow_blank=True, required=False)


class VideoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    image = ImageSerializer()
    country = serializers.CharField()
    countries = serializers.ListField(child=serializers.IntegerField())
    year = serializers.IntegerField()
    slug = serializers.CharField()
    categories = serializers.ListField(child=serializers.IntegerField())
    age_limit = serializers.IntegerField()
    rating_imdb = SafeFloatField(allow_null=True, required=False)
    rating_kinopoisk = SafeFloatField(allow_null=True, required=False)
    rating_megogo = SafeFloatField(allow_null=True, required=False)
    duration = serializers.IntegerField()
    genres = serializers.ListField(child=serializers.IntegerField())
    is_exclusive = serializers.BooleanField()
    show = serializers.CharField()
    is_sport = serializers.BooleanField()
    delivery_rules = serializers.ListField(child=serializers.CharField())


class ResponseDataSerializer(serializers.Serializer):
    limit = serializers.IntegerField()
    total_pages = serializers.IntegerField(required=False)
    next_page = serializers.CharField(required=False)
    offset = serializers.IntegerField(required=False)
    total = serializers.IntegerField(required=False)
    has_more = serializers.BooleanField(required=False)
    video_list = VideoSerializer(many=True)


class MegagoPopularSerializer(serializers.Serializer):
    result = serializers.CharField()
    code = serializers.IntegerField()
    data = ResponseDataSerializer()


class AvatarSerializer(serializers.Serializer):
    image_130x2000 = serializers.URLField(allow_blank=True)
    image_540x2000 = serializers.URLField(allow_blank=True)
    image_185x185 = serializers.URLField(allow_blank=True)
    image_240x240 = serializers.URLField(allow_blank=True)
    image_360x360 = serializers.URLField(allow_blank=True)
    image_original = serializers.URLField(allow_blank=True)


class PersonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    name_original = serializers.CharField()
    avatar = AvatarSerializer()
    type = serializers.CharField()
    slug = serializers.CharField()


class MegagoContentDetails(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    image = ImageSerializer()
    country = serializers.CharField()
    countries = serializers.ListField(child=serializers.IntegerField())
    year = serializers.IntegerField()
    slug = serializers.CharField()
    categories = serializers.ListField(child=serializers.IntegerField())
    age_limit = serializers.IntegerField()
    rating_imdb = SafeFloatField(allow_null=True, required=False)
    rating_kinopoisk = SafeFloatField(allow_null=True, required=False)
    rating_megogo = SafeFloatField(allow_null=True, required=False)
    duration = serializers.IntegerField()
    trailer_id = serializers.IntegerField()
    quality = serializers.CharField()
    video_url = serializers.URLField()
    full_url = serializers.URLField()
    title_original = serializers.CharField()
    description = serializers.CharField()
    is_promocode = serializers.BooleanField()
    is_favorite = serializers.BooleanField()
    is_embed = serializers.BooleanField()
    vote = serializers.IntegerField()
    comments_num = serializers.IntegerField()
    like = serializers.IntegerField()
    dislike = serializers.IntegerField()
    people = PersonSerializer(many=True)
    screenshots = ImageSerializer(many=True)
    season_list = serializers.ListField()
    subtitles = serializers.ListField(child=serializers.CharField())
    recommended_videos = serializers.ListField()
    purchase_info = serializers.DictField()
    is_available = serializers.BooleanField()
    is_selling = serializers.BooleanField()
    kinopoisk_url = serializers.URLField()
    allow_external_streaming = serializers.BooleanField()
    vod_channel = serializers.BooleanField()
    dvr = serializers.BooleanField()
    tv = serializers.BooleanField()
    video_type = serializers.CharField()
    cartoon = serializers.BooleanField()
    genres = serializers.ListField(child=serializers.IntegerField())
    is_exclusive = serializers.BooleanField()
    show = serializers.CharField()
    is_sport = serializers.BooleanField()
    audio_list = serializers.ListField(child=serializers.CharField())
    is_series = serializers.BooleanField()
    is_3d = serializers.BooleanField()
    parental_control_required = serializers.BooleanField()
    bizclass = serializers.ListField(child=serializers.CharField())
    is_wvdrm = serializers.BooleanField()
    type = serializers.CharField()
    delivery_rules = serializers.ListField(child=serializers.CharField())
    trailer_url = serializers.URLField(
        required=False)
    main_content_url = serializers.URLField(required=False)
