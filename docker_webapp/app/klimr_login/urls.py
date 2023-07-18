from django.conf.urls import url, include
from klimr_login import views

urlpatterns = [
    url(r'^$', views.login2),
    url(r'^token$', views.getcsrftoken),
    url(r'^login$', views.login)
]
