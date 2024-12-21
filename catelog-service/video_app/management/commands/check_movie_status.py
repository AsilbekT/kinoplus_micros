import os
from urllib.parse import urlparse
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from video_app.models import Movie  # Replace 'your_app' with the actual app name

class Command(BaseCommand):
    help = 'Check movie status and update is_ready field if necessary'

    def handle(self, *args, **options):
        # Directory where converted videos are stored
        converted_videos_dir = '/var/www/video_conversion/converted_videos/'

        # Fetch all movies
        movies = Movie.objects.all().order_by('title')

        # List to store formatted movie titles
        formatted_titles = []

        for movie in movies:
            content_url = movie.main_content_url
            if content_url:
                # Extract folder name from URL
                parsed_url = urlparse(content_url)
                folder_name = os.path.basename(os.path.dirname(parsed_url.path))
                folder_path = os.path.join(converted_videos_dir, folder_name)
                print(folder_path)
                # Check if the folder exists
                # if not os.path.exists(folder_path):
                    # Folder does not exist, count this movie and set is_ready to False
                formatted_titles.append(f"{len(formatted_titles) + 1}. {movie.title}")
                    # movie.is_ready = False
                    # movie.save(update_fields=['is_ready'])

        # Create a temporary file and write the formatted titles to it
        temp_file_path = '/tmp/movie_titles.txt'
        with open(temp_file_path, 'w') as file:
            file.write('\n'.join(formatted_titles))

        self.stdout.write(self.style.SUCCESS(f"Formatted movie titles saved to {temp_file_path}"))
