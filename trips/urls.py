from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

app_name = 'trips'
urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:trip_event_id>/', views.detail, name='detail'),
    path('?P<trip_event_destination>[A-Z]{3}/', views.dest, name='dest'),
    path('sub/?P<trip_event_subdestination>[A-Z]{3}/', views.dest_sub, name='dest_sub'),
    # ex: /polls/5/results/
    path('<int:trip_event_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:trip_event_id>/vote/', views.vote, name='vote'),
    path('<int:trip_event_id>/votetrip/', views.votetrip, name='votetrip'),
    path('name/', views.get_name, name='get_name'),
    path('your_name/?P<name_display>[A-Z]{3}/', views.your_name, name='your_name'),
    path('add_trip_event/', views.add_trip_event, name='add_trip_event'),
    path('edit_trip_event/', views.edit_trip_event, name='edit_trip_event'),
    path('<int:trip_event_id>/results_vote/', views.results_vote, name='results_vote'),
    path('<int:trip_event_id>/add_participant/', views.add_participant, name='add_participant'),
    path('<int:trip_event_id>/edit_participant/', views.edit_participant, name='edit_participant'),
    path('add_destination/', views.add_destination, name='add_destination'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.login, name='login'),
    path('logout/', auth_views.logout, {'next_page': '/trips/'}, name='logout'),
    path('password_resrt/', auth_views.password_reset, name='password_reset'),
    path('password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         auth_views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    path('admin/', admin.site.urls),
]

