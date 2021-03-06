from django.conf.urls.defaults import patterns, include, url
import views

urlpatterns = patterns('',
    url(r'^backend/journals$', views.backend_journals, name='backend_journals'),
    url(r'^backend/journals/(?P<journal_id>.*)$', views.backend_journal, name='backend_journal'),
    url(r'^backend/scrapers$', views.backend_scrapers, name='backend_scrapers'),
)
