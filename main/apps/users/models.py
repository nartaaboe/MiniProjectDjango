from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = "admin"
    TRADER = "trader"
    SALESMAN = "salesman"
    CUSTOMER = "customer"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TRADER, "Trader"),
        (SALESMAN, "Salesman"),
        (CUSTOMER, "Customer"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=CUSTOMER)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='users_pfp/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.role}"
