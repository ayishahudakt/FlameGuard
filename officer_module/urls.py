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
    
    # Fire Alerts
    path('fire-alerts/', views.view_fire_alerts, name='view_fire_alerts_officer'),
    
    # User Alerts
    path('user-alerts/send/', views.send_user_alert, name='send_user_alert'),
    
    # Human Intrusion
    path('intrusions/', views.view_human_intrusion, name='view_human_intrusion'),
    path('intrusions/update/<int:pk>/', views.update_intrusion_status, name='update_intrusion_status'),
    
    # Notifications
    path('notifications/', views.view_notifications, name='view_officer_notifications'),
]
