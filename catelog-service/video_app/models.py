# catalog service models
from django.utils import timezone
from django.db import models
from .utils import convert_to_https, validate_file_size, validate_image_file
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

# Model for storing different genres


class ExternalContent(models.Model):
    title = models.CharField(max_length=255)
    content_url = models.URLField(max_length=1024)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'external_content_table'
        ordering = ['title']


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField()
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'subscription_plan_table'  # Custom table name


class FavoriteContent(models.Model):
    username = models.CharField(max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('username', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.username}'s favorite {self.content_object.title}"


class VideoConversionType(models.Model):
    VIDEO_TYPE_CHOICES = [
        ('MOVIE', 'Movie'),
        ('MOVIE_TRAILER', 'Movie Trailer'),
        ('SERIES', 'Series'),
        ('SERIES_TRAILER', 'Series Trailer'),
        ('EPISODE', 'Episode'),
    ]

    video_type = models.CharField(
        max_length=20, choices=VIDEO_TYPE_CHOICES, unique=True)

    class Meta:
        db_table = 'video_conversion_type_table'

    def __str__(self):
        return self.video_type


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'genre_table'

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'director_table'

    def __str__(self):
        return self.name


class Catagory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # If the slug is not set, generate one from the name
        if not self.slug:
            self.slug = slugify(self.name)
        super(Catagory, self).save(*args, **kwargs)


class Content(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    available_under_plans = models.ManyToManyField(
        SubscriptionPlan, blank=True)
    category = models.ForeignKey(
        Catagory, on_delete=models.CASCADE, related_name="%(class)s_catagory", null=True, blank=True)
    genre = models.ManyToManyField(
        Genre, related_name="%(class)s_contents", blank=True)
    release_date = models.DateField(blank=True, null=True)
    duration_minute = models.IntegerField()
    director = models.ForeignKey(
        Director, on_delete=models.CASCADE, related_name="%(class)s_contents")
    cast_list = models.TextField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    is_mobile_only = models.BooleanField(default=False)
    without_content = models.BooleanField(default=False)

    telegram_link = models.URLField(default='https://t.me/c/2047954894/4')
    thumbnail_image = models.ImageField(
        upload_to="thumbnail_image/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_file]
    )
    widescreen_thumbnail_image = models.ImageField(
        upload_to="widescreen_thumbnail_image/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_file]
    )
    trailer_url = models.URLField(blank=True, null=True)

    main_content_url = models.URLField(blank=True, null=True, unique=True)

    is_ready = models.BooleanField(default=False)
    is_premiere = models.BooleanField(default=False)
    has_trailer = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    telegram_private_channel = models.CharField(
        max_length=200, default="-1001802351887")

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.__class__.objects.filter(title=self.title).exclude(pk=self.pk).exists():
            raise ValidationError(
                f"A content item with the title '{self.title}' already exists."
            )

        if not self.slug:
            self.slug = slugify(self.title)

        super(Content, self).save(*args, **kwargs)


class Movie(Content):
    production_cost = models.FloatField(blank=True, null=True)
    licensing_cost = models.FloatField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    conversion_type = models.ForeignKey(
        VideoConversionType, on_delete=models.SET_NULL, null=True, related_name='movies')
    favorites = GenericRelation(FavoriteContent)
    is_movie = models.BooleanField(default=True)
    main_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movies_main_plan',  # Adjusted related_name
    )
    external_content = models.OneToOneField(
        ExternalContent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='movie'
    )

    class Meta(Content.Meta):
        db_table = 'movie_table'

    def __str__(self):
        return f"Movie: {self.title}"

    def save(self, *args, **kwargs):
        # Condition to break recursion and update main_content_url only if it's not already set
        # or if it's explicitly required to update (e.g., changed from the admin).
        if not self.main_content_url or 'update_fields' in kwargs and 'main_content_url' in kwargs['update_fields']:
            if self.external_content:
                self.main_content_url = self.external_content.content_url
                super(Movie, self).save(*args, **kwargs)
            else:
                # Proceed with normal save operation if there's no external content
                # to update the main_content_url from.
                super(Movie, self).save(*args, **kwargs)
        else:
            # Avoid updating the main_content_url to prevent recursion.
            # Remove update_fields to prevent conflicts.
            kwargs.pop('update_fields', None)
            super(Movie, self).save(*args, **kwargs)


class Series(Content):
    main_content_url = None
    series_summary_url = models.URLField(blank=True, null=True)
    number_of_seasons = models.IntegerField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    conversion_type = models.ForeignKey(
        VideoConversionType, on_delete=models.SET_NULL, null=True, related_name='series')
    favorites = GenericRelation(FavoriteContent)
    is_movie = models.BooleanField(default=False)
    main_plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='series_main_plan',  # Adjusted related_name
    )

    class Meta(Content.Meta):
        db_table = 'series_table'

    def __str__(self):
        return f"Series: {self.title}"


class Season(models.Model):
    series = models.ForeignKey(
        Series, related_name='seasons', on_delete=models.CASCADE)
    season_number = models.IntegerField()
    trailer_url = models.URLField(blank=True, null=True)
    thumbnail_image = models.ImageField(
        upload_to="season_thumbnail_image/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_file]
    )

    class Meta:
        db_table = 'season_table'
        unique_together = (('series', 'season_number'),)

    def __str__(self):
        return f"Season {self.season_number} of {self.series.title}"


class Episode(models.Model):
    series = models.ForeignKey(
        Series, related_name='episodes', on_delete=models.CASCADE)
    season = models.ForeignKey(
        Season, related_name='episodes', on_delete=models.CASCADE)
    episode_number = models.IntegerField()
    title = models.CharField(max_length=255)
    duration_minute = models.IntegerField()
    thumbnail_image_url = models.ImageField(
        upload_to="episode_thumbnail_image/",
        blank=True,
        null=True,
        validators=[validate_file_size, validate_image_file]
    )
    episode_content_url = models.URLField(blank=True, null=True)
    is_ready = models.BooleanField(default=False)
    conversion_type = models.ForeignKey(
        VideoConversionType, on_delete=models.SET_NULL, null=True, blank=True, related_name='episodes')

    external_content = models.OneToOneField(
        ExternalContent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='episode'
    )

    class Meta:
        db_table = 'episode_table'

    def __str__(self):
        return f"S{self.season.season_number}E{self.episode_number} - {self.title} of {self.series.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.episode_content_url is None:
            self.episode_content_url = self.external_content.content_url if self.external_content else None
            self.save(update_fields=['episode_content_url'])


class Banner(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=models.Q(app_label='video_app', model='movie') | models.Q(
            app_label='video_app', model='series')
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    is_movie = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'banner_table'
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return self.name

    @property
    def trailer_url(self):
        return getattr(self.content_object, 'trailer_url', None)

    @property
    def thumbnail_image_url(self):
        if self.content_object and hasattr(self.content_object, 'thumbnail_image'):
            url = self.content_object.thumbnail_image.url if self.content_object.thumbnail_image else None
            return convert_to_https(url)
        return None

    @property
    def content_title(self):
        return getattr(self.content_object, 'title', None)

    @property
    def release_year(self):
        release_date = getattr(self.content_object, 'release_date', None)
        return release_date.year if release_date else None

    @property
    def rating(self):
        return getattr(self.content_object, 'rating', None)

    @property
    def is_premiere(self):
        return getattr(self.content_object, 'is_premiere', None)

    @property
    def genres(self):
        if hasattr(self.content_object, 'genre'):
            return self.content_object.genre
        return None


class UserSubscription(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Paused', 'Paused'),
        ('Exhausted', 'Exhausted'),
        ('Expired', 'Expired'),
    ]

    user_id = models.IntegerField()
    username = models.CharField(max_length=200)
    subscription_plan_name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.username}'s Subscription to {self.subscription_plan_name}"

    @property
    def is_active(self):
        """
        Determines if the subscription is currently active.
        """
        return self.status == 'Active' and self.start_date <= timezone.now().date() <= self.end_date

    class Meta:
        unique_together = ('username', 'subscription_plan_name',)


class Comment(models.Model):
    username = models.CharField(max_length=200)
    name = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to=models.Q(app_label='video_app', model='movie') | models.Q(
            app_label='video_app', model='series')
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey(
        'self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.username} on {self.content_object}"

    @property
    def is_reply(self):
        return self.parent is not None


class PandaDocs(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    document = models.FileField(upload_to='pandadocs/', blank=True, null=True)

    def get_document_url(self):
        if self.document:
            return self.document.url
        return None
