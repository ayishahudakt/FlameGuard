from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.officer_login, name='officer_login'),
    path('logout/', views.officer_logout, name='officer_logout'),
    
    # Dashboard
    path('dashboard/', views.officer_dashboard, name='officer_dashboard'),
    
    # Complaints
    path('complaints/send/', views.send_complaint, name='send_complaint'),
    path('complaints/', views.view_officer_complaints, name='view_officer_complaints'),
    
    # Reports
    path('reports/submit/', views.submit_report, name='submit_report'),
    path('my-reports/', views.view_my_reports, name='view_my_reports'),
    
    # Fire Alerts
    path('fire-alerts/', views.view_fire_alerts, name='view_fire_alerts_officer'),
    path('fire-alerts/update/<int:pk>/', views.update_fire_alert_status, name='update_fire_alert_status'),
    path('fire-alerts/send-alert/<int:pk>/', views.send_fire_alert_to_users, name='send_fire_alert_to_users'),
    path('fire-alerts/delete/<int:pk>/', views.delete_fire_alert, name='delete_fire_alert'),
    
    # Animal Detection
    path('animal-alerts/', views.view_animal_alerts, name='view_animal_alerts'),
    path('animal-alerts/update/<int:pk>/', views.update_animal_alert_status, name='update_animal_alert_status'),
    path('animal-alerts/delete/<int:pk>/', views.delete_animal_alert, name='delete_animal_alert'),
    
    # User Alerts
    path('user-alerts/send/', views.send_user_alert, name='send_user_alert'),
    path('user-alerts/sent/', views.view_sent_alerts, name='view_sent_alerts'),
    path('user-alerts/delete/<int:pk>/', views.delete_sent_alert, name='delete_sent_alert'),
    path('user-alerts/toggle/<int:pk>/', views.toggle_sent_alert_status, name='toggle_sent_alert_status'),
    
    # Human Intrusion
    path('intrusions/', views.view_human_intrusion, name='view_human_intrusion'),
    path('intrusions/update/<int:pk>/', views.update_intrusion_status, name='update_intrusion_status'),
    path('intrusions/delete/<int:pk>/', views.delete_human_intrusion, name='delete_human_intrusion'),
    
    # Notifications
    path('notifications/', views.view_notifications, name='view_officer_notifications'),

    # User (Mobile) Complaints
    path('user-complaints/', views.view_user_complaints, name='view_user_complaints'),
    path('user-complaints/<int:pk>/reply/', views.reply_user_complaint, name='reply_user_complaint'),

    # Animal Management (Officer)
    path('animals/', views.officer_manage_animals, name='officer_manage_animals'),
    path('animals/add/', views.officer_add_animal, name='officer_add_animal'),
    path('animals/edit/<int:pk>/', views.officer_edit_animal, name='officer_edit_animal'),
    path('animals/delete/<int:pk>/', views.officer_delete_animal, name='officer_delete_animal'),

    # Preserved Animal Management (Officer)
    path('preserved-animals/', views.officer_manage_preserved_animals, name='officer_manage_preserved_animals'),
    path('preserved-animals/add/', views.officer_add_preserved_animal, name='officer_add_preserved_animal'),
    path('preserved-animals/edit/<int:pk>/', views.officer_edit_preserved_animal, name='officer_edit_preserved_animal'),
    path('preserved-animals/delete/<int:pk>/', views.officer_delete_preserved_animal, name='officer_delete_preserved_animal'),
]
