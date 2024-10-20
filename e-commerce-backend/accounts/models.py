from django.db import models
from django.contrib.auth.models import AbstractUser
from uuid import uuid4


# Create your models here.
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    birth_date = models.DateField(null=True, blank=True)
    profile_url = models.TextField(null=True, blank=True)
    fb_doc_id = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "user"

    def __str__(self) -> str:
        return f"{self.id},{self.username}"
