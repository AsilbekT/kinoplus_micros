from django.contrib import admin
from .models import Banner, Comment, FavoriteContent, Season, UserSubscription
from django.utils.html import format_html
from django.contrib import admin, messages
from django.utils import timezone
from datetime import timedelta
from django import forms
from .models import (
    Genre,
    Director,
    Movie,
    Series,
    Episode,
    Banner,
    Catagory,
    VideoConversionType,
    SubscriptionPlan,
    PandaDocs,
    ExternalContent
)

import re

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

class TodayFilter(admin.SimpleListFilter):
    title = 'today'
    parameter_name = 'today'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            today = timezone.now().date()
            return queryset.filter(start_date=today)
        return queryset

class ThisWeekFilter(admin.SimpleListFilter):
    title = 'this week'
    parameter_name = 'this_week'

    def lookups(self, request, model_admin):
        return (
            ('this_week', 'This Week'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_week':
            today = timezone.now().date()
            start_of_week = today - timedelta(days=today.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return queryset.filter(start_date__range=(start_of_week, end_of_week))
        return queryset

class ThisMonthFilter(admin.SimpleListFilter):
    title = 'this month'
    parameter_name = 'this_month'

    def lookups(self, request, model_admin):
        return (
            ('this_month', 'This Month'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_month':
            today = timezone.now().date()
            start_of_month = today.replace(day=1)
            next_month = start_of_month + timedelta(days=31)
            end_of_month = next_month.replace(day=1) - timedelta(days=1)
            return queryset.filter(start_date__range=(start_of_month, end_of_month))
        return queryset

class ThisYearFilter(admin.SimpleListFilter):
    title = 'this year'
    parameter_name = 'this_year'

    def lookups(self, request, model_admin):
        return (
            ('this_year', 'This Year'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'this_year':
            today = timezone.now().date()
            start_of_year = today.replace(month=1, day=1)
            end_of_year = today.replace(month=12, day=31)
            return queryset.filter(start_date__range=(start_of_year, end_of_year))
        return queryset

class ExternalContentAdmin(admin.ModelAdmin):

    list_display = ('title', 'content_url')
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('title')  

    def get_natural_sorted_name(self, obj):
        return obj.title
    get_natural_sorted_name.admin_order_field = 'title'  # Ensure this refers to a field on the model

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        # Custom ordering can be applied here if necessary
        return response

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days']
    search_fields = ['name']
    list_filter = ['price']

class UserSubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'subscription_plan_name', 'start_date', 'end_date', 'status']
    search_fields = ['username', 'user_id']
    list_filter = ['subscription_plan_name', 'status', TodayFilter, ThisWeekFilter, ThisMonthFilter, ThisYearFilter]


class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# class SubscriptionPlanInline(admin.TabularInline):
#     model = SubscriptionPlan
#     extra = 1


class ContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_date', 'is_ready',
                    'is_premiere', 'has_trailer')
    search_fields = ('id', 'title', 'release_date')
    list_filter = ('is_ready', 'is_premiere', 'has_trailer')
    ordering = ('release_date',)

    def save_model(self, request, obj, form, change):
        # Save the instance first to ensure it has an ID.
        super().save_model(request, obj, form, change)
        
        # Now it's safe to work with many-to-many relationships.
        if obj.is_free:
            if obj.available_under_plans.exists():
                messages.set_level(request, messages.ERROR)
                messages.error(
                    request, "Free content should not have any associated subscription plans.")
        else:
            super().save_model(request, obj, form, change)

class MovieAdminForm(forms.ModelForm):
    clear_main_content_url = forms.BooleanField(required=False, label='Clear Main Content URL')

    class Meta:
        model = Movie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MovieAdminForm, self).__init__(*args, **kwargs)
        if not self.instance.main_content_url:
            self.fields['clear_main_content_url'].widget = forms.HiddenInput()

    def save(self, commit=True):
        movie = super().save(commit=False)
        if self.cleaned_data.get('clear_main_content_url'):
            movie.main_content_url = ''
            if commit:
                movie.save(update_fields=['main_content_url'])  # Specify fields to update to avoid recursion
        else:
            if commit:
                movie.save()
        return movie

class EpisodeAdminForm(forms.ModelForm):
    clear_episode_content_url = forms.BooleanField(required=False, label='Clear episode Content URL')

    class Meta:
        model = Movie
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EpisodeAdminForm, self).__init__(*args, **kwargs)
        if not self.instance.episode_content_url:
            self.fields['clear_episode_content_url'].widget = forms.HiddenInput()

    def save(self, commit=True):
        if self.cleaned_data.get('clear_episode_content_url'):
            self.instance.episode_content_url = ''
        return super().save(commit=commit)

class MovieAdmin(ContentAdmin):
    form = MovieAdminForm
    list_display = ContentAdmin.list_display + \
        ('is_featured', 'is_trending', 'production_cost', 'licensing_cost')
    list_filter = ContentAdmin.list_filter + ('is_featured', 'is_trending')

    def save_model(self, request, obj, form, change):
        # Custom save logic, if needed
        super().save_model(request, obj, form, change)


class SeriesAdmin(ContentAdmin):
    list_display = ContentAdmin.list_display + \
        ('number_of_seasons', 'is_featured', 'is_trending')
    list_filter = ContentAdmin.list_filter + \
        ('number_of_seasons', 'is_featured', 'is_trending')


class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeAdminForm

    list_display = ('series', 'season', 'episode_number',
                    'title', 'duration_minute')
    search_fields = ('series__title', 'title')
    list_filter = ('series', 'season')
    ordering = ('series', 'season', 'episode_number')
    
    
    def save_model(self, request, obj, form, change):
        # Custom save logic, if needed
        super().save_model(request, obj, form, change)


class BannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_object', 'status', 'priority',
                    'created_at', 'updated_at')
    list_filter = ('status',  'created_at')
    search_fields = ('name', 'content_object__title')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('content_type')
        return queryset


class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number', 'trailer_url')
    search_fields = ('series__title', 'trailer_url')
    list_filter = ('series',)


class FavoriteContentAdmin(admin.ModelAdmin):
    list_display = ('username', 'content_object_display')

    def content_object_display(self, obj):
        return obj.content_object
    content_object_display.short_description = 'Content'


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'content', 'created_at',
                    'updated_at', 'is_reply')
    list_filter = ('created_at', 'username')
    search_fields = ('username', 'content')
    raw_id_fields = ('parent',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('parent')


admin.site.register(Comment, CommentAdmin)
admin.site.register(FavoriteContent, FavoriteContentAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Director, DirectorAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
admin.site.register(Catagory)
admin.site.register(VideoConversionType)
admin.site.register(UserSubscription, UserSubscriptionPlanAdmin)
admin.site.register(PandaDocs)
admin.site.register(ExternalContent, ExternalContentAdmin)