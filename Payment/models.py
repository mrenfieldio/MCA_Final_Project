from django.db import models
from users.models import User

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    amount = models.IntegerField()

    order_id = models.CharField(max_length=255)
    payment_id = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=50, default="created")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id
