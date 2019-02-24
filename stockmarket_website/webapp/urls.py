from django.conf.urls import url
from django.views.generic import ListView, DetailView
from webapp.models import News
from . import views

urlpatterns = [
    url(r'^$', ListView.as_view( queryset= News.objects.all(), template_name="webapp/home.html")),
]