
from django.urls import path
from . import views

urlpatterns = [
    path('', views.jdadev_home, name='jdadev_home'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('upload_bond/', views.upload_bond_excel, name='upload_bond_excel'),
    path('upload_mutual_fund_excel/', views.upload_mutual_fund_excel, name='upload_mutual_fund_excel'),
    path('jdadev_stock_report/', views.jdadev_stock_report, name='jdadev_stock_report'),

    #path('upload_institution_type_excel/', views.upload_institution_type_excel, name='upload_institution_type_excel'),
    path('jdadev_bond_report/', views.jdadev_bond_report, name='jdadev_bond_report'),
    path('jdadev_mutual_fund_report/', views.jdadev_mutual_fund_report, name='jdadev_mutual_fund_report'),
    path('jdadev_overall_portfolio/<str:portfolio_type>', views.jdadev_overall_portfolio, name='jdadev_overall_portfolio'),
    #path('jdadev_ovp_dynamic/', views.jdadev_ovp_dynamic, name='jdadev_ovp_dynamic'),
    #path('jdadev_ovp_balanced/', views.jdadev_ovp_balanced, name='jdadev_ovp_balanced'),
    #path('jdadev_ovp_prudent/', views.jdadev_ovp_prudent, name='jdadev_ovp_prudent'),

    path('jdadev_liquid_assets/', views.jdadev_liquid_assets, name='jdadev_liquid_assets'),
    path('jdadev_equity_and_rights/', views.jdadev_equity_and_rights, name='jdadev_equity_and_rights'),
    path('jdadev_bonds/', views.jdadev_bonds, name='jdadev_bonds'),
    path('jdadev_mutual_funds/', views.jdadev_mutual_funds, name='jdadev_mutual_funds'),
    #path('reload-bonds-formset/', views.reload_bonds_formset, name='reload_bonds_formset'),

    path('jdadev_client_portfolio/', views.jdadev_client_portfolio, name='jdadev_client_portfolio'),
    path('fetch-stock-data/', views.fetch_stock_data, name='fetch_stock_data'),
    path('portfolio/', views.create_or_update_portfolio, name='create_or_update_portfolio'),
    path('portfolio/success/', views.portfolio_success, name='portfolio_success'),
    #path('reload-bonds-formset/', views.reload_bonds_formset, name='reload_bonds_formset'),
    path('reload_symbols/<str:inst_val>', views.reload_symbols, name='reload_symbols'),
    path('reload_bond_names/<str:sym_val>', views.reload_bond_names, name='reload_bond_names'),
    path('reload_original_value/<str:id_int>/<str:sym_val>', views.reload_original_value, name='reload_original_value'),
    path('reload_depositaire/<str:soc_text>', views.reload_depositaire, name='reload_depositaire'),
    path('reload_opcvm/<str:soc_text>', views.reload_opcvm, name='reload_opcvm'),
    path('reload_mu_total_current_value/<str:id_int>/<str:soc_text>', views.reload_mu_total_current_value, name='reload_mu_total_current_value'),

    path('reload_mu_original_value/<str:id_int>/<str:soc_text>', views.reload_mu_original_value, name='reload_mu_original_value'),
    path('reload_mu_current_value/<str:id_int>/<str:soc_text>', views.reload_mu_current_value, name='reload_mu_current_value'),
    path('reload_mu_nbr_of_share/<str:id_int>/<str:soc_text>', views.reload_mu_nbr_of_share, name='reload_mu_nbr_of_share'),


    path('jdadev_bonds/res/', views.res, name='res'),
    path('jdadev_bonds/res_htmx/', views.res_htmx, name='res_htmx'),
    path('jdadev_bonds/get-selected-value/', views.get_selected_value, name='get_selected_value'),

    path('index/', views.index, name='index'),

    path('get-selected-value/', views.get_selected_value, name='get_selected_value'),

    path('insert_distinct_institution_types', views.insert_distinct_institution_types, name='insert_distinct_institution_types'),
    path('insert_distinct_depositaire', views.insert_distinct_depositaire, name='insert_distinct_depositaire'),
    path('insert_distinct_sociate_de_gession', views.insert_distinct_sociate_de_gession, name='insert_distinct_sociate_de_gession'),

    path('load_cities/', views.load_cities, name='load_cities'),

    #insert_distinct_institution_types():


]