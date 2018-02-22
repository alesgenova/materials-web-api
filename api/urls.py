from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

# define the urls that are available in the API, and match them to the respective Views.
urlpatterns = [
    url(r'^add/$', views.AddCompound.as_view()),
    url(r'^batchadd/$', views.AddCompounds.as_view()),
    url(r'^clear/$', views.RemoveAll.as_view()),
    url(r'^search/$', views.SearchCompounds.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)