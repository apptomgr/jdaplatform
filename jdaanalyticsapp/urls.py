from django.urls import path
from . import views


urlpatterns = [
    path('', views.jdaanalyticsapp_home, name='jdaanalyticsapp_home'),
    path('jdaanalyticsapp_upload_form/', views.jdaanalyticsapp_upload_form, name='jdaanalyticsapp_upload_form'),
    path('jdaanalyticsapp_rpt/', views.jdaanalyticsapp_rpt, name='jdaanalyticsapp_rpt'),
    path('jdaanalyticsapp_sec_filter/', views.jdaanalyticsapp_sec_filter, name='jdaanalyticsapp_sec_filter'),
    #path('jdaanalyticsapp_view_book>', views.jdaanalyticsapp_view_book, name='jdaanalyticsapp_view_book'),
    #path('jdaanalyticsapp_create_book/<int:pk>', views.jdaanalyticsapp_create_book, name='jdaanalyticsapp_create_book')

]
