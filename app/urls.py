from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.raw_data_list, name='raw_data_list'),
    url(r'^annotation.html', views.annotation_page, name='annotation_page'),
]
