
from django.urls import path
from . import views

urlpatterns = [
    path('', views.jdatester_home, name='jdatester_home'),
    path('fact', views.jdatester_fact, name='jdatester_fact'),
    path('fact_form', views.jdatester_fact_form, name='jdatester_fact_form'),
    path('ed', views.jdatester_ed, name='jdatester_ed'),
    path('jdatester_book_formset', views.jdatester_book_formset, name='jdatester_book_formset'),
    path('jdatester_book_inline_formset', views.jdatester_book_inline_formset, name='jdatester_book_inline_formset'),

    path('jdatester_bal_dash', views.jdatester_bal_dash, name='jdatester_bal_dash'),
    path('jdatester_bal/<str:company>/<str:entry_date>', views.jdatester_bal, name='jdatester_bal'),
    #path('jdatester_bal_edit/<int:pk>', views.jdatester_bal_edit, name='jdatester_bal_edit'),

    path('jdatester_export', views.jdatester_export_data, name='jdatester_export_data'),
    path('jdatester_import', views.jdatester_import_data, name='jdatester_import_data'),

    path('jdatester_load_xls', views.jdatester_load_xls, name='jdatester_load_xls'),
    #path('jdatester_index', views.jdatester_index, name='jdatester_index'),
    #path('jdatester_sec_filter', views.jdatester_sec_filter, name='jdatester_sec_filter'),

    path('blog_listing', views.blog_listing, name='blog_listing'),
    path('blog_view/<int:blog_id>', views.blog_view, name='blog_view'),
    path('blog_see_request', views.blog_see_request, name='blog_see_request'),
    path('blog_user_info', views.blog_user_info, name='blog_user_info'),
    path('blog_private_place', views.blog_private_place, name='blog_private_place'),
    path('blog_staff_place', views.blog_staff_place, name='blog_staff_place'),








    path('test_model', views.test_model, name='test_model'),
    path('test_model_edit/<int:pk>', views.test_model_edit, name='test_model_edit'),

]