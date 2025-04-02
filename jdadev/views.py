import requests
from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import StockDailyValuesModel, BondModel, MutualFundModel, ClientPortfolioModel, ClientMutualFundsModel, DepositaireModel, SociateDeGessionModel
import pandas as pd  # For working with Excel files
from django.http import HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ValidationError
import numpy as np
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import ClientPortfolioModel, ClientEquityAndRightsModel, ClientBondsModel, InstitutionTypeModel
from .forms import ClientPortfolioForm, ClientEquityAndRightsForm, ClientEquityAndRightsFormset, ClientEquityAndRightsFormset_edit, ClientBondsForm, ClientBondsFormset, ClientBondsFormset_edit, ClientMutualFundsFormset, ClientMutualFundsFormset_edit
from accounts .decorators import allowed_users
from django.db.models import Sum
from django.contrib.auth.models import User

#/////////////////////////////////jdadev_home////////////////////
@login_required
def jdadev_home(request):
    user = request.user
    #print(f"User={user.username} - request.user={request.user}")
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    if client_portfolio is None:
        client_portfolio = ClientPortfolioModel(client=user)

    #print(f"Client Portfolio: {client_portfolio}")
    total_value_sum = ClientEquityAndRightsModel.objects.filter(client=user).aggregate(total_sum=Sum('total_current_value'))['total_sum'] or 0.00
    #print(f"total_value_sum: {total_value_sum}")
    update_equity_and_rights(request, total_value_sum)

    if request.method == 'POST':
        # Handling POST request for form and formset submissions
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)
        stock_formset = ClientEquityAndRightsFormset(request.POST)
        #print(f"30 -stock_formset: {stock_formset}")
        if form.is_valid() and stock_formset.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
            # Save each form in the formset
            stock_forms = stock_formset.save(commit=False)
            for stock_form in stock_forms:
                stock_form.client = user
                stock_form.save()

            messages.success(request, f"{client_portfolio} info successfully added")
            return redirect('jdadev_client_portfolio')
        else:
            # Debugging and displaying form errors
            #print("Form errors:", form.errors)
            #print("Formset errors:", stock_formset.errors)
            messages.warning(request, f"Form error: {form.errors} - Formset error: {[formset.errors for formset in stock_formset]}")
    else:
        # Handling GET request to display forms
        # Client form
        #print(f"Client Portfolio: {client_portfolio}")
        form = ClientPortfolioForm(instance=client_portfolio)

        # Equity and rights formset
        stock_formsets = ClientEquityAndRightsModel.objects.filter(client=user).first()
        #print(f"Stock Formsets: {stock_formsets}")
        if stock_formsets:
            stock_formset = ClientEquityAndRightsFormset_edit(queryset=ClientEquityAndRightsModel.objects.filter(client=user)) #, total_value_sum=total_value_sum)
        else:
            stock_formset = ClientEquityAndRightsFormset(queryset=ClientEquityAndRightsModel.objects.filter(client=user))

        # Bonds formset for
        bonds_formset = ClientBondsModel.objects.filter(client=user).first()
        if bonds_formset:
            bonds_formset = ClientBondsFormset_edit(queryset=ClientBondsModel.objects.filter(client=user))
        else:
            bonds_formset = ClientBondsFormset(queryset=ClientBondsModel.objects.filter(client=user))

    context = {'form': form, 'client_portfolio': client_portfolio,'client':user, 'stock_formset':stock_formset, 'bonds_formset':bonds_formset}
    return render(request, 'jdadev/jdadev_portfolio_management_home.html', context)


#/////////////////////////////////jdadev_liquid_assets////////////////////
@login_required
def jdadev_liquid_assets(request):
    #print("jdadev_liquid_assets")
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)

        if form.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
            messages.success(request, f"{client_portfolio} info successfully added")
            return redirect('jdadev_liquid_assets')
        else:
            messages.warning(request,f"Form error: {form.errors}")
    else:
        form = ClientPortfolioForm(instance=client_portfolio)

    context = {'form': form, 'client':user}
    return render(request, 'jdadev/jdadev_liquid_assets.html', context)


#/////////////////////////////////jdadev_equity_and_rights////////////////////
@login_required
def jdadev_equity_and_rights(request):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)
        stock_formset = ClientEquityAndRightsFormset(request.POST)

        if form.is_valid() and stock_formset.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
           # Save each form in the formset
            stock_forms = stock_formset.save(commit=False)
            for stock_form in stock_forms:
                stock_form.client = user
                stock_form.save()

           # Now check if the delete flag was on
            del_pk=[]
            for idx, form in enumerate(stock_formset):
                if request.POST.get(f'form-{idx}-DELETE') == 'on':
                    #print("127 - Delete flag on")
                    #print(f"128 - idx:{idx}")
                    eq_item=ClientEquityAndRightsModel.objects.filter(client=user)
                    #print(f"130 -{eq_item}")
                    #print(eq_item[idx].pk)
                    del_pk.append(eq_item[idx].pk)
                    #print(f"134 - del_pk: {del_pk}")
                    del_eq_item = ClientEquityAndRightsModel.objects.filter(client=user).filter(pk__in=del_pk)
                    print(f"136 - del_eq_item: {del_eq_item} - {del_eq_item[0].stocks}")
                    msg_eq_item = str(del_eq_item[0].stocks) # copy of the item to be deleted to pass to message
                    del_eq_item.delete()
                    #ClientEquityAndRightsModel.objects.filter(client=user).filter(pk__in=del_pk).delete()

                    messages.success(request, f"{msg_eq_item} stock is successfully deleted")
            if len(del_pk) <= 0:
                messages.success(request, f"{client_portfolio} info successfully added")
            #Now update the stock total_current_value to refresh the UI
            total_value_sum = ClientEquityAndRightsModel.objects.filter(client=user).aggregate(total_sum=Sum('total_current_value'))['total_sum'] or 0.00
            update_equity_and_rights(request, total_value_sum)

            return redirect('jdadev_equity_and_rights')
        else:
            # Debugging and displaying form errors
            #print("Form errors:", form.errors)
            #print("Formset errors:", stock_formset.errors)
            messages.warning(request, f"Form error: {form.errors} - Formset error: {[formset.errors for formset in stock_formset]}")

    else:
        form = ClientPortfolioForm(instance=client_portfolio)
        # Equity and rights formset
        stock_formsets = ClientEquityAndRightsModel.objects.filter(client=user).first()
        #print(f"Stock Formsets: {stock_formsets}")
        if stock_formsets:
            stock_formset = ClientEquityAndRightsFormset_edit(queryset=ClientEquityAndRightsModel.objects.filter(client=user)) #, total_value_sum=total_value_sum)
        else:
            stock_formset = ClientEquityAndRightsFormset(queryset=ClientEquityAndRightsModel.objects.filter(client=user))

    total_value_sum = ClientEquityAndRightsModel.objects.filter(client=user).aggregate(total_sum=Sum('total_current_value'))['total_sum'] or 0.00
    #print(f"total_value_sum: {total_value_sum}")
    update_equity_and_rights(request, total_value_sum)

    context = {'form': form, 'client_portfolio': client_portfolio,'client':user, 'stock_formset':stock_formset}
    #context = {'form': form, 'client':user,}
    return render(request, 'jdadev/jdadev_equity_and_rights.html', context)

#/////////////////////////////////jdadev_bonds///////////////////////////
@login_required
def jdadev_bonds(request):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()

    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)
        #print(f"181: {form}")
        bonds_formset = ClientBondsFormset(request.POST)
        #print(f"183: {bonds_formset}")

        if form.is_valid() and bonds_formset.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
            # Save each form in the formset
            bond_forms = bonds_formset.save(commit=False)
            for bond_form in bond_forms:
                bond_form.client = user
                bond_form.save()


            #///////
            # Now check if the delete flag was on
            del_pk=[]
            for idx, form in enumerate(bonds_formset):
                if request.POST.get(f'form-{idx}-DELETE') == 'on':
                    #print("127 - Delete flag on")
                    #print(f"128 - idx:{idx}")
                    bn_item=ClientBondsModel.objects.filter(client=user)
                    #print(f"130 -{eq_item}")
                    #print(eq_item[idx].pk)
                    del_pk.append(bn_item[idx].pk)
                    #print(f"134 - del_pk: {del_pk}")
                    del_bn_item = ClientBondsModel.objects.filter(client=user).filter(pk__in=del_pk)
                    print(f"136 - del_bn_item: {del_bn_item} - {del_bn_item[0].bond_name}")
                    msg_bn_item = str(del_bn_item[0].bond_name) # copy of the item to be deleted to pass to message
                    del_bn_item.delete()

                    messages.success(request, f"{msg_bn_item} bond is successfully deleted")
            if len(del_pk) <= 0:
                messages.success(request, f"{client_portfolio} info successfully added")

            #Now update the bond's total_current_value to refresh the UI
            total_value_sum = ClientBondsModel.objects.filter(client=user).aggregate(total_sum=Sum('total_current_value'))['total_sum'] or 0.00
            update_bonds(request, total_value_sum)
            #/////////


            #messages.success(request, f"{client_portfolio} info successfully added")
            return redirect('jdadev_bonds')
        else:
            messages.warning(request, f"Form error: {form.errors} - Formset error: {[formset.errors for formset in bonds_formset]}")
    else:
        form = ClientPortfolioForm(instance=client_portfolio)
        if ClientBondsModel.objects.filter(client=user).exists():
            bonds_formset = ClientBondsFormset_edit(queryset=ClientBondsModel.objects.filter(client=user))
        else:
            bonds_formset = ClientBondsFormset(queryset=ClientBondsModel.objects.filter(client=user))


    context = {'form': form, 'client_portfolio': client_portfolio, 'client': user, 'bonds_formset': bonds_formset, 'total_form_count': bonds_formset.total_form_count}
    return render(request, 'jdadev/jdadev_bonds.html', context)

#/////////////////////////////////jdadev_mutual_funds///////////////////////////
@login_required
def jdadev_mutual_funds(request):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"191 Client: {client_portfolio}")
    #print(f"192 User: {user}")
    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)
        mutual_funds_formset = ClientMutualFundsFormset(request.POST)

        if form.is_valid() and mutual_funds_formset.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
            mututal_fund_forms = mutual_funds_formset.save(commit=False)
            #print("254 - Attempting to save mutual_fund_formset")
            for mutual_fund_form in mututal_fund_forms:
                mutual_fund_form.client = user
                mutual_fund_form.save()

            #total_value_sum = ClientMutualFundsModel.objects.filter(client=user).aggregate(total_sum=Sum('mu_total_current_value'))['total_sum'] or 0.00
            #update_mutual_funds(request, total_value_sum)
            #print(f"209 save mu formset: {client_portfolio}")


            #messages.success(request, f"{client_portfolio} info successfully added")
            #///////
            # Now check if the delete flag was on
            del_pk=[]
            for idx, form in enumerate(mutual_funds_formset):
                if request.POST.get(f'form-{idx}-DELETE') == 'on':
                    #print("270 - Delete flag on")
                    #print(f"217 - idx:{idx}")
                    mu_item=ClientMutualFundsModel.objects.filter(client=user)
                    #print(f"273 -{mu_item}")
                    #print(mu_item[idx].pk)
                    del_pk.append(mu_item[idx].pk)
                    #print(f"276 - del_pk: {del_pk}")
                    del_mu_item = ClientMutualFundsModel.objects.filter(client=user).filter(pk__in=del_pk)
                    #print(f"278 - del_mu_item: {del_mu_item} - {del_mu_item[0].opcvm}")
                    msg_mu_item = str(del_mu_item[0].opcvm) # copy of the item to be deleted to pass to message
                    del_mu_item.delete()

                    messages.success(request, f"{msg_mu_item} mutual fund is successfully deleted")
            if len(del_pk) <= 0:
                messages.success(request, f"{client_portfolio} info successfully added")

            #Now update the mututal's total_current_value to refresh the UI
            total_value_sum = ClientMutualFundsModel.objects.filter(client=user).aggregate(total_sum=Sum('mu_total_current_value'))['total_sum'] or 0.00
            update_mutual_funds(request, total_value_sum)
            #/////////


            #messages.success(request, f"{client_portfolio} info successfully added")

            return redirect('jdadev_mutual_funds')
        else:
            messages.warning(request, f"Form error: {form.errors} - Formset error: {[formset.errors for formset in mutual_funds_formset]}")
    else:
        form = ClientPortfolioForm(instance=client_portfolio)
        if ClientMutualFundsModel.objects.filter(client=user).exists():
            mutual_funds_formset = ClientMutualFundsFormset_edit(queryset=ClientMutualFundsModel.objects.filter(client=user))
        else:
            mutual_funds_formset = ClientMutualFundsFormset(queryset=ClientMutualFundsModel.objects.filter(client=user))

    #print(f"444 - mutual_funds_formset[0].depositaire: {mutual_funds_formset[0].depositaire}")
    #print(form)

    context = {'form': form, 'client_portfolio': client_portfolio, 'client': user, 'mutual_funds_formset': mutual_funds_formset, 'total_form_count': mutual_funds_formset.total_form_count}
    return render(request, 'jdadev/jdadev_mutual_funds.html', context)

#////////////////////////////////jdadev_overall_portfolio////////////////////////////////
@login_required
def jdadev_overall_portfolio(request, portfolio_type):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    ovp= ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"ovp:{ovp}")

    if ovp:
        la  = ovp.liquid_assets
        eqr = ovp.equity_and_rights
        bn  = ovp.bonds
        mu = ovp.mutual_funds
        tot=la+eqr+bn+mu
        custom_form =None

        per_tot=(tot/tot)
        per_la=(la/tot)
        per_eqr=(eqr/tot)
        per_bn=(bn/tot)
        per_mu=(mu/tot)

        #adj_bn=adjusted_per_bn(portfolio_type,per_tot,per_bn,per_mu)[0]
        #adj_mu=adjusted_per_bn(portfolio_type,per_tot,per_bn,per_mu)[1]
        #print(f"332 caller: adj_bn:{adj_bn} - adj_mu:{adj_mu}")
        per_lst=[]
        val_lst=[]
        if portfolio_type == 'overall_portfolio':
            per_lst.append(per_tot*100)
            per_lst.append(per_la*100)
            per_lst.append(per_eqr*100)
            per_lst.append(per_bn*100)
            per_lst.append(per_mu*100)

            val_lst.append(tot)
            val_lst.append(la)
            val_lst.append(eqr)
            val_lst.append(bn)
            val_lst.append(mu)

        elif portfolio_type == 'dynamic':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.05)) #
            val_lst.append(tot*Decimal(.55))
            val_lst.append(tot*Decimal(.20))
            val_lst.append(tot*Decimal(.20))

            per_lst.append((tot/tot)*100)
            per_lst.append(.05*100)
            per_lst.append(.55*100)
            per_lst.append(.20*100)
            per_lst.append(.20*100)

        elif portfolio_type == 'moderate':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.05))
            val_lst.append(tot*Decimal(.40))
            val_lst.append(tot*Decimal(.35))
            val_lst.append(tot*Decimal(.20))
            per_lst.append((tot/tot)*100)
            per_lst.append(.05*100)
            per_lst.append(.40*100)
            per_lst.append(.35*100)
            per_lst.append(.20*100)

        elif portfolio_type == 'prudent':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.05))
            val_lst.append(tot*Decimal(.20))
            val_lst.append(tot*Decimal(.55))
            val_lst.append(tot*Decimal(.20))
            per_lst.append((tot/tot)*100)
            per_lst.append(.05*100)
            per_lst.append(.20*100)
            per_lst.append(.55*100)
            per_lst.append(.20*100)
        elif portfolio_type == 'custom':
            #Show user default portfolio values
            per_lst.append(per_tot*100)
            per_lst.append(per_la*100)
            per_lst.append(per_eqr*100)
            per_lst.append(per_bn*100)
            per_lst.append(per_mu*100)

            val_lst.append(tot)
            val_lst.append(la)
            val_lst.append(eqr)
            val_lst.append(bn)
            val_lst.append(mu)
            # User will have to provide custom values
            #print(f"386 - Custom portfolio not implemented yet")
            # redirect to custom_profile_form loaded via htmx to a partial custom profile page
            custom_form = CustomProfileForm()
            #context={'custom_form': custom_form, 'tes':'tes'}
            #print("redirecting to")
            #return redirect('jdadev_overall_portfolio.html', context)
    else:
        #print("Invalid portfolio type")
        return redirect('jdadev_home')

    context={'client_portfolio': client_portfolio,'client':user,'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst, 'custom_form': custom_form, 'tes':'tes'}
    return render(request, 'jdadev/jdadev_overall_portfolio.html', context)

#////////////////////////////////////////////////////////////////////////////////////
# views.py
from django.shortcuts import render, redirect
from .forms import CustomProfileForm

def jdadev_custom_portfolio(request):
    # Handle form submission
    if request.method == 'POST':
        form = CustomProfileForm(request.POST)
        if form.is_valid():
            # Process data (e.g., save to session/database)
            request.session['custom_allocation'] = form.cleaned_data
            # Return the display partial with submitted data
            return render(request, 'partials/custom_profile_display.html', form.cleaned_data)
        else:
            # Re-render form with errors
            return render(request, 'partials/custom_profile_form.html', {'form': form})

    # Handle initial GET request
    portfolio_type = request.GET.get('portfolio_type')

    #if portfolio_type == 'custom':
    form = CustomProfileForm()
    #    return render(request, 'partials/custom_profile_form.html', {'form': form})
    #else:
    context={"form": form}
    return context
#//////////////////////////////// adjusted_per_bn //////////////////////////////////

def adjusted_per_bn(portfolio_type, per_tot, per_bn, per_mu):
    print(f"394 per_tot: {per_tot}")
    print(f"395 per_bn: {per_bn} - per_mu: {per_mu}")
    adj_bn = 0
    adj_mu = 0
    adj_vals=[]
    if portfolio_type =='dynamic':
        if per_bn+per_mu >per_tot*Decimal(.20):
            print(f"401 If per_bn+per_mu: {per_bn+per_mu} > per_tot*20: {per_tot*Decimal(.20)}")
            x_mu=per_tot*Decimal(.20)-per_mu
            print(f"403 - x_mu: {x_mu}")
            if x_mu <0:
                adj_bn=0
                adj_mu =.20
            else:
                adj_bn=x_mu
                adj_mu=per_mu

            print(f"411 x_mu: {x_mu} - per_mu:{per_mu}- adj_bn: {adj_bn} - adj_mu: {adj_mu}")
        else:
            #print(f"<Else per_tot*20: {per_tot*Decimal(.20)}")
            adj_bn=per_tot*Decimal(.20)-per_mu
            adj_mu=per_mu
    elif portfolio_type =='moderate':
        if per_bn+per_mu >per_tot*Decimal(.45):
            x_mu=per_tot*Decimal(.45)-per_mu
            if x_mu <0:
                adj_bn=0
                adj_mu =.45
            else:
                adj_bn=x_mu
                adj_mu=per_mu
        else:
            adj_bn=per_tot*Decimal(.45)-per_mu
            adj_mu=per_mu


    elif portfolio_type =='prudent':
        if per_bn+per_mu >per_tot*Decimal(.70):
            x_mu=per_tot*Decimal(.70)-per_mu
            if x_mu <0:
                adj_bn=0
                adj_mu =.70
            else:
                adj_bn=x_mu
                adj_mu=per_mu
        else:
            adj_bn=per_tot*Decimal(.70)-per_mu
            adj_mu=per_mu

    adj_vals.append(adj_bn)
    adj_vals.append(adj_mu)
    print(f"444 - adj_bn:{adj_bn} - adj_mu:{adj_mu}")


    return adj_vals

#///////////////////////////////////jdadev_view_client_list////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers','staffs'])
def jdadev_view_client_list(request):
    client_list = ClientPortfolioModel.objects.all().order_by('-id')
    grp =None

    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
    #GreaGreatprint(f"grp:{grp}")
    context = {'client_list': client_list, 'grp': grp}
    return render(request, 'jdadev/jdadev_client_list.html', context)


#////////////////////////////////jdadev_overall_portfolio_by_client////////////////////////////////
@login_required
def jdadev_overall_portfolio_by_client(request, portfolio_type, client):
    user = client #request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    ovp= ClientPortfolioModel.objects.filter(client=user).first()

    if ovp:
        la  = ovp.liquid_assets
        eqr = ovp.equity_and_rights
        bn  = ovp.bonds
        mu = ovp.mutual_funds
        tot=la+eqr+bn+mu

        per_tot=(tot/tot)
        per_la=(la/tot)
        per_eqr=(eqr/tot)
        per_bn=(bn/tot)
        per_mu=(mu/tot)

        adj_bn=adjusted_per_bn(portfolio_type,per_tot,per_bn,per_mu)[0]
        adj_mu=adjusted_per_bn(portfolio_type,per_tot,per_bn,per_mu)[1]
        #print(f"caller: adj_bn:{adj_bn} - adj_mu:{adj_mu}")
        per_lst=[]
        val_lst=[]
        if portfolio_type == 'overall_portfolio':
            per_lst.append(per_tot*100)
            per_lst.append(per_la*100)
            per_lst.append(per_eqr*100)
            per_lst.append(per_bn*100)
            per_lst.append(per_mu*100)

            val_lst.append(tot)
            val_lst.append(la)
            val_lst.append(eqr)
            val_lst.append(bn)
            val_lst.append(mu)

        elif portfolio_type == 'dynamic':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.10))
            val_lst.append(tot*Decimal(.70))
            val_lst.append(tot*Decimal(adj_bn))
            val_lst.append(tot*Decimal(adj_mu))

            per_lst.append((tot/tot)*100)
            per_lst.append(.10*100)
            per_lst.append(.70*100)
            per_lst.append(adj_bn*100)
            per_lst.append(adj_mu*100)

        elif portfolio_type == 'moderate':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.10))
            val_lst.append(tot*Decimal(.45))
            val_lst.append(tot*Decimal(adj_bn))
            val_lst.append(tot*Decimal(adj_mu))
            per_lst.append((tot/tot)*100)
            per_lst.append(.10*100)
            per_lst.append(.45*100)
            per_lst.append(adj_bn*100)
            per_lst.append(adj_mu*100)

        elif portfolio_type == 'prudent':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.10))
            val_lst.append(tot*Decimal(.20))
            val_lst.append(tot*Decimal(adj_bn))
            val_lst.append(tot*Decimal(adj_mu))
            per_lst.append((tot/tot)*100)
            per_lst.append(.10*100)
            per_lst.append(.20*100)
            per_lst.append(adj_bn*100)
            per_lst.append(adj_mu*100)
    else:
        #print("Invalid portfolio type")
        return redirect('jdadev_home')
    # get username based on user param id
    user = User.objects.get(id=user)
    username = user.username

    context={'client_portfolio': client_portfolio,'client':username,'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst}
    return render(request, 'jdadev/jdadev_overall_portfolio.html', context)

#///////////////////////////////////jdadev_view_client_portfolio////////////////////////////////
# #//////////////////////////////// adjusted_per_bn //////////////////////////////////
# def adjusted_per_bn(portfolio_type, per_tot, per_bn, per_mu):
#     #print(f"per_tot: {per_tot}")
#     #print(f"per_bn: {per_bn} - per_mu: {per_mu}")
#     adj_bn = 0
#     adj_mu = 0
#     adj_result=[]
#     if portfolio_type =='dynamic':
#         if per_bn+per_mu >per_tot*Decimal(.20):
#             print(f"> per_tot*20: {per_tot*Decimal(.20)}")
#             adj_bn=per_tot*Decimal(.20)-per_mu
#             adj_mu=per_mu + adj_bn
#             if adj_bn <0:
#                 adj_bn=0
#                 #print(f"adj_bn: {adj_bn}")
#             #print(f"adj_bn: {adj_bn} - adj_mu: {adj_mu}")
#         else:
#             adj_result.append(per_mu)
#             #pass
#             #print(f"< per_tot*20: {per_tot*.20}")
#     elif portfolio_type =='moderate':
#         per_bn= per_tot*Decimal(.45)-per_mu
#         adj_bn=per_bn
#     elif portfolio_type =='prudent':
#         per_bn= per_tot*Decimal(.70)-per_mu
#         adj_bn=per_bn
#
#         adj_result.append(adj_bn)
#         adj_result.append(adj_mu)
#
#     return adj_result

# #////////////////////////////////jdadev_ovp_dynamic////////////////////////////////
# def jdadev_ovp_dynamic(request):
#     user = request.user
#     client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
#     ovp= ClientPortfolioModel.objects.get()
#
#     la  = ovp.liquid_assets
#     print(f"la:{la}")
#     eqr = ovp.equity_and_rights
#     bn  = ovp.bonds
#     mu = ovp.mutual_funds
#     tot=la+eqr+bn+mu
#     per_tot=(tot/tot)*100
#     per_la=(la/tot)*100
#     per_eqr=(eqr/tot)*100
#     per_bn=(bn/tot)*100
#     per_mu=(mu/tot)*100
#     per_lst=[]
#
#     per_lst.append(per_tot)
#     per_lst.append((tot)*Decimal(.10))
#     per_lst.append((tot)*Decimal(.70))
#     per_lst.append((tot)*Decimal(.06))
#     per_lst.append((tot)*Decimal(.14))
#
#     context={'client_portfolio': client_portfolio,'client':user,'tot':tot, 'ovp':ovp, 'per_lst':per_lst}
#     return render(request, 'jdadev/jdadev_ovp_dynamic.html', context)
#
# #////////////////////////////////jdadev_ovp_moderate////////////////////////////////
# def jdadev_ovp_moderate(request):
#     user = request.user
#     client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
#     ovp= ClientPortfolioModel.objects.get()
#
#     la  = ovp.liquid_assets
#     eqr = ovp.equity_and_rights
#     bn  = ovp.bonds
#     mu = ovp.mutual_funds
#     tot=la+eqr+bn+mu
#     per_tot=(tot/tot)*100
#     per_la=(la/tot)*100
#     per_eqr=(eqr/tot)*100
#     per_bn=(bn/tot)*100
#     per_mu=(mu/tot)*100
#     per_lst=[]
#
#     per_lst.append(per_tot)
#     per_lst.append((tot)*Decimal(.10))
#     per_lst.append((tot)*Decimal(.45))
#     per_lst.append((tot)*Decimal(.45))
#     per_lst.append((tot)*Decimal(.10))
#
#     context={'client_portfolio': client_portfolio,'client':user,'tot':tot, 'ovp':ovp, 'per_lst':per_lst}
#     return render(request, 'jdadev/jdadev_ovp_moderate.html', context)
#
# #////////////////////////////////jdadev_ovp_prudent////////////////////////////////
# def jdadev_ovp_prudent(request):
#     user = request.user
#     client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
#     ovp= ClientPortfolioModel.objects.get()
#
#     la  = ovp.liquid_assets
#     eqr = ovp.equity_and_rights
#     bn  = ovp.bonds
#     mu = ovp.mutual_funds
#     tot=la+eqr+bn+mu
#     per_tot=(tot/tot)*100
#     per_la=(la/tot)*100
#     per_eqr=(eqr/tot)*100
#     per_bn=(bn/tot)*100
#     per_mu=(mu/tot)*100
#
#     print(f"per_tot: {per_tot} per_la: {per_la} per_eqr {per_eqr} per_bn: {per_bn} per_mu: {per_mu}")
#
#     val_lst=[]
#     val_lst.append(tot)
#     val_lst.append(la)
#     val_lst.append(eqr)
#     val_lst.append(bn)
#     val_lst.append(mu)
#
#     print(f"val_lst[0]:{val_lst[0]}, val_lst[1]:{val_lst[1]}, val_lst[2]:{val_lst[2]}")
#
#     per_lst=[]
#     per_lst.append(per_tot)
#     per_lst.append(per_la)
#     per_lst.append(per_eqr)
#     per_lst.append(per_bn)
#     per_lst.append(per_mu)
#
#
#     context={'client_portfolio': client_portfolio,'client':user,'tot':tot, 'ovp':ovp, 'per_lst':per_lst, 'val_lst':val_lst}
#     return render(request, 'jdadev/jdadev_ovp_prudent.html', context)

# def calculate_values(total_val):
#     """
#     Calculate bond_val and mutual_val based on total_val.
#     bond_val cannot exceed 40% of total_val.
#
#     :param total_val: The total value to be distributed.
#     :return: A tuple containing bond_val and mutual_val.
#     """
#     max_bond_val = Decimal(0.4) * total_val
#     bond_val = min(total_val * Decimal(0.4), max_bond_val)
#     mutual_val = total_val - bond_val
#     bond_percent = bond_val/total_val
#     mutual_percent = mutual_val/total_val
#     print(f"Bond percent: {bond_percent}")
#     print(f"Mutual percent: {mutual_percent}")
#     return bond_val, mutual_val


#//////////////////////////////reload_symbols////////////////////////////////
def reload_symbols(request, inst_val):
    #print(inst_val)
    #query the Intitution_types model to get the inst+type name based on the inst_val (id)
    inst_val_str = InstitutionTypeModel.objects.filter(id=inst_val)[0].inst_type

    #print(inst_val_str)
    if inst_val == "":
        symbols = BondModel.objects.all().order_by('symbol')
        #print(symbols)
    else:
        #print(f"QRY: filter(institution_type={inst_val_str})")
        symbols = BondModel.objects.filter(institution_type=inst_val_str).order_by('symbol')
    context ={'symbols':symbols}
    return render(request, 'jdadev/partials/jdadev_symbols.html', context)

#//////////////////////////////reload_bond_names////////////////////////////////
def reload_bond_names(request, sym_val):
    #print("sym_val: ", sym_val)
    if sym_val == "":
        symbols = BondModel.objects.all().order_by('symbol')
        #print(symbols)
    else:
        symbols = BondModel.objects.filter(id=sym_val).order_by('symbol')
        #print(f"symb:{symbols} - OV: {symbols[0].original_value} - CPN: {symbols[0].coupon}")
    context ={'symbols':symbols}
    return render(request, 'jdadev/partials/jdadev_bond_names.html', context)


#//////////////////////////////reload_original_value////////////////////////////////
from decimal import Decimal
def reload_original_value(request, id_int, sym_val):
    #print(f"id_int:{id_int}  sym_val:{sym_val}")
    if sym_val == "":
        symbols = BondModel.objects.all().order_by('symbol')
        #print(f"symbols all:{symbols}")
    else:
        symbols = BondModel.objects.filter(id=sym_val).order_by('symbol')
        #for i in symbols:
        #    print(f"symb:{symbols} - OV: {symbols[i].original_value}")
    #print(f"220:id_int: {id_int} symbols{symbols} - OV: {symbols[0].original_value}")
    ov= str(symbols[0].original_value).replace(',', '.')
    #print(f"ov: {ov}")
    context ={'id_int':id_int,'orig_val':ov}
    return render(request, 'jdadev/partials/jdadev_original_value.html', context)

#//////////////////////////////reload_current_value////////////////////////////////
def reload_current_value(request, id_int, sym_val):
    if sym_val == "":
        symbols = BondModel.objects.all().order_by('symbol')
        #print(f"symbols all:{symbols}")
    else:
        symbols = BondModel.objects.filter(id=sym_val).order_by('symbol')
    #print(f"220:id_int: {id_int} symbols{symbols} - OV: {symbols[0].original_value}")
    curr_v= str(symbols[0].current_value).replace(',', '.')
    print(f"curr_v: {curr_v}")
    context ={'id_int':id_int,'curr_val':curr_v}
    return render(request, 'jdadev/partials/jdadev_bond_current_value.html', context)

#//////////////////////////////reload_bond_coupon////////////////////////////////
def reload_bond_coupon(request, id_int, sym_val):
    #print(f"cpn id_int:{id_int}  sym_val:{sym_val}")
    if sym_val == "":
        symbols = BondModel.objects.all().order_by('symbol')
        #print(f"symbols all:{symbols}")
    else:
        symbols = BondModel.objects.filter(id=sym_val).order_by('symbol')
        #for i in symbols:
        #    print(f"symb:{symbols} - OV: {symbols[i].original_value}")
    #print(f"220:id_int: {id_int} symbols{symbols} - OV: {symbols[0].original_value}")
    cv= str(symbols[0].coupon).replace(',', '.')
    print(f"cv: {cv}")
    context ={'id_int':id_int,'cpn_val':cv}
    return render(request, 'jdadev/partials/jdadev_bond_coupon_value.html', context)
#//////////////////////////////reload_depositaire////////////////////////////////
from decimal import Decimal
def reload_depositaire(request, soc_text):
    #print(f"236: soc_val:{soc_text}")
    #get dps based on the soc_text
    dps=MutualFundModel.objects.filter(sociate_de_gession=soc_text) # dps.depositaire
    depositaires=[]
    for i in dps:
        depositaires.append(i.depositaire)

    if soc_text == "":
        depositaire = DepositaireModel.objects.all().order_by('depositaire')
    else:
        depositaire = DepositaireModel.objects.filter(depositaire__in=depositaires).order_by('depositaire').distinct()
        #print(f"Dep: {depositaire}")
        #for i in depositaire:
        #    print(f"{i.id} - {i}")
        #dep=[]
        #for i in depositaire:
        #    dep.append(i.depositaire)
        #unique_dep = list(set(dep))

    context ={'depositaire':depositaire}
    return render(request, 'jdadev/partials/jdadev_depositaire.html', context)

#//////////////////////////////reload_opcvm////////////////////////////////
from decimal import Decimal
def reload_opcvm(request, soc_text):
    #print(f"261: soc_text:{soc_text}")
    if soc_text == "":
        opcvm = MutualFundModel.objects.all().order_by('opcvm')
        #print(f"depositaire all:{depositaire}")
    else:
        opcvm = MutualFundModel.objects.filter(depositaire=soc_text).order_by('opcvm').distinct()
        # opc=[]
        # for i in opcvm:
        #     opc.append(i.opcvm)
        # unique_dep = list(set(opc))

    context ={'opcvm':opcvm}
    return render(request, 'jdadev/partials/jdadev_opcvm.html', context)



#//////////////////////////////reload_mu_original_value////////////////////////////////
def reload_mu_original_value(request, id_int, soc_text):
    #print(f"305: soc_text:{soc_text}")
    if soc_text == "":
        original_value = MutualFundModel.objects.all()
        #print(f"depositaire all:{depositaire}")
    else:
        original_value = MutualFundModel.objects.filter(opcvm=soc_text)
        orv=[]
        for i in original_value:
            orv.append(i.original_value)
        mu_orig_val= str(orv[0]).replace(',', '.').replace('0000', '00')
        #unique_orv = list(set(orv))
        #print(mu_orig_val)
    #return HttpResponse("999")
    context ={'id_int':id_int,'mu_orig_val':mu_orig_val}
    return render(request, 'jdadev/partials/jdadev_mu_original_value.html', context)

#//////////////////////////////reload_mu_current_value////////////////////////////////
def reload_mu_current_value(request, id_int, soc_text):
    #print(f"323: soc_val:{soc_text}")


    if soc_text == "" or soc_text == 'OPCVM':
        pass

        #current_value = MutualFundModel.objects.all()
        #print(f"depositaire all:{depositaire}")

    else:
        cv = MutualFundModel.objects.get(id=soc_text)
        #orv=[]
        #for i in current_value:
        #    orv.append(i.current_value)
        mu_curr_val= str(cv.current_value).replace(',', '.').replace('0000', '00')
        #unique_orv = list(set(orv))
        #print(mu_curr_val)
        #print(f"340 - reload_mu_current_value: {mu_curr_val}")

    context ={'id_int':id_int,'mu_curr_val':mu_curr_val}
    return render(request, 'jdadev/partials/jdadev_mu_current_value.html', context)

#//////////////////////////////reload_mu_nbr_of_share////////////////////////////////
def reload_mu_nbr_of_share(request, id_int, soc_text):
    #print(f"347: soc_val:{soc_text}")
    if soc_text == "":
        pass
        #mu_nbr_of_share = MutualFundModel.objects.all()

    else:
        ns = MutualFundModel.objects.get(id=soc_text)
        mu_nbr_of_share= str(ns.nbr_of_share).replace(',', '.').replace('0000', '00')

    context ={'id_int':id_int,'mu_nbr_of_share':mu_nbr_of_share}
    return render(request, 'jdadev/partials/jdadev_mu_nbr_of_share.html', context)


#//////////////////////////////reload_mu_total_current_value////////////////////////////////
def reload_mu_total_current_value(request, id_int, soc_text):
    #print(f"362: soc_text:{soc_text}")
    mu_tot_curr_val=soc_text
    context ={'id_int':id_int,'mu_tot_curr_val':mu_tot_curr_val}
    return render(request, 'jdadev/partials/jdadev_mu_total_current_value.html', context)


#/////////////////////////update_equity_and_rights////////////////////////////////
@login_required
def update_equity_and_rights(request, new_value):
    user = request.user  # Get the logged-in user
    #print(f"New_Value: {new_value}")
    # Assuming you want to set the equity_and_rights field to 999 for the logged-in user's portfolio
    # new_value = 999.00

    # Update the equity_and_rights field for the user's portfolio
    updated_rows = ClientPortfolioModel.objects.filter(client=user).update(equity_and_rights=new_value)

    # Debug output to check if the update was successful
    #print(f"Updated {updated_rows} row(s)")

    # Redirect or render a template after updating
    #return redirect('some_success_url')  # Replace 'some_success_url' with your actual success URL or render a template

#/////////////////////////update_bonds////////////////////////////////
@login_required
def update_bonds(request, new_value):
    user = request.user  # Get the logged-in user
    #print(f"New_Value: {new_value}")
    # Assuming you want to set the bonds field to 999 for the logged-in user's portfolio
    # new_value = 999.00

    # Update the bonds field for the user's portfolio
    updated_rows = ClientPortfolioModel.objects.filter(client=user).update(bonds=new_value)

    # Debug output to check if the update was successful
    #print(f"Updated {updated_rows} row(s)")

    # Redirect or render a Stemplate after updating
    #return redirect('some_success_url')  # Replace 'some_success_url' with your actual success URL or render a template

#/////////////////////////update_mututal_fund////////////////////////////////
@login_required
def update_mutual_funds(request, new_value):
    user = request.user  # Get the logged-in user
    #print(f"486 New_Value: {new_value}")
    # Assuming you want to set the mutual_funds field to 999 for the logged-in user's portfolio
    # new_value = 999.00

    # Update the mutual_funds field for the user's portfolio
    updated_rows = ClientPortfolioModel.objects.filter(client=user).update(mutual_funds=new_value)

    # Debug output to check if the update was successful
    #print(f"414 Updated {updated_rows} row(s)")

    # Redirect or render a Stemplate after updating
    #return redirect('some_success_url')  # Replace 'some_success_url' with your actual success URL or render a template


from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def fetch_stock_data(request):
    stock_id = request.GET.get('stock_id')
    stock = get_object_or_404(StockDailyValuesModel, id=stock_id)
    data = {'daily_value': stock.daily_value,}
    #print(f"data: {data}")
    return JsonResponse(data)


# #/////////////////////////update_mutual_funds////////////////////////////////
# @login_required
# def update_mutual_funds(request, new_value):
#     user = request.user  # Get the logged-in user
#     print(f"476 user: {user}")
#     print(f"477 New_Value: {new_value}")
#     # Assuming you want to set the equity_and_rights field to 999 for the logged-in user's portfolio
#     # new_value = 999.00
#
#     # Update the equity_and_rights field for the user's portfolio
#     updated_rows = ClientPortfolioModel.objects.filter(mutual_funds=user).update(mutual_funds=new_value)
#
#     # Debug output to check if the update was successful
#     print(f"485 Updated {updated_rows} row(s)")
#
#     # Redirect or render a Stemplate after updating
#     #return redirect('some_success_url')  # Replace 'some_success_url' with your actual success URL or render a template
#/////////////////////////////// upload_file //////////////////////////////////////////////////////////
def upload_file(request):
    #print("file upload")
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            for index, row in df.iterrows():
                StockDailyValuesModel.objects.create(
                    ticker=row['Ticker'],
                    daily_value=row['Daily Value'],
                    target_value=row['Target Value'],
                )
            return render(request, 'success.html')
    else:
        form = UploadFileForm()
    return render(request, 'jdadev/jdadev_upload_success.html', {'form': form})

#///////////////////////////////////////upload_excel//////////////////////////////////////////////////////
def upload_excel(request):
    #print("765 file upload ")
    if request.method == 'POST':
        try:
            excel_data = request.FILES['excel_file']
        except MultiValueDictKeyError as e:
            #print(f"error creating:{e}")
            return render(request, 'jdadev/upload_error.html', {'error_message': f"No file uploaded. Please select a file: {e}"})

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check file extension
            if not excel_data.name.endswith('.xls') and not excel_data.name.endswith('.xlsx'):
                return render(request, 'jdadev/upload_error.html', {'error_message': "Invalid file type. Please upload a valid Excel file."})

            try:
                df = pd.read_excel(excel_data)
                #print(f"781 Pre: {df}")
                # Preprocess the data
                df['daily_value'] = df['daily_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['target_value'] = df['target_value'].apply(lambda x: None if pd.isna(x) else float(x))

                # Replace NaN with a temporary placeholder
                df['daily_value'] = df['daily_value'].replace(np.nan, '')
                df['target_value'] = df['target_value'].replace(np.nan, '')

                # Replace the temporary placeholder with None
                df['daily_value'] = df['daily_value'].replace('', 0.00)
                df['target_value'] = df['target_value'].replace('', 0.00)
                #print(f"Post: {df}")
                #print(f"{df['daily_value']}-----{df['target_value']}")
            except pd.errors.ParserError as pe:
                #print(f"796 Exception pe: {pe}")
                #messages.error(request, f"Error Loading institution types: {e})")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                #print(f"800 Exception e: {e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            except pd.errors.ParserError:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            # Check if required columns are present
            required_columns = ['ticker', 'daily_value', 'target_value']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                #print("811: missing columns")
                return render(request, 'jdadev/upload_error.html', {'error_message': f"Missing required columns in Excel file: {', '.join(missing_columns)}"})

            try:
                for index, row in df.iterrows():
                    try:
                        ticker = row['ticker']
                        daily_value = row['daily_value']
                        target_value = row['target_value']
                        StockDailyValuesModel.objects.create(ticker=ticker, daily_value=daily_value, target_value=target_value)
                    except Exception as e:
                        #print(f"822 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                #print(f"825 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            return render(request, 'jdadev/upload_success.html')
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})

#///////////////////////////////////////upload_bond_excel//////////////////////////////
def upload_bond_excel(request):
    #print("107 file upload ")
    if request.method == 'POST':
        try:
            excel_data = request.FILES['excel_file']
            #print(excel_data)
        except MultiValueDictKeyError as e:
            #print(f"error creating:{e}")
            return render(request, 'jdadev/upload_error.html', {'error_message': f"No file uploaded. Please select a file: {e}"})

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check file extension
            if not excel_data.name.endswith('.xls') and not excel_data.name.endswith('.xlsx'):
                return render(request, 'jdadev/upload_error.html', {'error_message': "Invalid file type. Please upload a valid Excel file."})

            try:
                df = pd.read_excel(excel_data)
                #print(f"Pre: {df}")
                # Preprocess the data
                df['original_value'] = df['original_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['coupon'] = df['coupon'].apply(lambda x: None if pd.isna(x) else float(x))
                df['current_value'] = df['current_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['nbr_of_shares'] = df['nbr_of_shares'].apply(lambda x: None if pd.isna(x) else float(x))
                df['total_value'] = df['total_value'].apply(lambda x: None if pd.isna(x) else float(x))
                # Replace NaN with a temporary placeholder
                # Replace the temporary placeholder with None
                df['original_value'] = df['original_value'].replace('', 0.00)
                df['coupon'] = df['coupon'].replace('', 0.00)
                df['current_value'] = df['current_value'].replace('', 0.00)
                df['nbr_of_shares'] = df['nbr_of_shares'].replace('', 0)
                df['current_value'] = df['current_value'].replace('', 0.00)

                #print(f"Post: {df}")
                #print(f"{df['original_value']}-----{df['coupon']}-----{df['current_value']}-----{df['nbr_of_shares']}-----{df['total_value']}")
            except pd.errors.ParserError as pe:
               # print(f"409 Exception pe: {pe}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
               # print(f"412 Exception e: {e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            except pd.errors.ParserError:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            # Check if required columns are present
            required_columns = ['symbol', 'bond_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return render(request, 'jdadev/upload_error.html', {'error_message': f"Missing required columns in Excel file: {', '.join(missing_columns)}"})

            try:
                for index, row in df.iterrows():
                    try:
                        symbol = row['symbol']
                        bond_name = row['bond_name']
                        original_value = row['original_value']
                        coupon = row['coupon']
                        current_value = row['current_value']
                        nbr_of_shares = row['nbr_of_shares']
                        total_value = row['total_value']
                        institution_type = row['institution_type']
                        BondModel.objects.create(symbol=symbol,
                                                 bond_name=bond_name,
                                                 original_value=original_value,
                                                 coupon=coupon,
                                                 current_value =current_value,
                                                 nbr_of_shares=nbr_of_shares,
                                                 total_value=total_value,
                                                 institution_type=institution_type)
                    except Exception as e:
                        #print(f"92 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                #print(f"95 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            # Bond ddata upload is successful.  Now insert intitution types data into the InstitutionTypeModel
            insert_distinct_institution_types()
            return render(request, 'jdadev/upload_success.html')
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})


#///////////////////////////////////////upload_mutual_fund_excel//////////////////////////////
def upload_mutual_fund_excel(request):
    #print("463 file upload ")
    if request.method == 'POST':
        try:
            excel_data = request.FILES['excel_file']
            #print(excel_data)
        except MultiValueDictKeyError as e:
            #print(f"error creating:{e}")
            return render(request, 'jdadev/upload_error.html', {'error_message': f"No file uploaded. Please select a file: {e}"})

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check file extension
            if not excel_data.name.endswith('.xls') and not excel_data.name.endswith('.xlsx'):
                return render(request, 'jdadev/upload_error.html', {'error_message': "Invalid file type. Please upload a valid Excel file."})

            try:
                df = pd.read_excel(excel_data)
                #print(f"Pre: {df}")
                # Preprocess the data
                #df['sociate_de_gession'] = df['sociate_de_gession'].apply(lambda x: None if pd.isna(x) else float(x))
                #df['depositaire'] = df['depositaire'].apply(lambda x: None if pd.isna(x) else float(x))
                #df['opcvm'] = df['opcvm'].apply(lambda x: None if pd.isna(x) else float(x))
                df['original_value'] = df['original_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['current_value'] = df['current_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['nbr_of_share'] = df['nbr_of_share'].apply(lambda x: None if pd.isna(x) else int(x))

                # Replace NaN with a temporary placeholder
                # Replace the temporary placeholder with None
                df['original_value'] = df['original_value'].replace('', 0.00)

                df['current_value'] = df['current_value'].replace('', 0.00)
                df['nbr_of_share'] = df['nbr_of_share'].replace('', 0)

                #print("495 Done with data validation")
                #print(f"Post: {df}")
                #print(f"497 {df['sociate_de_gession']}-----{df['depositaire']}-----{df['opcvm']}-----{df['original_value']}-----{df['nbr_of_share']}")
            except pd.errors.ParserError as pe:
                #print(f"499 Exception pe: {pe}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                #print(f"965 Exception e: {e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            except pd.errors.ParserError:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            # Check if required columns are present
            required_columns = ['depositaire', 'opcvm']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return render(request, 'jdadev/upload_error.html', {'error_message': f"Missing required columns in Excel file: {', '.join(missing_columns)}"})
            #print("515 starting inserts")
            try:
                for index, row in df.iterrows():
                    try:
                        #print("trying to..")
                        sociate_de_gession = row['sociate_de_gession']
                        depositaire = row['depositaire']
                        opcvm = row['opcvm']
                        original_value = row['original_value']
                        current_value = row['current_value']
                        nbr_of_share = row['nbr_of_share']

                        MutualFundModel.objects.create(sociate_de_gession=sociate_de_gession,
                                                 depositaire=depositaire,
                                                 opcvm=opcvm,
                                                 original_value=original_value,
                                                 current_value =current_value,
                                                 nbr_of_share=nbr_of_share,)
                    except Exception as e:
                        #print(f"533 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                #print(f"95 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            # Bond ddata upload is successful.  Now insert intitution types data into the InstitutionTypeModel
            #insert_distinct_institution_types()
            return render(request, 'jdadev/upload_success.html')
    else:
        #print("543 UploadFileForm")
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})
#/////////////////////////////////////// insert_distinct_institution_types //////////////////////////////////////
# def insert_distinct_institution_types():
#     # Get distinct institution_type values from BondModel
#     distinct_institution_types = BondModel.objects.values_list('institution_type', flat=True).distinct()
#     try:
#         # Iterate through the distinct institution types
#         for institution_type in distinct_institution_types:
#             # Check if the institution type already exists in InstitutionType model
#             if not InstitutionTypeModel.objects.filter(name=institution_type).exists():
#                 # If it doesn't exist, create a new InstitutionType object and save it
#                 InstitutionTypeModel.objects.create(name=institution_type)
#     except Exception as e:
#         # Handle other types of errors
#         print(f"An error occurred: {e}")
#/////////////////////////////////////////insert_distinct_institution_types///////////////////////////////
def insert_distinct_institution_types(request):
    # Get distinct institution_type values from BondModel
    distinct_institution_types = BondModel.objects.values_list('institution_type', flat=True).distinct()
    try:
        # Iterate through the distinct institution types
        for institution_type in distinct_institution_types:
            # Check if the institution type already exists in InstitutionType model
            if not InstitutionTypeModel.objects.filter(inst_type=institution_type).exists():
                # If it doesn't exist, create a new InstitutionType object and save it
                InstitutionTypeModel.objects.create(inst_type=institution_type)
    except Exception as e:
        # Handle other types of errors
        #print(f"An error occurred: {e}")
        messages.error(request, f"Error Loading institution types: {e})")
        return redirect('jdadev_home')

    inst_type_count = InstitutionTypeModel.objects.count()
    messages.success(request, f"Institution types successfully loaded - {inst_type_count} records loaded")
    return redirect('jdadev_home')

#/////////////////////////////////////////insert_distinct_depositaire///////////////////////////////
def insert_distinct_depositaire(request):
    # Get distinct depositaire values from MutualFundModel
    distinct_depositaires = MutualFundModel.objects.values_list('depositaire', flat=True).distinct().order_by('depositaire')
    try:
        # Iterate through the distinct institution types
        for depositaire in distinct_depositaires:
            # Check if the depositaire already exists in MutualFundModel model
            if not DepositaireModel.objects.filter(depositaire=depositaire).exists():
                # If it doesn't exist, create a new depositaire object and save it
                DepositaireModel.objects.create(depositaire=depositaire)
                #print(f"771 - depositaire: {depositaire}")
    except Exception as e:
        # Handle other types of errors
        #print(f"An error occurred: {e}")
        messages.error(request, f"Error Loading depositaires: {e})")
        return redirect('jdadev_home')

    depositaire_count = DepositaireModel.objects.count()
    messages.success(request, f"Depositaires successfully loaded - {depositaire_count} records loaded")
    return redirect('jdadev_home')

#/////////////////////////////////////////insert_distinct_sociate_de_gession///////////////////////////////
def insert_distinct_sociate_de_gession(request):
    # Get distinct depositaire values from MutualFundModel
    distinct_sociate_de_gessions = MutualFundModel.objects.values_list('sociate_de_gession', flat=True).distinct()
    try:
        # Iterate through the distinct institution types
        for sociate_de_gession in distinct_sociate_de_gessions:
            # Check if the sociate_de_gession already exists in MutualFundModel model
            if not SociateDeGessionModel.objects.filter(sociate_de_gession=sociate_de_gession).exists():
                # If it doesn't exist, create a new sociate_de_gession object and save it
                SociateDeGessionModel.objects.create(sociate_de_gession=sociate_de_gession)
    except Exception as e:
        # Handle other types of errors
        #print(f"An error occurred: {e}")
        messages.error(request, f"Error Loading sociate de gession data: {e})")
        return redirect('jdadev_home')

    sociate_de_gession_count = SociateDeGessionModel.objects.count()
    messages.success(request, f"Sociates de gession successfully loaded - {sociate_de_gession_count} records loaded")
    return redirect('jdadev_home')


#///////////////////////////////////////upload_institution_type_excel//////////////////////////////
def upload_institution_type_excel(request):
    #print("410 file upload ")
    if request.method == 'POST':
        try:
            excel_data = request.FILES['excel_file']
            #print(excel_data)
        except MultiValueDictKeyError as e:
            #print(f"error creating:{e}")
            return render(request, 'jdadev/upload_error.html', {'error_message': f"No file uploaded. Please select a file: {e}"})

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Check file extension
            if not excel_data.name.endswith('.xls') and not excel_data.name.endswith('.xlsx'):
                return render(request, 'jdadev/upload_error.html', {'error_message': "Invalid file type. Please upload a valid Excel file."})

            try:
                df = pd.read_excel(excel_data)
                #print(f"Pre: {df}")
                # Preprocess the data
                df['institution_type_id'] = df['institution_type_id'].apply(lambda x: None if pd.isna(x) else int(x))
                df['institution_type'] = df['institution_type'].apply(lambda x: None if pd.isna(x) else str(x))
                df['institution_type_id'] = df['institution_type_id'].replace('', 999)
                df['institution_type'] = df['institution_type'].replace('', 'NA')


                #print(f"Post: {df}")
                #print(f"{df['institution_type_id']}-----{df['institution_type']}")
            except pd.errors.ParserError as pe:
                #print(f"443 Exception pe: {pe}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                #print(f"446 Exception e: {e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            except pd.errors.ParserError:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            # Check if required columns are present
            required_columns = ['institution_type_id', 'institution_type']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return render(request, 'jdadev/upload_error.html', {'error_message': f"Missing required columns in Excel file: {', '.join(missing_columns)}"})

            try:
                for index, row in df.iterrows():
                    try:
                        institution_type_id = row['institution_type_id']
                        institution_type = row['institution_type_id']

                        BondModel.objects.create(institution_type_id=institution_type_id,institution_type=institution_type)
                    except Exception as e:
                        #print(f"92 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                #print(f"95 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            return render(request, 'jdadev/upload_success.html')
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})
#/////////////////////////////////jdadev_stock_report////////////////////////////////
def jdadev_stock_report(request):
    stocks = StockDailyValuesModel.objects.all()

    context = {'stocks': stocks}
    return render(request, 'jdadev/jdadev_stock_report.html', context)

#/////////////////////////////////jdadev_bond_report////////////////////////////////
def jdadev_bond_report(request):
    bonds = BondModel.objects.all()

    context = {'bonds': bonds}
    return render(request, 'jdadev/jdadev_bond_report.html', context)


#/////////////////////////////////jdadev_mututal_fund_report////////////////////////////////
def jdadev_mutual_fund_report(request):
    mutual_funds = MutualFundModel.objects.all()

    context = {'mutual_funds': mutual_funds}
    return render(request, 'jdadev/jdadev_mutual_fund_report.html', context)


#////////////////////////// jdadev_client_portfolio ///////////////////////
#@login_required
#@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_client_portfolio(request):
    now = datetime.now()
    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            cport = form.save(commit=False)
            cport.client = form.cleaned_data['client']
            cport.publication_date = form.cleaned_data['entry_date']

            cport.save()

            #messages.success(request, f"Successfully saved file '{uploaded_file}'")
            return redirect('Xjdapublicationsapp_listing')
        else:
            messages.error(request, f"Please fill in all required fields before proceeding ")
            #messages.error(request, f"Please fill in all required fields before proceeding {form.errors.as_data()}") {% for key, value in form.errors.items %}

    else:
        form=ClientPortfolioForm()
        #print("200")

    #grp = get_user_grp(request)
    #curr_lang_code = translation.get_language()
    context = {'form':form, 'rpt_date': now}
    return render(request, 'jdadev/jdadev_client_portfolio.html', context)



# myapp/views.py
from django.shortcuts import render, redirect
from .forms import Client_portfolio_form
from .models import Daily_stock, Client_portfolio

def create_or_update_portfolio(request):
    if request.method == 'POST':
        form = Client_portfolio_form(request.POST)
        if form.is_valid():
            stock = form.cleaned_data['stock']
            number_of_stocks = form.cleaned_data['number_of_stocks']
            total_value = stock.current_price * number_of_stocks
            if 'auto_submit' in request.POST:
                # Re-render the form with updated total value
                form = Client_portfolio_form(initial={
                    'client': form.cleaned_data['client'],
                    'stock': stock,
                    'number_of_stocks': number_of_stocks,
                    'total_value': total_value,
                    'auto_submit': True,
                })
            else:
                portfolio = form.save(commit=False)
                portfolio.total_value = total_value
                portfolio.save()
                return redirect('portfolio_success')
    else:
        form = Client_portfolio_form()

    return render(request, 'jdadev/portfolio_form.html', {'form': form})

def portfolio_success(request):
    return render(request, 'jdadev/portfolio_success.html')

def res(request):
    return render(request, 'jdadev/res.html')

def res_htmx(request):
    return HttpResponse("res_htmx")

from django.http import HttpResponse

def get_selected_value(request):
    #print("Request GET parameters:", request.GET)  # Log all GET parameters
    selected_value = request.GET.get('dynamic_select')
    #print(f"Selected value: {selected_value}")  # Debugging line
    return HttpResponse(f'<div id="select-container">{selected_value}</div>')


from .forms import CountryCityForm
from .models import CountryCityModel, City
from django.http import HttpResponse

def index(request):
    print("Loading index")

    country_city = CountryCityModel.objects.all()
    if request.method == 'POST':
        form = CountryCityForm(request.POST)
        if form.is_valid():
            print("country_form is valid")
            print(form.cleaned_data['country'])
            print(form.cleaned_data['city'])

            form = form.save()
        else:
            print(f"Form is not valid: {form.errors}")
    else:
        form = CountryCityForm()


    return render(request, 'jdadev/index.html', {'form': form, 'country_city': country_city})

def load_cities(request):
    print("Loading cities")
    country_id = request.GET.get("country")
    print(f"country_id: {country_id}")
    cities = City.objects.filter(country_id=country_id).order_by('name')
    return render(request, 'jdadev/partials/city_dropdown_list_options.html', {'country_id': country_id ,'cities': cities})





# from .models import City
#
# def country(request):
#     country_form = CountryForm()
#     city_form = CityForm()
#     return render(request, 'jdadev/country.html', {'country_form': country_form, 'city_form': city_form})

# def load_cities(request):
#     country_id = request.GET.get('country')
#     cities = City.objects.filter(country_id=country_id).order_by('name')
#     return render(request, 'jdadev/partials/city_dropdown_list_options.html', {'cities': cities})