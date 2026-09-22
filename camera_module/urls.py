from django.urls import path
from .api import detection_api

urlpatterns = [
    path('detect-fire/', detection_api.detect_fire_api, name='api_detect_fire'),
    path('detect-animal/', detection_api.detect_animal_api, name='api_detect_animal'),
    path('detect-human/', detection_api.detect_human_api, name='api_detect_human'),
]
