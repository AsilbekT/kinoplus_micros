from django.db import models

class User(models.Model):
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    google_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    apple_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    auth_type = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'users'


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    device_name = models.CharField(max_length=100, help_text="Name of the device used for the session")
    token = models.CharField(max_length=255, unique=True, help_text="Session token")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The time when the session was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="The time when the session was last updated")

    def __str__(self):
        return f"{self.user.username} - {self.device_name} - {self.token[:15]}..."

    class Meta:
        db_table = 'sessions'