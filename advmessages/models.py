from django.db import models
from authentication.models import Profile
# Create your models here.
class AdviserMessages(models.Model):
    ROLE = (
        ('system', 'System'),
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )
    profile = models.ForeignKey(Profile, related_name='profile', on_delete=models.CASCADE)
    message = models.TextField()
    role = models.CharField(max_length=20, choices=ROLE)
    response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.message