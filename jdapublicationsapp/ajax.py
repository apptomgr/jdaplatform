from django.http import HttpResponse, Http404
#from .forms import FullSearchForm, TypeEmptyForm, TypeModelSearchForm, CitySenegalForm, CityFranceForm


""" jdapublicationapp_ajax_set_type """
def jdapublicationapp_ajax_set_type(request, id_param):
    if request.is_ajax:
        city=''
        if id_param=='models':
            pass
            #form=TypeModelSearchForm()

        elif id_param=='newsletter':
            pass
            #form=TypeModelSearchForm()
        else:
            #form=TypeEmptyForm()
            pass

        response = 'form'

        return HttpResponse(response)
    else:
        return Http404


""" ajax_tester_btn"""
def ajax_tester_btn(request):
    if request.is_ajax:
        response= "You clicked here!"
        print(response)
        return HttpResponse(response)
    else:
        return Http404




""" ajax_selected"""
def ajax_selected(request):
    if request.is_ajax:
        response= "You clicked here!"
        print(response)
        return HttpResponse(response)
    else:
        return Http404


# """ ajax_dropdown_test"""
# def ajax_dropdown_test(request, id_param):
#     print(f"28: //////////////id_param: {id_param}")
#     if request.is_ajax:
#         city=''
#         if id_param=='senegal':
#             form=CitySenegalForm()
#         elif id_param=='france':
#             form=CityFranceForm()
#         else:
#             city=f'Unkn {id_param}'
#
#
#
#         #response= f"from ajax.py -  ajax_dropdown_test id_param: {city}"
#         response = form
#
#         return HttpResponse(response)
#     else:
#         return Http404