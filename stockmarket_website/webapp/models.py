from django.db import models

class News(models.Model):
    title = models.TextField()
    link = models.TextField()
    published_date = models.TextField()

    def __str__(self):
        return self.title

