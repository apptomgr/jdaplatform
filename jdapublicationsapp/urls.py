
from django.urls import path
from . import views #, ajax

urlpatterns = [
    path('', views.jdapublicationsapp_home, name='jdapublicationsapp_home'),
    path('jdapublicationsapp_dept/', views.jdapublicationsapp_dept, name='jdapublicationsapp_dept'),
    path('jdapublicationsapp_pubs/', views.jdapublicationsapp_pubs, name='jdapublicationsapp_pubs'),
    path('jdapublicationsapp_filter/', views.jdapublicationsapp_filter, name='jdapublicationsapp_filter'),
    path('jdapublicationsapp_fullSearch/', views.jdapublicationsapp_fullSearch, name='jdapublicationsapp_fullSearch'),
    path('jdapublicationsapp_entry/', views.jdapublicationsapp_entry, name='jdapublicationsapp_entry'),
    path('jdapublicationsapp_edit/<int:pk>', views.jdapublicationsapp_edit, name='jdapublicationsapp_edit'),
    path('jdapublicationsapp_listing/', views.jdapublicationsapp_listing, name='jdapublicationsapp_listing'),
    path('jdapublicationsapp_delete/<int:pk>', views.jdapublicationsapp_delete, name='jdapublicationsapp_delete'),
    path('jdapublicationsapp_company_listing/', views.jdapublicationsapp_company_listing, name='jdapublicationsapp_company_listing'),
    path('jdapublicationsapp_new_company/', views.jdapublicationsapp_new_company, name='jdapublicationsapp_new_company'),
    path('jdapublicationsapp_delete_company_confirm/<int:pk>', views.jdapublicationsapp_delete_company_confirm, name='jdapublicationsapp_delete_company_confirm'),
    path('jdapublicationsapp_delete_company_yes/<int:pk>', views.jdapublicationsapp_delete_company_yes, name='jdapublicationsapp_delete_company_yes'),

    path('tes/', views.tes, name='tes'),
    path('jda_simple_form_tester/', views.jda_simple_form_tester, name='jda_simple_form_tester'),

#    path('jda_ajax_tester/', views.jda_ajax_tester, name='jda_ajax_tester'),
#    path('jda_ajax_tester/ajax_tester_btn', ajax.ajax_tester_btn, name='ajax_tester_btn'),
#    path('jda_ajax_tester/ajax_selected', ajax.ajax_selected, name='ajax_selected'),
#    path('jda_ajax_tester/ajax_dropdown_test/<str:id_param>', ajax.ajax_dropdown_test, name='ajax_dropdown_test'),

#    path('jdapublicationsapp_ajax_set_type/<str:id_param>', ajax.jdapublicationsapp_ajax_set_type, name='jdapublicationsapp_ajax_set_type'),



]