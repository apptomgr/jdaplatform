
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

    path('test_model', views.test_model, name='test_model'),
    path('test_model_edit/<int:pk>', views.test_model_edit, name='test_model_edit'),

]