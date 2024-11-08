from django.db import models

# Create your models here.


class DistanceQuery(models.Model):
    source_address = models.CharField(max_length=512)
    destination_address = models.CharField(max_length=512)
    distance = models.DecimalField(max_digits=1000, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.source_address} to {self.destination_address} - {self.distance} km"
        )
