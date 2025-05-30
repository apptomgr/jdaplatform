
from django.urls import path
from . import views

urlpatterns = [
    path('', views.jdadev_home, name='jdadev_home'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('upload_bond/', views.upload_bond_excel, name='upload_bond_excel'),
    path('upload_mutual_fund_excel/', views.upload_mutual_fund_excel, name='upload_mutual_fund_excel'),
    path('jdadev_stock_report/', views.jdadev_stock_report, name='jdadev_stock_report'),
    path('jdadev_clear_stock_data', views.jdadev_clear_stock_data, name='jdadev_clear_stock_data'),
    path('jdadev_clear_custom_profile', views.jdadev_clear_custom_profile, name='jdadev_clear_custom_profile'),



    #path('upload_institution_type_excel/', views.upload_institution_type_excel, name='upload_institution_type_excel'),
    path('jdadev_bond_report/', views.jdadev_bond_report, name='jdadev_bond_report'),
    path('jdadev_mutual_fund_report/', views.jdadev_mutual_fund_report, name='jdadev_mutual_fund_report'),
    path('jdadev_overall_portfolio/<str:portfolio_type>', views.jdadev_overall_portfolio, name='jdadev_overall_portfolio'),
    path('jdadev_recommendation/', views.jdadev_recommendation, name='jdadev_recommendation'),
    path('jdadev_save_transaction_fees/', views.jdadev_save_transaction_fees, name='jdadev_save_transaction_fees'),
    #path('jdadev_set_custom_profile/', views.jdadev_set_custom_profile, name='jdadev_set_custom_profile'),

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
    path('reload_current_value/<str:id_int>/<str:sym_val>', views.reload_current_value, name='reload_current_value'),
    path('reload_bond_coupon/<str:id_int>/<str:sym_val>', views.reload_bond_coupon, name='reload_bond_coupon'),
    path('reload_depositaire/<str:soc_text>', views.reload_depositaire, name='reload_depositaire'),
    path('reload_opcvm/<str:soc_text>', views.reload_opcvm, name='reload_opcvm'),
    path('reload_mu_total_current_value/<str:id_int>/<str:soc_text>', views.reload_mu_total_current_value, name='reload_mu_total_current_value'),

    path('reload_mu_original_value/<str:id_int>/<str:soc_text>', views.reload_mu_original_value, name='reload_mu_original_value'),
    path('reload_mu_current_value/<str:id_int>/<str:soc_text>', views.reload_mu_current_value, name='reload_mu_current_value'),
    path('reload_mu_nbr_of_share/<str:id_int>/<str:soc_text>', views.reload_mu_nbr_of_share, name='reload_mu_nbr_of_share'),

    path('jdadev_view_client_list', views.jdadev_view_client_list, name='jdadev_view_client_list'),
    path('jdadev_overall_portfolio_by_client/<str:portfolio_type>/<str:client>', views.jdadev_overall_portfolio_by_client, name='jdadev_overall_portfolio_by_client'),

    #Simulation
    path('jdadev_simulation_home', views.jdadev_simulation_home, name='jdadev_simulation_home'),
    path('jdadev_simulation_target_portfolio', views.jdadev_simulation_target_portfolio, name='jdadev_simulation_target_portfolio'),

    path('jdadev_bonds/res/', views.res, name='res'),
    path('jdadev_bonds/res_htmx/', views.res_htmx, name='res_htmx'),
    path('jdadev_bonds/get-selected-value/', views.get_selected_value, name='get_selected_value'),

    path('index/', views.index, name='index'),

    path('get-selected-value/', views.get_selected_value, name='get_selected_value'),

    path('insert_distinct_institution_types', views.insert_distinct_institution_types, name='insert_distinct_institution_types'),
    path('insert_distinct_depositaire', views.insert_distinct_depositaire, name='insert_distinct_depositaire'),
    path('insert_distinct_sociate_de_gession', views.insert_distinct_sociate_de_gession, name='insert_distinct_sociate_de_gession'),

    path('load_cities/', views.load_cities, name='load_cities'),

    #openai stuff
    path('jdadev_ai_validator_home/', views.jdadev_ai_validator_home, name='jdadev_ai_validator_home'),
    path('jdadev_ai_validator_report/', views.jdadev_ai_validator_report, name='jdadev_ai_validator_report'),
    #path('validate/', views.validate_stock_data, name='validate_stock_data'),

    #insert_distinct_institution_types():


]