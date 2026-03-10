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
    
    # Animal Detection
    path('animal-alerts/', views.view_animal_alerts, name='view_animal_alerts'),
    path('animal-alerts/update/<int:pk>/', views.update_animal_alert_status, name='update_animal_alert_status'),
    
    # User Alerts
    path('user-alerts/send/', views.send_user_alert, name='send_user_alert'),
    
    # Human Intrusion
    path('intrusions/', views.view_human_intrusion, name='view_human_intrusion'),
    path('intrusions/update/<int:pk>/', views.update_intrusion_status, name='update_intrusion_status'),
    
    # Notifications
    path('notifications/', views.view_notifications, name='view_officer_notifications'),

    # User (Mobile) Complaints
    path('user-complaints/', views.view_user_complaints, name='view_user_complaints'),
    path('user-complaints/<int:pk>/reply/', views.reply_user_complaint, name='reply_user_complaint'),
]
