from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.raw_data_list, name='raw_data_list'),
    url(r'^annotation.html', views.annotation_page, name='annotation_page'),
    url(r'^train$', views.train_model, name='train_model'),
    url(r'^apply$', views.apply_model, name='apply_model'),
]
