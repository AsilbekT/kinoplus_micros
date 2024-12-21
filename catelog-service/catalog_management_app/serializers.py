from rest_framework import serializers
from video_app.models import Banner, Catagory, Comment, Director, Episode, FavoriteContent, Season, Series, Genre, Movie, VideoConversionType


class CatagorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Catagory
        fields = '__all__'


class FavoriteContentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteContent
        fields = '__all__'


class VideoConversionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoConversionType
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
