from django.db import models

# Create your models here.
class Scholarship(models.Model):
    Name = models.TextField()
    Eligibility=models.TextField()
    Eligible=models.TextField()
    Contacts_offline_applications=models.URLField()
    Special_Categories=models.TextField()
    Scholarship_Fellowship=models.TextField()
    Level=models.TextField()
    State=models.TextField(max_length=255, default='Unknown')
    Application_Period=models.TextField()
    Links_online_application=models.TextField()

    class Meta:
        app_label = 'authentication'