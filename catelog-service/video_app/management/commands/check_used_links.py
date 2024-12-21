from video_app.models import ExternalContent, Movie, Series, Episode


def get_all_content_urls():
    urls = []

    urls.extend(ExternalContent.objects.exclude(content_url='').values_list('content_url', flat=True))

    urls.extend(Movie.objects.exclude(main_content_url='').values_list('main_content_url', flat=True))

    urls.extend(Series.objects.exclude(series_summary_url='').values_list('series_summary_url', flat=True))

    urls.extend(Episode.objects.exclude(episode_content_url='').values_list('episode_content_url', flat=True))

    urls.extend(Movie.objects.exclude(trailer_url='').values_list('trailer_url', flat=True))
    urls.extend(Series.objects.exclude(trailer_url='').values_list('trailer_url', flat=True))
    urls.extend(Episode.objects.exclude(trailer_url='').values_list('trailer_url', flat=True))

    return list(set(urls))  

all_urls = get_all_content_urls()
for url in all_urls:
    print(url)
