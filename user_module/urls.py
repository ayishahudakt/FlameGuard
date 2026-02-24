from django.urls import path
from . import views

urlpatterns = [
    path('user/login/',     views.user_login,    name='user-login'),
    path('user/register/',  views.user_register, name='user-register'),
    path('fire-alerts/',    views.fire_alerts,   name='fire-alerts'),
    path('animal-alerts/',  views.animal_alerts, name='animal-alerts'),
    path('notifications/',  views.notifications, name='notifications'),
    path('complaints/',     views.complaints,    name='complaints'),
    path('animals/',        views.animals,       name='animals'),
    path('contacts/',       views.contacts,      name='contacts'),
    path('divisions/',      views.divisions,     name='divisions'),
]
