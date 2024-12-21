# documents.py

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from video_app.models import Movie, Series, Genre, Director


@registry.register_document
class MovieDocument(Document):
    genre = fields.ObjectField(properties={
        'name': fields.TextField(),
    })
    director = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

    class Index:
        name = 'movies'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Movie
        fields = [
            'title',
            'description',
            'release_date',
            'duration_minute',
            'cast_list',
            'rating',
            'thumbnail_image',
            'trailer_url',
            'main_content_url',
            'is_ready',
            'is_premiere',
            'has_trailer',
            'is_free',
            # Include other fields as needed
        ]
        related_models = [Genre, Director]


@registry.register_document
class SeriesDocument(Document):
    genre = fields.ObjectField(properties={
        'name': fields.TextField(),
    })
    director = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

    class Index:
        name = 'series'
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Series
        fields = [
            'title',
            'description',
            'release_date',
            'duration_minute',
            'cast_list',
            'rating',
            'thumbnail_image',
            'series_summary_url',
            'number_of_seasons',
            'is_ready',
            'is_premiere',
            'has_trailer',
            'is_free',
            # Include other fields as needed
        ]
        related_models = [Genre, Director]
