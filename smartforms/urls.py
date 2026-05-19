from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/backup/export.json', views.export_backup_json, name='dashboard_export_backup'),
    path('dashboard/backup/import.json', views.import_backup_json, name='dashboard_import_backup'),
    path('dashboard/forms/new/', views.form_create, name='dashboard_form_create'),
    path('dashboard/forms/<int:pk>/edit/', views.form_edit, name='dashboard_form_edit'),
    path('dashboard/forms/<int:pk>/toggle/', views.form_toggle_active, name='dashboard_form_toggle'),
    path('dashboard/forms/<int:pk>/delete/', views.form_delete, name='dashboard_form_delete'),
    path('dashboard/forms/<int:pk>/fields/add/', views.field_add, name='dashboard_field_add'),
    path('dashboard/forms/<int:pk>/submissions/', views.submissions_list, name='dashboard_submissions'),
    path('dashboard/forms/<int:pk>/submissions/<int:submission_id>/delete/', views.submission_delete, name='dashboard_submission_delete'),
    path('dashboard/forms/<int:pk>/export.csv', views.export_submissions_csv, name='dashboard_export_csv'),
    path('f/<slug:slug>/', views.form_detail, name='form_detail'),
]
