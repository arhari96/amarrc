from django.db import models

class HostDetail(models.Model):
    name = models.CharField(max_length=100)
    mobile_number = models.CharField(max_length=15, primary_key=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_active']

    def __str__(self):
        return f"{self.name} - {self.mobile_number}"
    
class CanCall(models.Model):
    can_call = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.can_call}"