
from django.urls import path
from . import views
# from django.utils.text import slugify

urlpatterns = [
    path('', views.jdapublicationsapp_home, name='jdapublicationsapp_home'),
    path('jdapublicationsapp_dept/', views.jdapublicationsapp_dept, name='jdapublicationsapp_dept'),
    path('jdapublicationsapp_pubs/', views.jdapublicationsapp_pubs, name='jdapublicationsapp_pubs'),
    # path('jdapublicationsapp_pubs/<str:pub_lang>', views.jdapublicationsapp_pubs_lang, name='jdapublicationsapp_pubs_lang'),

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
    # path('jdapublicationsapp_view_one_pub/<str:folder>/<str:yr>/<str:mon>/<str:file_name>', views.jdapublicationsapp_view_one_pub, name='jdapublicationsapp_view_one_pub'),
    # path('jdapublicationsapp_view_watermarked_pub/<str:file_name>', views.jdapublicationsapp_view_watermarked_pub, name='jdapublicationsapp_view_watermarked_pub'),
    # Securities
    # path('jdafinancialsapp_add_security', views.jdafinancialsapp_add_security, name='jdafinancialsapp_add_security'),

    # misc
    path('tes/', views.tes, name='tes'),
    path('jda_simple_form_tester/', views.jda_simple_form_tester, name='jda_simple_form_tester'),
]