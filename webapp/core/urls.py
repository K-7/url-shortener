from django.conf.urls import url
from core import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^api/(?P<short_url>\w+)', views.redirect_method, name="redirect_method"),
    url(r'^url_short/(?P<id>\d*)', views.UrlMappingViewset.as_view(), name="url_short"),
]