from django.urls import path
from . import views


urlpatterns = [
    path('', views.jdafinancialsapp_home, name='jdafinancialsapp_home'),
    path('jdafinancialsapp_stmts', views.jdafinancialsapp_stmts, name='jdafinancialsapp_stmts'),
    path('jdafinancialsapp_new_company', views.jdafinancialsapp_new_company, name='jdafinancialsapp_new_company'),
    path('jdafinancialsapp_company_listing', views.jdafinancialsapp_company_listing, name='jdafinancialsapp_company_listing'),
    path('jdafinancialsapp_view_company_detail/<int:pk>', views.jdafinancialsapp_view_company_detail, name='jdafinancialsapp_view_company_detail'),
    path('jdafinancialsapp_delete_company_confirm/<int:pk>', views.jdafinancialsapp_delete_company_confirm, name='jdafinancialsapp_delete_company_confirm'),

    path('jdafinancialsapp_bal_entry_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>', views.jdafinancialsapp_bal_entry_form, name='jdafinancialsapp_bal_entry_form'),
    path('jdafinancialsapp_bal_edit_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_bal_edit_form, name='jdafinancialsapp_bal_edit_form'),
    path('jdafinancialsapp_bal_rpt/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>', views.jdafinancialsapp_bal_rpt, name='jdafinancialsapp_bal_rpt'),

    path('jdafinancialsapp_inc_entry_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inc_entry_form, name='jdafinancialsapp_inc_entry_form'),
    path('jdafinancialsapp_inc_edit_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inc_edit_form, name='jdafinancialsapp_inc_edit_form'),
    path('jdafinancialsapp_inc_rpt/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inc_rpt, name='jdafinancialsapp_inc_rpt'),

    path('jdafinancialsapp_inv_acct_entry_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inv_acct_entry_form, name='jdafinancialsapp_inv_acct_entry_form'),
    path('jdafinancialsapp_inv_acct_edit_form/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inv_acct_edit_form, name='jdafinancialsapp_inv_acct_edit_form'),
    path('jdafinancialsapp_inv_acct_rpt/<str:sector>/<int:company_id>/<str:statement>/<str:entry_date>',views.jdafinancialsapp_inv_acct_rpt, name='jdafinancialsapp_inv_acct_rpt'),

    path('jdafinancialsapp_bal_all_rpt', views.jdafinancialsapp_bal_all_rpt, name='jdafinancialsapp_bal_all_rpt'),

    # Securities
    path('jdafinancialsapp_add_stock_security', views.jdafinancialsapp_add_stock_security, name='jdafinancialsapp_add_stock_security'),
    path('jdafinancialsapp_add_bond_security', views.jdafinancialsapp_add_bond_security, name='jdafinancialsapp_add_bond_security'),
    path('jdafinancialsapp_security_listing', views.jdafinancialsapp_security_listing, name='jdafinancialsapp_security_listing'),
    path('jdafinancialsapp_view_security_detail/<int:pk>', views.jdafinancialsapp_view_security_detail, name='jdafinancialsapp_view_security_detail'),

    # misc
    path('res', views.res, name='res'),


    #path('jdafinancialsapp_inc_entry_formset/<str:sector>/<int:company_id>/<str:publication_date>/<str:statement>', views.jdafinancialsapp_inc_entry_formset, name='jdafinancialsapp_inc_entry_formset'),


    path('financialStatementFactForm/', views.financialStatementFactForm, name='financialStatementFactForm'),

    path('language_formset/', views.language_formset, name='language_formset'),
    path('language_inline_formset/', views.language_inline_formset, name='language_inline_formset'),
    path('shareholder_formset/', views.shareholder_formset, name='shareholder_formset'),


    path('financial_fact_formset/', views.financial_fact_formset, name='financial_fact_formset'),

    path('res/', views.res, name='res'),
]