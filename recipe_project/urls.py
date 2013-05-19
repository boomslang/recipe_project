from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from settings import DOCUMENT_ROOT
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'recipe_project.views.home', name='home'),
    # url(r'^recipe_project/', include('recipe_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # (r'^static/(.*)$', 'django.views.static.serve', {'document_root': '%s' % DOCUMENT_ROOT, 'show_indexes': True}),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', 'main.views.logout_view'),
    (r'^profile/$', 'main.views.profile_view'),
    (r'^create/$', 'main.views.create_view'),

    (r'^register/', 'main.views.register'),

    (r'^r/(?P<recipe_id>[^/]+)/$', 'main.views.recipe_view'),
    (r'^r/(?P<recipe_id>[^/]+)/mutate$', 'main.views.mutate_view'),
    (r'^r/(?P<recipe_id>[^/]+)/tag$', 'main.views.tag_view'),
    (r'^u/(?P<user_name>[^/]+)/$', 'main.views.user_view'),
    (r'^ajax_like/', 'main.views.ajax_like'),




    (r'^$', 'main.views.mainPage_view'), # Should be the last element!
)

urlpatterns += staticfiles_urlpatterns()