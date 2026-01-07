from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    
    # Dashboard
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Forest Division Management
    path('divisions/', views.manage_divisions, name='manage_divisions'),
    path('divisions/add/', views.add_division, name='add_division'),
    path('divisions/edit/<int:pk>/', views.edit_division, name='edit_division'),
    path('divisions/delete/<int:pk>/', views.delete_division, name='delete_division'),
    
    # Forest Station Management
    path('stations/', views.manage_stations, name='manage_stations'),
    path('stations/add/', views.add_station, name='add_station'),
    path('stations/edit/<int:pk>/', views.edit_station, name='edit_station'),
    path('stations/delete/<int:pk>/', views.delete_station, name='delete_station'),
    
    # Animal Management
    path('animals/', views.manage_animals, name='manage_animals'),
    path('animals/add/', views.add_animal, name='add_animal'),
    path('animals/edit/<int:pk>/', views.edit_animal, name='edit_animal'),
    path('animals/delete/<int:pk>/', views.delete_animal, name='delete_animal'),
    
    # Preserved Animal Management
    path('preserved-animals/', views.manage_preserved_animals, name='manage_preserved_animals'),
    path('preserved-animals/add/', views.add_preserved_animal, name='add_preserved_animal'),
    
    # Forest Officer Management
    path('officers/', views.manage_officers, name='manage_officers'),
    path('officers/add/', views.add_officer, name='add_officer'),
    path('officers/allocate/<int:pk>/', views.allocate_officer, name='allocate_officer'),
    
    # Complaint Management
    path('complaints/', views.view_complaints, name='view_complaints'),
    path('complaints/reply/<int:pk>/', views.reply_complaint, name='reply_complaint'),
    
    # Notifications
    path('notifications/send/', views.send_notification, name='send_notification'),
    
    # Reports
    path('reports/', views.view_reports, name='view_reports'),
    
    # Fire Alerts
    path('fire-alerts/', views.view_fire_alerts, name='view_fire_alerts'),
    path('fire-alerts/update/<int:pk>/', views.update_fire_alert, name='update_fire_alert'),
]
