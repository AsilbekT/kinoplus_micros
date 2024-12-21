from django.core.management.base import BaseCommand
from video_app.models import Catagory, Content  # Replace 'your_app' with the actual app name

class Command(BaseCommand):
    help = 'Delete specified categories without deleting their associated contents'

    def add_arguments(self, parser):
        parser.add_argument('category_names', nargs='+', type=str, help='List of category names to delete')

    def handle(self, *args, **options):
        category_names = options['category_names']
        for name in category_names:
            try:
                category = Catagory.objects.get(name=name)
                # Unlink the category from its contents
                contents = Content.objects.filter(category=category)
                for content in contents:
                    content.category = None
                    content.save()
                
                # Delete the category
                category.delete()
                self.stdout.write(self.style.SUCCESS(f"Successfully deleted category '{name}'"))
            except Catagory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Category '{name}' does not exist"))
