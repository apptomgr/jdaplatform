import requests
from django.shortcuts import render, redirect, reverse
from .forms import UploadFileForm
from .models import StockDailyValuesModel, BondModel, MutualFundModel, ClientPortfolioModel,ClientProfileModel, ClientMutualFundsModel, DepositaireModel, SociateDeGessionModel, TransactionFeesModel,SimHeldSecuritiesModel, SimStockPurchasedModel, SimBondPurchasedModel, SimMutualFundPurchasedModel, SimStockSoldModel,SimBondSoldModel, SimMutualFundSoldModel
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
from .forms import ClientPortfolioForm, ClientProfileForm, ClientEquityAndRightsForm, ClientEquityAndRightsFormset, ClientEquityAndRightsFormset_edit, ClientBondsForm, ClientBondsFormset, ClientBondsFormset_edit, ClientMutualFundsFormset, ClientMutualFundsFormset_edit, TransactionFeesForm
from accounts .decorators import allowed_users
from django.db.models import Sum
from django.contrib.auth.models import User
from .helpers import EquityReportRow
from django.utils import timezone
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models import OuterRef, Subquery, IntegerField, DecimalField, FloatField, Value, ExpressionWrapper, F
from django.db.models.functions import Coalesce
from decimal import Decimal, ROUND_DOWN

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
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()

    if request.method == 'POST':
        form = ClientPortfolioForm(request.POST, instance=client_portfolio)
        if form.is_valid():
            client_portfolio = form.save(commit=False)
            client_portfolio.client = user
            client_portfolio.save()
            messages.success(request, "Portfolio info successfully updated")
            return redirect('jdadev_liquid_assets')
        else:
            #print(form.errors)
            messages.warning(request, f"Error: {form.errors}")
    else:
        form = ClientPortfolioForm(instance=client_portfolio)

    context = {'form': form, 'client': user}
    return render(request, 'jdadev/jdadev_liquid_assets.html', context)


#/////////////////////////////////jdadev_equity_and_rights////////////////////
@login_required
def jdadev_equity_and_rights(request):
    user = request.user
    #print(f"110 - user: {user}")
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
                    #print(f"136 - del_eq_item: {del_eq_item} - {del_eq_item[0].stocks}")
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
            #print("153 - Form errors:", form.errors)
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
    #print(f"else: {stock_formset}")
    context = {'form': form, 'client_portfolio': client_portfolio,'client':user, 'stock_formset':stock_formset}
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
                    #print(f"136 - del_bn_item: {del_bn_item} - {del_bn_item[0].bond_name}")
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
#from django.db import connection
@login_required
def jdadev_overall_portfolio(request, portfolio_type):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"client:{user}")
    ovp= ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"ovp:{ovp}")
    client_profiles = None #ClientProfileModel.objects.filter(client=user) # get existing profiles
    custom_profile = None#ClientProfileModel.objects.filter(client=user, profile_type='custom')
    print(f"321 client_profiles:{client_profiles}")
    #Check for the latest saved client profile
    lcp = None
    if ClientProfileModel.objects.count() >0:
        lcp = ClientProfileModel.objects.latest('id')
        print(f"324:lcp for client {lcp.client} - Profile is {lcp.profile_type}")
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
            print(f"345: portfolio_type - {portfolio_type}")
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
            #print(f"357:lcp for client {lcp.client} - {lcp.profile_type} ")

        elif portfolio_type == 'dynamic':
            print("368 - set dynamic")
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
            #save the profiles in ClientProfileModel if they don't exist'
            # First check if it exists
            #dynamic_pro=ClientProfileModel.objects.filter(client=user, profile_type='dynamic').exists()
            #print(f"375 dynamic_pro exists: {dynamic_pro}")
            #if not dynamic_pro:
            #create new dynamic profile for the customer
            ClientProfileModel.objects.create(client=user, liquid_assets=per_lst[1], equity_and_rights=per_lst[2], bonds=per_lst[3], mutual_funds=per_lst[4], profile_type=portfolio_type)
            #print(f"378:lcp for client {lcp.client} - Profile is {lcp.profile_type}")
            #pull selected client profile from the database
            #client_profiles=ClientProfileModel.objects.filter(profile_type='dynamic')
            #print(f"379:{client_profiles.profile_type}")

        elif portfolio_type == 'moderate':
            #print("385 - set moderate")
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
            #save the profiles in ClientProfileModel if they don't exist'
            # First check if it exists
            #moderate_pro=ClientProfileModel.objects.filter(client=user, profile_type='moderate').exists()
            #print(f"396 moderate_pro exists: {moderate_pro}")
            #if not moderate_pro:
            ClientProfileModel.objects.create(client=user, liquid_assets=per_lst[1], equity_and_rights=per_lst[2], bonds=per_lst[3], mutual_funds=per_lst[4], profile_type=portfolio_type)
            #pull selected client profile from the database
            #client_profiles=ClientProfileModel.objects.filter(profile_type='moderate')
            #print(f"401:{client_profiles}")
        elif portfolio_type == 'prudent':
            #print("406 - set prudent")
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.05))
            val_lst.append(tot*Decimal(.20))
            val_lst.append(tot*Decimal(.55))
            per_lst.append((tot/tot)*100)
            per_lst.append(.05*100)
            per_lst.append(.20*100)
            per_lst.append(.55*100)
            per_lst.append(.20*100)
            #save the profiles in ClientProfileModel if they don't exist'
            # First check if it exists
            #prudent_pro=ClientProfileModel.objects.filter(client=user, profile_type='prudent').exists()
            #if not prudent_pro:
            ClientProfileModel.objects.create(client=user, liquid_assets=per_lst[1], equity_and_rights=per_lst[2], bonds=per_lst[3], mutual_funds=per_lst[4], profile_type=portfolio_type)
            #pull selected client profile from the database
            #client_profiles=ClientProfileModel.objects.filter(profile_type='prudent')
            #print(f"414:{client_profiles}")
            #print(f"Dynamic_profile:{ClientProfileModel.objects.all()}")
            #return redirect('jdadev_recommendation')
        elif portfolio_type == 'custom':
            #pull selected client profile from the database
            #print("429 - set custom")
            client_profiles=ClientProfileModel.objects.filter(profile_type='custom').order_by('-entry_date').first()
            #print(f"431 - client_profiles: {client_profiles}")
            #last_custom_profile = ClientProfileModel.objects.filter(client=client_portfolio).latest()
            #return redirect('jdadev_overall_portfolio', portfolio_type='custom')
            #per_la = client_profiles.liquid_assets
            per_lst.append(per_tot*100)
            per_lst.append(client_profiles.liquid_assets)
            per_lst.append(client_profiles.equity_and_rights)
            per_lst.append(client_profiles.bonds)
            per_lst.append(client_profiles.mutual_funds)

            val_lst.append(tot)
            val_lst.append(la)
            val_lst.append(eqr)
            val_lst.append(bn)
            val_lst.append(mu)


        elif portfolio_type == 'custom_set':
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
            if request.method == 'POST':
                custom_form = ClientProfileForm(request.POST, instance=client_portfolio)

                if custom_form.is_valid():
                    la = custom_form.cleaned_data['liquid_assets']
                    eq = custom_form.cleaned_data['equity_and_rights']
                    bn = custom_form.cleaned_data['bonds']
                    mu = custom_form.cleaned_data['mutual_funds']

                    # Delete the user's current custom profile if it exists
                    ClientProfileModel.objects.filter(client=user, profile_type="custom").delete()

                    # Create and save the new entry
                    client_portfolio = ClientProfileModel(client=user,liquid_assets=la,equity_and_rights=eq,bonds=bn,mutual_funds=mu,profile_type="custom")
                    try:
                        client_portfolio.full_clean()
                        client_portfolio.save()
                        return redirect('jdadev_overall_portfolio', portfolio_type='custom')

                    except ValidationError as e:
                        # Add field-specific and non-field errors to the form
                        for field, errors in e.message_dict.items():
                            for error in errors:
                                if field == '__all__':
                                    custom_form.add_error(None, error)  # non-field error
                                else:
                                    custom_form.add_error(field, error)

                        #print(f"error: {e}")
                        #custom_form.add_error(None, f"Validation Exception: {e}")
                        #custom_form.add_error(None, f"Validation Exception: The sum of all asset percentages must be exactly 100%.")



                        #return redirect('jdadev_overall_portfolio', portfolio_type='custom_set')

                    context={'client_portfolio': client_portfolio,'client':user,'client_profiles':client_profiles, 'custom_profile':custom_profile,'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst, 'custom_form': custom_form}
                    return render(request, 'jdadev/jdadev_overall_portfolio.html', context) #{'custom_form': custom_form, 'val_lst': [0,0,0,0,0],  # or actual values 'per_lst': [0,0,0,0],'ovp': None,})
            else:
                custom_form = ClientProfileForm()
    else:
        #print("492- else")
        return redirect('jdadev_home')

    #lcp = ClientProfileModel.objects.latest('id')
    if ClientProfileModel.objects.count() >0:
        lcp = ClientProfileModel.objects.latest('id')
    #print(f"324:lcp for client {lcp.client} - Profile is {lcp.profile_type}")
    #print(f"504 lcp:{lcp} type: {lcp.profile_type}")
    #print(f"505 client_profiles:{client_profiles}")
    context={'client_portfolio': client_portfolio,'client':user,'client_profiles':client_profiles, 'custom_profile':custom_profile,'lcp':lcp, 'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst, 'custom_form': custom_form}
    return render(request, 'jdadev/jdadev_overall_portfolio.html', context)

#////////////////////////////////////////jdadev_set_custom_profile////////////////////////////////////////
@login_required
def jdadev_set_custom_profile(request):
    user = request.user

    try:
        existing_profile = ClientProfileModel.objects.get(client=user, profile_type="custom")
    except ClientProfileModel.DoesNotExist:
        existing_profile = None

    if request.method == 'POST':
        custom_form = ClientProfileForm(request.POST)

        if custom_form.is_valid():
            la = custom_form.cleaned_data['liquid_assets']
            eq = custom_form.cleaned_data['equity_and_rights']
            bn = custom_form.cleaned_data['bonds']
            mu = custom_form.cleaned_data['mutual_funds']

            # Delete any existing custom profile
            ClientProfileModel.objects.filter(client=user, profile_type="custom").delete()

            # Create a new profile instance
            new_profile = ClientProfileModel(
                client=user,
                liquid_assets=la,
                equity_and_rights=eq,
                bonds=bn,
                mutual_funds=mu,
                profile_type="custom"
            )

            try:
                new_profile.full_clean()  # Will trigger your `clean()` logic
                new_profile.save()
                return redirect('jdadev_overall_portfolio', portfolio_type='custom')

            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        custom_form.add_error(None if field == '__all__' else field, error)

    else:
        custom_form = ClientProfileForm(instance=existing_profile)

    return render(request, 'jdadev/jdadev_overall_portfolio.html', {'custom_form': custom_form})
#///////////////////////////////////////jdadev_recommendation/////////////////////////////////////////////
@login_required
def jdadev_recommendation(request):
    user = request.user
    instance = TransactionFeesModel.objects.filter(client=user).last()
    if instance:
        form = TransactionFeesForm(instance=instance)

    else:
        form = TransactionFeesForm()
    spinner = True
    context = {'form': form, 'spinner':spinner}
    return render(request, 'jdadev/jdadev_recommendation.html', context)

#//////////////////////////////////////save_transaction_fees////////////////////
@login_required
def jdadev_save_transaction_fees(request):
    user = request.user
    print(f"584: user - {user} user.id - {user.id}")
    #client_eq_portfolio=ClientEquityAndRightsModel.objects.filter(client=user)
    portfolio = ClientEquityAndRightsModel.objects.filter(client=request.user)
    latest_fees = TransactionFeesModel.objects.filter(client=request.user).order_by('-entry_date').first()
    print(f"588 - latest_fees: {latest_fees}")

    if request.method == 'POST':
        instance = TransactionFeesModel.objects.filter(client=user).last()
        form = TransactionFeesForm(request.POST, instance=instance)

        if form.is_valid():
            transaction_fees = form.save(commit=False)
            transaction_fees.client = user
            transaction_fees.save()
            #print("SAVED")
            #gain_or_loss =client_eq_portfolio.daily_value -
            #report_rows = [EquityReportRow(obj) for obj in client_eq_portfolio]
            if not latest_fees:
                latest_fees = TransactionFeesModel.objects.filter(client=request.user).order_by('-entry_date').first()
                #return render(request, "jdadev/error.html", {"message": "No transaction fees available for this client."})

            report_rows = [EquityReportRow(eq, latest_fees) for eq in portfolio]
            #print(f"600 - report_rows: {report_rows}")
            save_sim_held_securities(request, report_rows)
            spinner = False;
            context= {'instance': transaction_fees, 'report_rows':report_rows, 'spinner':spinner, 'selected_nav':'text-info'}
            return render(request,"jdadev/partials/jdadev_transaction_fees_form_readonly.html", context)
        else:
            print("611 - 🚨 Form is invalid:")
            print(f"612: - { form.errors}")
            return render(request,"jdadev/partials/jdadev_transaction_fees_form.html", {"form": form})

    else:
        instance = TransactionFeesModel.objects.filter(client=user).last()
        form = TransactionFeesForm(instance=instance)

    return render(request, 'jdadev/partials/jdadev_transaction_fees_form.html', {'form': form})

#//////////////////////////////////save_sim_held_securities/////////////////////////////////
def save_sim_held_securities(request, report_rows):
    user = request.user
    # Delete previous entries for this user
    SimHeldSecuritiesModel.objects.filter(client=user).delete()

    # Bulk create entries from report rows
    instances = []
    for row in report_rows:
        instance = SimHeldSecuritiesModel(
            client=user,
            stock=row.stock,
            nbr_of_stocks=row.nbr_of_stocks,
            avg_weighted_cost=row.avg_weighted_cost,
            mkt_price=row.market_price,
            gain_or_loss=row.gain_or_loss,
            target_price=row.target_price,
            potential_gain_or_loss=row.potential_gain_or_loss,
            selling_price=row.selling_price,
            decision=row.decision,
            sale_amount=row.sale_amount
        )
        instances.append(instance)

    SimHeldSecuritiesModel.objects.bulk_create(instances)

#//////////////////////////////////jdadev_simulation_home/////////////////////////////////
@login_required
def jdadev_simulation_home(request):
    sim=SimHeldSecuritiesModel.objects.filter(client=request.user).filter(decision='KEEP')
    context={'sim':sim, 'selected_nav':'text-info', 'client': request.user}
    return render(request, 'jdadev/jdadev_simulation_home.html', context)

#//////////////////////////////////jdadev_simulation_portfolio_after_sale/////////////////////////////////
@login_required
def jdadev_simulation_portfolio_after_sale(request):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"client:{user}")
    ovp= ClientPortfolioModel.objects.filter(client=user).first() #ovp= Overall portfolio
    #print(f"before la: {ovp.liquid_assets}")
    #print(f"before eq: {ovp.equity_and_rights}")
    client_profiles = ClientProfileModel.objects.filter(client=user) # get existing profiles
    sim = SimHeldSecuritiesModel.objects.filter(client=user).filter(decision='SELL').aggregate(total_amount_sold=Sum('sale_amount'))
    total_amount_sold = sim['total_amount_sold'] or 0
    #print(f"total_amount_sold: {total_amount_sold}")
    ovp.liquid_assets = ovp.liquid_assets + abs(total_amount_sold)
    ovp.equity_and_rights = ovp.equity_and_rights - abs(total_amount_sold)
    #print(f"total_amount: {abs(total_amount_sold)}")
    #print(f"After la: {ovp.liquid_assets}")
    #custom_profile = ClientProfileModel.objects.filter(client=user, profile_type='custom')
    #now get the sale amounts and add them to the liquid asset
    #remove the equity sold values from the equity and rights client portfolio

    if ovp:
        la  = ovp.liquid_assets
        #print(f"la: {la}")
        eqr = ovp.equity_and_rights
        #print(f"eqr: {eqr}")
        bn  = ovp.bonds
        mu = ovp.mutual_funds
        tot=la+eqr+bn+mu

        per_tot=(tot/tot)
        per_la=(la/tot)
        per_eqr=(eqr/tot)
        per_bn=(bn/tot)
        per_mu=(mu/tot)

        per_lst=[]
        val_lst=[]

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


    context={'client_portfolio': client_portfolio,'client':user,'client_profiles':client_profiles, 'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst}
    return render(request, 'jdadev/jdadev_simulation_portfolio_after_sale.html', context)

#//////////////////////////////////jdadev_simulation_target_portfolio/////////////////////////////////
@login_required
def jdadev_simulation_target_portfolio(request):
    user = request.user
    client_portfolio = ClientPortfolioModel.objects.filter(client=user).first()
    #print(f"client:{user}")
    ovp= ClientPortfolioModel.objects.filter(client=user).first() #ovp= Overall portfolio
    #orig_eqr = ovp.equity_and_rights
    #print(f"714 orig_eqr: {orig_eqr}")
    client_profiles = ClientProfileModel.objects.filter(client=user) # get existing profiles
    sim = SimHeldSecuritiesModel.objects.filter(decision='SELL').aggregate(total_amount_sold=Sum('sale_amount'))
    total_amount_sold = sim['total_amount_sold'] or 0
    ovp.liquid_assets = ovp.liquid_assets + abs(total_amount_sold)
    #print(f"before eq: {ovp.equity_and_rights}")
    ovp.equity_and_rights = ovp.equity_and_rights - abs(total_amount_sold)

    # After Sale eqr
    lq_after_sale = ovp.liquid_assets
    eqr_after_sale = ovp.equity_and_rights
    bn_after_sale = ovp.bonds
    mu_after_sale = ovp.mutual_funds
    #print(f"after after_sale_eqr: {eqr_after_sale}")
    #print(f"after after_sale_bn: {bn_after_sale}")
    #print(f"after after_sale_mu: {mu_after_sale}")
    #store port after sale info to pass as params

    sec_port_aft_sale =[]
    sec_port_aft_sale.append(float(lq_after_sale))
    sec_port_aft_sale.append(float(eqr_after_sale))
    sec_port_aft_sale.append(float(bn_after_sale))
    sec_port_aft_sale.append(float(mu_after_sale))
    #print(f"734- sec_port_aft_sale:{sec_port_aft_sale}")
    #eqr_tgt_port = 0
    #print(f"total_amount: {abs(total_amount_sold)}")
    #print(f"After la: {ovp.liquid_assets}")
    #custom_profile = ClientProfileModel.objects.filter(client=user, profile_type='custom')
    #now get the sale amounts and add them to the liquid asset
    #remove the equity sold values from the equity and rights client portfolio

    #workflow_next_step
    workflow_next_step = ""
    workflow_bs = [] #0 #[0,1,2] -> [Do nothing, B, S]

    #init the sec_tgt_ports (eq, bn and mu) to pass as a param to the next worklfow - Stock Sale
    sec_tgt_ports =[]
    # get client lcp (latest client profile) saved
    lcp = None
    if ClientProfileModel.objects.count() >0:
        lcp = ClientProfileModel.objects.latest('id')

    #print(f"759 - lcp: {lcp.profile_type}")

    if ovp:
        la  = ovp.liquid_assets
        eqr = ovp.equity_and_rights
        #print(f"eqr: {eqr}")
        bn  = ovp.bonds
        mu = ovp.mutual_funds
        tot=la+eqr+bn+mu
        #print(f"tot: {tot}")

        per_lst=[]
        val_lst=[]
        if lcp.profile_type == 'dynamic':
            val_lst.append(tot)
            val_lst.append(tot*Decimal(.05))
            val_lst.append(tot*Decimal(.55))
            val_lst.append(tot*Decimal(.20))
            val_lst.append(tot*Decimal(.20))
            per_lst.append((tot/tot)*100)
            per_lst.append(.05*100)
            per_lst.append(.55*100)
            per_lst.append(.20*100)
            per_lst.append(.20*100)
            eqr_tgt_port = val_lst[2]
            bn_tgt_port = val_lst[3]
            mu_tgt_port = val_lst[4]

            sec_tgt_ports.append(float(eqr_tgt_port))
            sec_tgt_ports.append(float(bn_tgt_port))
            sec_tgt_ports.append(float(mu_tgt_port))

        elif lcp.profile_type == 'moderate':
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

            eqr_tgt_port = val_lst[2]
            #print(f"805 - eqr_tgt_port: {eqr_tgt_port}")
            bn_tgt_port = val_lst[3]
            mu_tgt_port = val_lst[4]
            sec_tgt_ports.append(float(eqr_tgt_port))
            sec_tgt_ports.append(float(bn_tgt_port))
            sec_tgt_ports.append(float(mu_tgt_port))

        elif lcp.profile_type == 'prudent':
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

            eqr_tgt_port = val_lst[2]
            bn_tgt_port = val_lst[3]
            mu_tgt_port = val_lst[4]
            sec_tgt_ports.append(float(eqr_tgt_port))
            sec_tgt_ports.append(float(bn_tgt_port))
            sec_tgt_ports.append(float(mu_tgt_port))

    #Check decision point
    ### 1. Determine if stock B or S
    if eqr_after_sale < eqr_tgt_port:
            print(f"813 true: {eqr_after_sale:,.2f} is less than {eqr_tgt_port:,.2f} redirect to bond sale")
            workflow_bs = "Stock Sale" # Do nothing
            #workflow_next_step = "Stock Sale"
            #redirect to sell stocks buy
            #ßmessages.warning(request, f"{eqr_after_sale:,.2f} is less than {eqr_tgt_port:,.2f}. You don't have enough stocks to sell. Redirecting next workflow - Bond sale")

    else:
        ### Since eq after sale is > eq trgt the client can sell stocks
        #print(f"839 - eqr_after_sale:{eqr_after_sale:,.2f} eqr_tgt_port: {eqr_tgt_port:,.2f}")
        workflow_bs = "Bond Sale"

        #print(f"840 sec_tgt_ports: {sec_tgt_ports}")

    #Create session to store sec_tgt_ports, sec_port_aft_sale
    # Delete the session keys first if they exist
    if 'sec_tgt_ports' in request.session:
        del request.session['sec_tgt_ports']
    if 'sec_port_aft_sale' in request.session:
        del request.session['sec_port_aft_sale']

    # Now create the session keys with new values
    request.session['sec_tgt_ports'] = sec_tgt_ports
    request.session['sec_port_aft_sale'] = sec_port_aft_sale

    formatted_ports = [f"{val:,.2f}" for val in sec_tgt_ports]
    #print(f"856 - {formatted_ports}")
    formatted_ports = [f"{val:,.2f}" for val in sec_port_aft_sale]
    #print(f"858 - {formatted_ports}")


    # Mark session as modified (optional but safe)
    request.session.modified = True

    context={'client_portfolio': client_portfolio,'client':user,'client_profiles':client_profiles, 'tot':tot, 'ovp':ovp, 'val_lst': val_lst, 'per_lst':per_lst, "sec_tgt_ports":sec_tgt_ports, 'sec_port_aft_sale':sec_port_aft_sale, "workflow_bs":workflow_bs, "workflow_next_step":workflow_next_step}
    return render(request, 'jdadev/jdadev_simulation_target_portfolio.html', context)

#//////////////////////////////////jdadev_simulation_stock_sale/////////////////////////////////
import ast
@login_required
def jdadev_simulation_stock_sale(request):#, workflow_bs, sec_tgt_ports, sec_port_aft_sale ):
    user = request.user
    ### Get the sess_sec_tgt_ports and sess_sec_port_aft_sale
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])

    ### Get the portfolio_balance
    #print(f"876: sec_tgt_ports {sec_tgt_ports}")
    #print(f"877: sec_port_aft_sale {sec_port_aft_sale}")
    portfolio_balance = float(sec_port_aft_sale[1] - sec_tgt_ports[0])
    #print(f"879 - bn_portfolio_balance: {portfolio_balance:,.2f} -sec_port_aft_sale_values[2]: {sec_port_aft_sale[1]:,.2f} minus sec_tgt_ports[1]: {sec_tgt_ports[0]:,.2f}")
    # #Convert str sec_tgt_ports to a list
    # #sec_tgt_ports_values =None
    # if sec_tgt_ports:
    #     try:
    #         sec_tgt_ports_values = ast.literal_eval(sec_tgt_ports)
    #     except (ValueError, SyntaxError):
    #         sec_tgt_ports_values = []
    # else:
    #     sec_tgt_ports_values = []
    #
    # #Convert str port_aft_sale to a list
    # if sec_port_aft_sale:
    #     #print("856: True")
    #     try:
    #         sec_port_aft_sale_values = ast.literal_eval(sec_port_aft_sale)
    #         #print(f"858:sec_port_aft_sale_values: {sec_port_aft_sale_values}")
    #     except (ValueError, SyntaxError):
    #         print(f"861 error {ValueError}")
    #         sec_port_aft_sale_values = []
    # else:
    #     print(f"897 - false")
    #     sec_port_aft_sale_values = []

    client_eqr_portfolio = None
    stock_sold_rpt= None

    ### Determine if you can sell stocks. If float(sec_port_aft_sale_values[1] > sec_tgt_ports_values[0])
    # Now check if the client's bn_tot_curr_val is > or < than the sec_tgt_ports_values[2] (2 for bn) value
    if float(sec_port_aft_sale[1] > sec_tgt_ports[0]):
        print(f"true: {sec_port_aft_sale[1]:,.2f} is less than {sec_tgt_ports[0]:,.2f} proceed with stock sale")
        workflow_bs = "Stock Sale"

        ### get sim stocks to exclude from ClientEquityAndRightsModel since it was initially sold
        sim_stocks = SimHeldSecuritiesModel.objects.filter(client=user, decision='SELL').values_list('stock', flat=True)
        client_eqr_portfolio = ClientEquityAndRightsModel.objects.filter(client=user).exclude(stocks__ticker__in=sim_stocks) #.annotate(gp_calc=ExpressionWrapper((F('stocks__target_value') / F('daily_value')) - 1, output_field=FloatField())).order_by('-gp_calc')
        ### Generate the stock sold report
        stock_sold_rpt = generate_stock_sold_report(request, portfolio_balance, client_eqr_portfolio)
        ### Set the workflow_bs to "Stock Sell" send a message to the user
        workflow_bs = "Stock Sale"

        messages.success(request, f"Your after sale equity portfolio {sec_port_aft_sale[1]:,.2f} is greater than your target equity portfolio, {sec_tgt_ports[0]:,.2f}. Stock Sale is required.")
    else:
        messages.warning(request, f"Your after sale equity portfolio {sec_port_aft_sale[1]:,.2f} is less than your target equity portfolio, {sec_tgt_ports[0]:,.2f}. Stock Sale is not required. Redirecting you to the next workflow - Bond Sell")
        workflow_bs = "Bond Sale"
        #print("928 FALSE")


    context ={'client_eqr_portfolio':client_eqr_portfolio, 'portfolio_balance': portfolio_balance, 'stock_sold_rpt':stock_sold_rpt,'workflow_bs':workflow_bs}#, "sec_tgt_ports":sec_tgt_ports, "sec_port_aft_sale":sec_port_aft_sale}
    return render(request, 'jdadev/jdadev_simulation_stock_sale.html', context)


#////////////////////////////////////////generate_stock_sold_report ////////////////////////////////////
def generate_stock_sold_report(request, portfolio_balance, client_eqr_portfolio):
    """
    Generate a prorata sale report for a client's portfolio,
    capped at 50% per stock and limited by portfolio_balance.
    """
    #sort by gp
    #client_eqr_portfolio = client_eqr_portfolio.annotate(gp_calc=ExpressionWrapper((F('stocks__target_value') / F('daily_value')) - 1, output_field=FloatField())).order_by('gp_calc')

    stocks = client_eqr_portfolio

   # Sort by growth potential descending
    #stocks = sorted(stocks, key=lambda s: s.gp or Decimal("-999"), reverse=True)

    balance_left = Decimal(portfolio_balance)

    report = []

    for stock in stocks:
        if balance_left <= 0:
            break

        # basic stock info
        total_shares = stock.nbr_of_stocks or 0
        market_price = stock.daily_value or Decimal("0")

        if total_shares == 0 or market_price == 0:
            continue

        # max shares we can sell (50% cap)
        max_to_sell = total_shares // 2

        # max proceeds if we sold 50%
        max_proceeds = Decimal(max_to_sell) * market_price

        # check against portfolio balance left
        if max_proceeds <= balance_left:
            # sell full 50% of this stock
            shares_to_sell = max_to_sell
            proceeds = max_proceeds
        else:
            # sell only as much as balance allows
            shares_to_sell = (balance_left / market_price).to_integral_value(rounding=ROUND_DOWN)
            proceeds = shares_to_sell * market_price

        # Deduct from balance
        balance_left -= proceeds

        # Add to report
        report.append({
            "ticker": stock.stocks.symbol if hasattr(stock.stocks, "symbol") else str(stock.stocks),
            "number_of_share": total_shares,
            "daily_value": float(market_price),
            "target_value": float(stock.stocks.target_value),
            "gp": float(stock.gp),
            "total_current_value": float(stock.total_current_value),
            "nbr_of_sell_share": int(shares_to_sell),
            "percentage_sold": "50%" if shares_to_sell == max_to_sell else f"{(shares_to_sell / total_shares * 100):.2f}%",
            "nbr_shares_sold": int(shares_to_sell),
            "net_sell_price": float(market_price),
            "sold_amount": float(proceeds),
        })

    ### store report in session
    request.session['stock_sold'] = report
    ### delete model data
    SimStockSoldModel.objects.all().delete()

    return report

#////////////////////////////////////jdadev_simulation_confirm_stock_sold/////////
from django.views.decorators.http import require_POST
@require_POST
@login_required
def jdadev_simulation_confirm_stock_sold(request):
    stock_sold = request.session.get('stock_sold', [])

    if not stock_sold:
        # Handle empty session (user didn't select stocks yet)
        messages.error(request, "No stock data found in session.")
        return redirect('some-page')

    for stock in stock_sold:
        ### Format the percentage_sold in case it comes as a string
        percentage_str = stock['percentage_sold']  # "50%"
        if isinstance(percentage_str, str) and percentage_str.endswith('%'):
            percentage_value = Decimal(percentage_str.replace('%', '').strip())
        else:
            percentage_value = Decimal(percentage_str)

        SimStockSoldModel.objects.create(
             client=request.user,
             ticker=stock['ticker'],
             number_of_share=stock['number_of_share'],
             daily_value=stock['daily_value'],
             target_value=stock['target_value'],
             gp=stock['gp'],
             total_current_value=stock['total_current_value'],
             percentage_sold=percentage_value, #stock['percentage_sold'],
             nbr_shares_sold=stock['nbr_shares_sold'],
             net_sell_price=stock['net_sell_price'],
             sold_amount=stock['sold_amount'],
         )
    messages.success(request, f"Successfully  Sold stocks")  # show is current stock and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    ### Clear session after saving
    del request.session['stock_sold']
    ### delete model data
    #SimStockSoldModel.objects.all().delete()
    ### HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = reverse('jdadev_simulation_stock_sold')
    return response

#//////////////////////////////////jdadev_simulation_simulation_stock_sold/////////////////////////////
@login_required
def jdadev_simulation_stock_sold(request):
    sold_stocks = SimStockSoldModel.objects.filter(client=request.user).order_by('-id') #[:10]
    context={'sold_stocks': sold_stocks}
    return render(request, 'jdadev/jdadev_simulation_stock_sold.html', context)

#//////////////////////////////////jdadev_simulation_bond_sale/////////////////////////////////
@login_required
def jdadev_simulation_bond_sale(request):
    ### Get the sess_sec_tgt_ports and sess_sec_port_aft_sale
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])

    ### Get the bn_portfolio_balance
    #print(f"1060: sec_tgt_ports {sec_tgt_ports}")
    #print(f"1061: sec_port_aft_sale {sec_port_aft_sale}")
    bn_portfolio_balance = float(sec_port_aft_sale[2] - sec_tgt_ports[1])
    #print(f"1063 -bn_portfolio_balance: {bn_portfolio_balance:,.2f} -sec_port_aft_sale_values[2]: {sec_port_aft_sale[2]:,.2f} minus sec_tgt_ports[1]: {sec_tgt_ports[1]:,.2f}")
    ### Determine if you can sell stocks. If float(sec_port_aft_sale_values[1] > sec_tgt_ports_values[0])
    # Now check if the client's bn_tot_curr_val is > or < than the sec_tgt_ports_values[2] (2 for bn) value
    client_bn_portfolio = None
    bond_sold_rpt = None
    workflow_bs= None
    if float(sec_port_aft_sale[2] > sec_tgt_ports[1]):
        print(f"true: {sec_port_aft_sale[2]:,.2f} is less than {sec_tgt_ports[1]:,.2f} proceed with stock sale")

        client_bn_portfolio = ClientBondsModel.objects.filter(client=request.user)
        ### Generate the bond sold report
        bond_sold_rpt = generate_bond_sold_report(request, bn_portfolio_balance, client_bn_portfolio)
        ### Set the workflow_bs to "Stock Sell" send a message to the user
        workflow_bs = "Bond Sale"

        messages.success(request, f"Your after sale bond portfolio {sec_port_aft_sale[2]:,.2f} is greater than your target bond portfolio, {sec_tgt_ports[1]:,.2f}. Bond Sale is required.")
    else:
        messages.warning(request, f"Your after sale equity portfolio {sec_port_aft_sale[2]:,.2f} is less than your target bond portfolio, {sec_tgt_ports[1]:,.2f}. Bond Sale is not required. Redirecting you to the next workflow - Mutual Fund Sell")
        workflow_bs = "Mutual Fund Sale"
        #print("928 FALSE")

    #print(f"1082 bond_sold_rpt - {bond_sold_rpt}")
    context ={'client_bn_portfolio':client_bn_portfolio, "bn_portfolio_balance": bn_portfolio_balance, 'bond_sold_rpt':bond_sold_rpt,'workflow_bs':workflow_bs}#, "sec_tgt_ports":sec_tgt_ports, "sec_port_aft_sale":sec_port_aft_sale}

    return render(request, 'jdadev/jdadev_simulation_bond_sale.html', context)

#////////////////////////////////////////generate_bond_sold_report ////////////////////////////////////
def generate_bond_sold_report(request, portfolio_balance, client_bn_portfolio):
    """
    Generate a prorata sale report for a client's portfolio,
    capped at 50% per stock and limited by portfolio_balance.
    """
    #sort by gp
    #client_eqr_portfolio = client_eqr_portfolio.annotate(gp_calc=ExpressionWrapper((F('bonds__target_value') / F('daily_value')) - 1, output_field=FloatField())).order_by('gp_calc')

    bonds = client_bn_portfolio

    # Sort by growth potential descending
    #stocks = sorted(stocks, key=lambda s: s.gp or Decimal("-999"), reverse=True)

    balance_left = Decimal(portfolio_balance)

    report = []

    for bond in bonds:
        if balance_left <= 0:
            break
        # basic bond info
        total_shares = bond.nbr_of_shares or 0
        market_price = bond.current_value or Decimal("0")

        if total_shares == 0 or market_price == 0:
            continue

        # max shares we can sell (50% cap)
        max_to_sell = total_shares // 2

        # max proceeds if we sold 50%
        max_proceeds = Decimal(max_to_sell) * market_price

        # check against portfolio balance left
        if max_proceeds <= balance_left:
            # sell full 50% of this stock
            shares_to_sell = max_to_sell
            proceeds = max_proceeds
        else:
            # sell only as much as balance allows
            shares_to_sell = (balance_left / market_price).to_integral_value(rounding=ROUND_DOWN)
            proceeds = shares_to_sell * market_price

        # Deduct from balance
        balance_left -= proceeds

        # Add to report
        report.append({
            "symbol": bond.bond_name.symbol if hasattr(bond.bond_name.symbol, "symbol") else str(bond.bond_name),
            "bond_name": str(bond.bond_name.bond_name),
            "number_of_share": total_shares,
            "daily_value": float(market_price),
            "ytm": float(bond.bond_name.yield_to_maturity),
            "total_current_value": float(bond.total_current_value),
            "nbr_of_sell_share": int(shares_to_sell),
            "percentage_sold": "50%" if shares_to_sell == max_to_sell else f"{(shares_to_sell / total_shares * 100):.2f}%",
            "nbr_shares_sold": int(shares_to_sell),
            "net_sell_price": float(market_price),
            "sold_amount": float(proceeds),
        })

    ### store report in session
    request.session['bond_sold'] = report
    ### delete model data
    SimBondSoldModel.objects.all().delete()

    return report
#////////////////////////////////////jdadev_simulation_confirm_bond_sold/////////
from django.views.decorators.http import require_POST
@require_POST
@login_required
def jdadev_simulation_confirm_bond_sold(request):
    #print("1159 - Confirming bond sold")
    bond_sold = request.session.get('bond_sold', [])

    if not bond_sold:
        print("1163 - not bond_sold")
        # Handle empty session (user didn't select stocks yet)
        messages.error(request, "No bond data found in session.")
        return redirect('some-page')

    for bond in bond_sold:
        ### Format the percentage_sold in case it comes as a string
        percentage_str = bond['percentage_sold']  # "50%"
        if isinstance(percentage_str, str) and percentage_str.endswith('%'):
            percentage_value = Decimal(percentage_str.replace('%', '').strip())
        else:
            percentage_value = Decimal(percentage_str)

        SimBondSoldModel.objects.create(
            client=request.user,
            bond_name=bond['bond_name'],
            nbr_of_shares=bond['number_of_share'],
            current_value=bond['daily_value'],
            yield_to_maturity=bond['ytm'],
            total_current_value=bond['total_current_value'],
            percentage_sold=percentage_value, #stock['percentage_sold'],
            nbr_shares_sold=bond['nbr_shares_sold'],
            net_sell_price=bond['net_sell_price'],
            sold_amount=bond['sold_amount'],
        )
    messages.success(request, f"Successfully  Sold bonds")  # show is current stock and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    ### Clear session after saving
    del request.session['bond_sold']
    ### delete model data
    #SimBondSoldModel.objects.all().delete()
    ### HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = reverse('jdadev_simulation_bond_sold')
    return response

#//////////////////////////////////jdadev_simulation_simulation_bond_sold/////////////////////////////
@login_required
def jdadev_simulation_bond_sold(request):
    sold_bonds = SimBondSoldModel.objects.filter(client=request.user).order_by('-id') #[:10]
    context={'sold_bonds': sold_bonds}
    #print(f"1204: {sold_bonds}")
    return render(request, 'jdadev/jdadev_simulation_bond_sold.html', context)

#//////////////////////////////////jdadev_simulation_mutual_fund_sale/////////////////////////////////
@login_required
def jdadev_simulation_mutual_fund_sale(request):
    ### Get the sess_sec_tgt_ports and sess_sec_port_aft_sale
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])

    ### Get the bn_portfolio_balance
    #print(f"1167: sec_tgt_ports {sec_tgt_ports}")
    #print(f"1068: sec_port_aft_sale {sec_port_aft_sale}")
    mu_portfolio_balance = float(sec_port_aft_sale[3] - sec_tgt_ports[2])
    #print(f"1170 -mu_portfolio_balance: {mu_portfolio_balance:,.2f} sec_port_aft_sale_values[3]: {sec_port_aft_sale[3]:,.2f} minus sec_tgt_ports[2]: {sec_tgt_ports[2]:,.2f}")
    ### Determine if you can sell mu. If float(sec_port_aft_sale[3] > sec_tgt_ports[2])
    # Now check if the client's mu_tot_curr_val is > or < than the sec_tgt_ports[2] (3 for mu) value
    client_mu_portfolio = None
    mutual_fund_sold_rpt = None
    workflow_bs= None
    if float(sec_port_aft_sale[3] > sec_tgt_ports[2]):
        #print(f"true: {sec_port_aft_sale[3]:,.2f} is greater than {sec_tgt_ports[2]:,.2f} proceed with mutual fund sale")
        workflow_bs = "Mutual Fund Sale"

        ### get sim mutuals to exclude from ClientMutualFundsModel since it was initially sold
        #sim_mutual_funds = ClientMutualFundsModel.objects.filter(client=request.user, decision='SELL').values_list('opcvm', flat=True)
        #client_mu_portfolio = ClientMutualFundsModel.objects.filter(client=request.user).exclude(opcvm__ticker__in=sim_mutual_funds) #.annotate(gp_calc=ExpressionWrapper((F('stocks__target_value') / F('daily_value')) - 1, output_field=FloatField())).order_by('-gp_calc')
        client_mu_portfolio = ClientMutualFundsModel.objects.filter(client=request.user)

        ### Generate the mututal fund sold report
        mutual_fund_sold_rpt = generate_mutual_fund_sold_report(request, mu_portfolio_balance, client_mu_portfolio)

        ### Set the workflow_bs to "Stock Sell" send a message to the user
        workflow_bs = "Mutual Fund Sale"
        #print("1198 /////////////////")

        messages.success(request, f"Your after sale mututal fund portfolio {sec_port_aft_sale[3]:,.2f} is greater than your target mututal fund portfolio, {sec_tgt_ports[2]:,.2f}. Mututal Funds sell is required.")
    else:
        messages.warning(request, f"Your after sale mututal fund portfolio {sec_port_aft_sale[3]:,.2f} is less than your target mututal fund portfolio, {sec_tgt_ports[2]:,.2f}. Mututal funds to sell is not required. Redirecting you to the next workflow - Stock Buy")
        workflow_bs = "Stock Buy"
        #print("1189 FALSE")

    context ={'client_mu_portfolio':client_mu_portfolio, "mu_portfolio_balance": mu_portfolio_balance, 'mutual_fund_sold_rpt':mutual_fund_sold_rpt,'workflow_bs':workflow_bs}#, "sec_tgt_ports":sec_tgt_ports, "sec_port_aft_sale":sec_port_aft_sale}
    return render(request, 'jdadev/jdadev_simulation_mutual_fund_sale.html', context)

#////////////////////////////////////////generate_bond_sold_report ////////////////////////////////////
def generate_mutual_fund_sold_report(request, portfolio_balance, client_mu_portfolio):
    """
    Generate a prorata sale report for a client's portfolio,
    capped at 50% per stock and limited by portfolio_balance.
    """
    #sort by gp
    #client_eqr_portfolio = client_eqr_portfolio.annotate(gp_calc=ExpressionWrapper((F('stocks__target_value') / F('daily_value')) - 1, output_field=FloatField())).order_by('gp_calc')

    mututal_funds = client_mu_portfolio

    # Sort by performance ascending
    #mututal_funds = sorted(mututal_funds, key=lambda s: s.opcvm.performance or Decimal("999"), reverse=False)
    mututal_funds = sorted(mututal_funds, key=lambda s: s.opcvm.performance if s.opcvm.performance is not None else Decimal("999"))

    balance_left = Decimal(portfolio_balance)

    report = []

    for mu in mututal_funds:
        if balance_left <= 0:
            break

        # basic mu info
        total_shares = mu.mu_nbr_of_share or 0
        market_price = mu.mu_current_value or Decimal("0")

        if total_shares == 0 or market_price == 0:
            continue

        # max shares we can sell (50% cap)
        max_to_sell = total_shares // 2

        # max proceeds if we sold 50%
        max_proceeds = Decimal(max_to_sell) * market_price
        print(f"max_proceeds: {max_proceeds}")

        # check against portfolio balance left
        if max_proceeds <= balance_left:
            # sell full 50% of this stock

            shares_to_sell = max_to_sell
            proceeds = max_proceeds

        else:
            # sell only as much as balance allows
            shares_to_sell = (balance_left / market_price).to_integral_value(rounding=ROUND_DOWN)
            proceeds = shares_to_sell * market_price
            #print(f"shares_to_sell: {shares_to_sell}")
        # Deduct from balance
        balance_left -= proceeds

        # Add to report
        report.append({
            "opcvm": mu.opcvm.opcvm if hasattr(mu.opcvm, "opcvm") else str(mu.opcvm),
            "depositaire": mu.opcvm.depositaire,
            "market_price": float(mu.mu_current_value),
            "mu_nbr_of_share": total_shares,
            "mu_total_current_value": float(mu.mu_total_current_value),
            "performance": float(mu.opcvm.performance),
            "nbr_of_sell_share": int(shares_to_sell),
            "percentage_sold": "50%" if shares_to_sell == max_to_sell else f"{(shares_to_sell / total_shares * 100):.2f}%",
            "nbr_shares_sold": int(shares_to_sell),
            "net_sell_price": float(market_price),
            "sold_amount": float(proceeds),
        })

    ### store report in session
    request.session['mutual_fund_sold'] = report
    ### delete model data
    SimMutualFundSoldModel.objects.all().delete()

    return report

#////////////////////////////////////jdadev_simulation_confirm_mutual_fund_sold/////////
from django.views.decorators.http import require_POST
@require_POST
@login_required
def jdadev_simulation_confirm_mutual_fund_sold(request):
    mutual_fund_sold = request.session.get('mutual_fund_sold', [])

    if not mutual_fund_sold:
        # Handle empty session (user didn't select mutual_funds yet)
        messages.error(request, "No mutual fund data found in session.")
        return redirect('some-page')

    for mu in mutual_fund_sold:
        print(f"1288 mu: {mu}")
        ### Format the percentage_sold in case it comes as a string
        percentage_str = mu['percentage_sold']  # "50%"
        if isinstance(percentage_str, str) and percentage_str.endswith('%'):
            percentage_value = Decimal(percentage_str.replace('%', '').strip())
        else:
            percentage_value = Decimal(percentage_str)

        SimMutualFundSoldModel.objects.create(
            client=request.user,
            opcvm=mu['opcvm'],
            #depositaire=mu['depositaire'],
            mu_nbr_of_share=mu['mu_nbr_of_share'],
            mu_current_value=mu['market_price'],
            performance=mu['performance'],
            total_current_value=mu['mu_total_current_value'],
            percentage_sold=percentage_value, #stock['percentage_sold'],
            nbr_shares_sold=mu['nbr_shares_sold'],
            net_sell_price=mu['net_sell_price'],
            sold_amount=mu['sold_amount'],
        )
    messages.success(request, f"Successfully  Sold Mutual Funds")  # show is current mutual_fund and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    ### Clear session after saving
    del request.session['mutual_fund_sold']
    ### delete model data
    #SimStockSoldModel.objects.all().delete()
    ### HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = reverse('jdadev_simulation_mutual_fund_sold')
    return response

#//////////////////////////////////jdadev_simulation_mutual_fund_sold/////////////////////////////
@login_required
def jdadev_simulation_mutual_fund_sold(request):
    sold_mutual_funds = SimMutualFundSoldModel.objects.filter(client=request.user).order_by('-id') #[:10]
    context={'sold_mutual_funds': sold_mutual_funds}
    return render(request, 'jdadev/jdadev_simulation_mutual_fund_sold.html', context)


#//////////////////////////////////jdadev_simulation_stock_buy/////////////////////////////////
@login_required
def jdadev_simulation_stock_buy(request):#, workflow_bs, sec_tgt_ports, sec_port_aft_sale):
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])
    #print(f"1271 - sec_tgt_ports: {sec_tgt_ports}")
    #print(f"1272 - sec_port_aft_sale: {sec_port_aft_sale}")
    # First delete the previous simulation
    SimStockPurchasedModel.objects.all().delete()

    user = request.user
    workflow_bs = None

    ### client_portfolio_balance is the difference between the portfolio after sale and the target portfolio for the product, stocks
    client_portfolio_balance = float(sec_tgt_ports[0]) -float(sec_port_aft_sale[1])

    ### Decision point: We need to buy stocks since eq_after_sale < eq_tgt_port
    #Get the portfolio_balance after the initial sale
    #print(f"1283 true: {sec_port_aft_sale[1]:,.2f} is less than {sec_tgt_ports[0]:,.2f} buy stocks if you have enough liquidity")
    if sec_port_aft_sale[1] < sec_tgt_ports[0]: #[1],[0] for eq
        #print(f"1285 true: {sec_port_aft_sale[1]} is greater than {sec_tgt_ports[0]} buy stocks if you have enough liquidity")
        ### Check if you have enough lq up to 5% of lq from the init sale
        lq_5 = sec_port_aft_sale[0] * 0.95
        ### check if you bought stocks to adjust your lq balance since it's the previous sequence
        total_stock_purchase_amt = SimStockPurchasedModel.objects.aggregate(total=Sum('purchase_amount'))['total'] or 0
        curr_lq_balance = float(lq_5) - float(total_stock_purchase_amt)
        if client_portfolio_balance <=curr_lq_balance:
            ### you have enough cash to purchase stocks
            messages.success(request, f"Your have enough liquidity to purchase more stocks: Your current liquid balance is <b>{curr_lq_balance:,.2f}</b> given you want to spend: {client_portfolio_balance}. ")
            workflow_bs ='Buy Stock' #
        else:
            # You don't have enough lq
            #print(f"1297 - You don't have enough lq curr bal is {curr_lq_balance}")
            messages.warning(request, f"Your DON'T have enough liquidity to purchase more stocks: Your current liquid balance is <b>{curr_lq_balance:,.2f}</b> given you want to spend: <b>{client_portfolio_balance:,.2f}</b>. ")
            workflow_bs ='Buy Bond'
    else:
        workflow_bs ='Buy Bond'
        #print("1300 You can't buy stocks... ")
        messages.warning(request, f"Your equity portfolio after sale is {sec_port_aft_sale[1]:,.2f} is less than your equity target portfolio : {sec_tgt_ports[0]:,.2f}. Proceed to next workflow - Buy Bond")

    #print(f"1302 stock tgt and after_sale - {sec_tgt_ports[0]} - {sec_port_aft_sale[1]}")

    context ={'client_portfolio_balance':client_portfolio_balance, 'workflow_bs':workflow_bs}
    return render(request, 'jdadev/jdadev_simulation_stock_buy.html', context)

#//////////////////////////////////////////////////////jdadev_simulation_get_number_of_stocks/////////////////
@login_required
def jdadev_simulation_get_number_of_stocks(request, client_portfolio_balance): #, sec_port_aft_sale, sec_tgt_ports):
    stock_count = int(request.GET.get('stock_count', 0))
    #sec_tgt_ports
    #sec_port_aft_sale
    # Customize these
    client_id = request.user.id

    total_portfolio_balance= float(client_portfolio_balance)
    percentage_per_stock = round(100.0 / stock_count, 2)

    # Subquery to get number_of_share from ClientEquityAndRightsModel
    number_of_share_subquery = ClientEquityAndRightsModel.objects.filter(stocks=OuterRef('stocks'),client_id=client_id).values('nbr_of_stocks')[:1]

    # Base query
    stocks_with_gp = (
        StockDailyValuesModel.objects
            .filter(daily_value__gt=0)
            .annotate(
            gp=ExpressionWrapper(
                F('target_value') / F('daily_value'),
                output_field=DecimalField(max_digits=18, decimal_places=4)
            ),
            number_of_share=Coalesce(
                Subquery(number_of_share_subquery, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField()
            ),
            total_current_value=ExpressionWrapper(
                F('daily_value') * F('number_of_share'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
            percentage_purchase=ExpressionWrapper(
                Value(percentage_per_stock),
                output_field=FloatField()
            ),
            purchase_amount=ExpressionWrapper(
                Value(total_portfolio_balance) * Value(percentage_per_stock) / Value(100),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
            nbr_shares_to_buy=ExpressionWrapper(
                (Value(total_portfolio_balance) * Value(percentage_per_stock) / Value(100)) / F('daily_value'),
                output_field=IntegerField()
            ),
            net_purchase_price=ExpressionWrapper(
                F('nbr_shares_to_buy') * F('daily_value'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )
            .order_by('-gp')[:stock_count]
    )

    # Convert queryset into list of dicts for session storage
    stocks_list = list(
        stocks_with_gp.values(
            "ticker",
            "number_of_share",
            "daily_value",
            "target_value",
            "gp",
            "total_current_value",
            "percentage_purchase",
            "nbr_shares_to_buy",
            "net_purchase_price",
            "purchase_amount"
        )
    )

    # Optionally convert Decimals to floats for JSON serialization
    for stock in stocks_list:
        for key, value in stock.items():
            if isinstance(value, Decimal):
                stock[key] = float(value)

    #print(f"1141 - stock_list: {stocks_list}")
    # Save to session
    request.session['pending_stocks'] = stocks_list

    context = {'stocks':stocks_with_gp}
    return render(request, 'jdadev/partials/jdadev_simulation_number_of_stocks.html', context)


#////////////////////////////////////jdadev_simulation_confirm_stock_purchase/////////
from django.views.decorators.http import require_POST
@require_POST
@login_required
def jdadev_simulation_confirm_stock_purchase(request):
    stock_data = request.session.get('pending_stocks', [])

    if not stock_data:
        # Handle empty session (user didn't select stocks yet)
        messages.error(request, "No stock data found in session.")
        return redirect('some-page')

    # stock_data is now a list of dicts, same structure as above
    for stock in stock_data:
        SimStockPurchasedModel.objects.create(
            client=request.user,
            ticker=stock['ticker'],
            number_of_share=stock['number_of_share'],
            daily_value=stock['daily_value'],
            target_value=stock['target_value'],
            gp=stock['gp'],
            total_current_value=stock['total_current_value'],
            percentage_purchase=stock['percentage_purchase'],
            nbr_shares_to_buy=stock['nbr_shares_to_buy'],
            net_purchase_price=stock['net_purchase_price'],
            purchase_amount=stock['purchase_amount'],
        )
    #messages.success(request, f"Successfully  Purchased stocks")  # show is current stock and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    # Optionally clear session after saving
    del request.session['pending_stocks']
    # HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = '/jdadev/jdadev_simulation_stock_purchased'  # URL mapped to purchased stock page
    return response

#//////////////////////////////////jdadev_purchased_stock/////////////////////////////////
@login_required
def jdadev_simulation_stock_purchased(request):
    purchased_stocks = SimStockPurchasedModel.objects.filter(client=request.user).order_by('-id') #[:10]
    context={'purchased_stocks': purchased_stocks}
    return render(request, 'jdadev/jdadev_simulation_stock_purchased.html', context)

#//////////////////////////////////jdadev_simulation_bond_buy/////////////////////////////////
@login_required
def jdadev_simulation_bond_buy(request): #, workflow_bs, sec_tgt_ports, sec_port_aft_sale):
    #print("1209 jdadev_simulation_bond_buy")
    ### Get the sess_sec_tgt_ports and sess_sec_port_aft_sale
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])
    print(f"1550 - sess_sec_tgt_ports: {sec_tgt_ports}")
    print(f"1551 - sess_sec_port_aft_sale: {sec_port_aft_sale}")

    ### First delete the previous simulation
    SimBondPurchasedModel.objects.all().delete()

    user = request.user
    workflow_bs = None
    #print(f"1557 - {workflow_bs}")


    ### client_portfolio_balance is the difference between the portfolio after sale and the target portfolio for the product, bond
    client_portfolio_balance = float(sec_tgt_ports[1]) -float(sec_port_aft_sale[2])  #[1] & [2] for bn
    #print(f"1578- client_portfolio_balance: {client_portfolio_balance:,.2f}")

    ### Decision point: We need to buy bonds if bn_after_sale < bn_tgt_port
    #Get the portfolio_balance after the initial sale
    if sec_port_aft_sale[2] < sec_tgt_ports[1]: #[2],[1] for bn
        #print(f"1566true: {sec_port_aft_sale[2]} is less than {sec_tgt_ports[1]} buy bonds if you have enough liquidity")
        ### check if you have enough lq up to 5% of lq from the init sale
        lq_5 = sec_port_aft_sale[0] * 0.95
        ### check if you bought stocks to adjust your lq balance since it's the previous sequence
        total_stock_purchase_amt = SimStockPurchasedModel.objects.aggregate(total=Sum('purchase_amount'))['total'] or 0
        curr_lq_balance = float(lq_5) - float(total_stock_purchase_amt)
        if client_portfolio_balance <=curr_lq_balance:
            ### you have enough cash to purchase bondss
            messages.success(request, f"Your have enough liquidity ßto purchase more bonds: Your current liquid balance is {curr_lq_balance:,.2f} given you want to spend: {client_portfolio_balance:,.2f}. ")
            workflow_bs ='Confirm Bond Purchase' #
        else:
            # You don't have enough lq
            #print(f"1240 - You don't have enough lq curr bal is {curr_lq_balance}")
            #print(f"1557 - {workflow_bs}")
            workflow_bs ='Buy Mutual Fund'
    else:
        #print("1582 You can't buy bonds... ")
        workflow_bs ='Buy Mutual Fund'
        #print(f"1584 - {workflow_bs}")
        messages.warning(request, f"Your bond portfolio after sale is {sec_port_aft_sale[2]:,.2f} is greater than your bond target portfolio : {sec_tgt_ports[1]:,.2f}. No need to buy more bonds. Proceed to next workflow - Buy Mutual Fund")

    #print(f"1248 bond tgt and after_sale - {sec_tgt_ports[1]} - {sec_port_aft_sale[2]}")
    #print(f"1588 workflow_bs - {workflow_bs}")
    #print(f"1245 - client_portfolio_balance: {client_portfolio_balance} ")
    context ={'client_portfolio_balance':client_portfolio_balance, 'workflow_bs':workflow_bs}#, "sec_tgt_ports":sec_tgt_ports, "sec_port_aft_sale":sec_port_aft_sale}
    return render(request, 'jdadev/jdadev_simulation_bond_buy.html', context)

#//////////////////////////////////////////////////////jdadev_simulation_get_number_of_bonds/////////////////
def jdadev_simulation_get_number_of_bonds(request, client_portfolio_balance):
    bond_count = int(request.GET.get('bond_count', 0))
    #print(f"1254 - bond_count: {bond_count}")
    #print(f"1255 - client_portfolio_balance: {client_portfolio_balance}")
    client_id = request.user.id

    #lool

    total_portfolio_balance= float(client_portfolio_balance)
    percentage_per_bond = round(100.0 / bond_count, 2)
    #///
    # Subquery: fetch client's number of shares for each BondModel
    client_shares_sq = Subquery(
        ClientBondsModel.objects.filter(
            client=request.user,
            symbol=OuterRef('pk')  # BondModel.pk <-> ClientBondsModel.symbol (FK)
        ).values('nbr_of_shares')[:1],
        output_field=IntegerField(),
    )

    # Annotate BondModel queryset with client-specific data
    bonds_with_ytm = (
        BondModel.objects.filter(current_value__gt=0)
            .annotate(
            client_nbr_of_shares=Coalesce(client_shares_sq, Value(0), output_field=IntegerField()),
        )
            .annotate(
            total_current_value=ExpressionWrapper(
                F('current_value') * F('client_nbr_of_shares'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
            percentage_purchase=ExpressionWrapper(
                Value(percentage_per_bond),
                output_field=FloatField()
            ),
            purchase_amount=ExpressionWrapper(
                Value(total_portfolio_balance) * Value(percentage_per_bond) / Value(100),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
            nbr_shares_to_buy=ExpressionWrapper(
                (Value(total_portfolio_balance) * Value(percentage_per_bond) / Value(100)) / F('current_value'),
                output_field=IntegerField()
            ),
            net_purchase_price=ExpressionWrapper(
                F('nbr_shares_to_buy') * F('current_value'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
        )
            .order_by('-yield_to_maturity')[:bond_count]
    )

    # Return as list of dictionaries
    bonds_list = list(
        bonds_with_ytm.values(
            "symbol",                # Bond symbol
            "client_nbr_of_shares",  # <-- from ClientBondsModel (NOT BondModel)
            "current_value",
            "yield_to_maturity",
            "total_current_value",
            "percentage_purchase",
            "nbr_shares_to_buy",
            "net_purchase_price",
            "purchase_amount",
        )
    )

    #///

    # # Subquery to get number_of_share from ClientEquityAndRightsModel
    # number_of_share_subquery = ClientBondsModel.objects.filter(bond_name=OuterRef('bond_names'),client=request.user).values('nbr_of_shares')[:1]
    # #print(f"1264 - number_of_share_subquery: {number_of_share_subquery}")
    # #tmp
    # bonds_with_ytm=BondModel.objects.filter(current_value__gt=0).annotate(
    #     number_of_share=Coalesce(
    #              Subquery(number_of_share_subquery, output_field=IntegerField()),
    #              Value(0),
    #              output_field=IntegerField()
    #          ),
    #         total_current_value=ExpressionWrapper(
    #                      F('current_value') * F('nbr_of_shares'),
    #                      output_field=DecimalField(max_digits=18, decimal_places=2)
    #                  ),
    #         percentage_purchase=ExpressionWrapper(
    #                      Value(percentage_per_bond),
    #                      output_field=FloatField()
    #                  ),
    #         purchase_amount=ExpressionWrapper(
    #                  Value(total_portfolio_balance) * Value(percentage_per_bond) / Value(100),
    #                  output_field=DecimalField(max_digits=18, decimal_places=2)
    #              ),
    #         nbr_shares_to_buy=ExpressionWrapper(
    #                  (Value(total_portfolio_balance) * Value(percentage_per_bond) / Value(100)) / F('current_value'),
    #                  output_field=IntegerField()
    #              ),
    #         net_purchase_price=ExpressionWrapper(
    #                      F('nbr_shares_to_buy') * F('current_value'),
    #                      output_field=DecimalField(max_digits=18, decimal_places=2)
    #                  )
    #
    #
    # ).order_by('-yield_to_maturity')[:bond_count]
    #
    # ### Convert queryset into list of dicts for session storage
    # bonds_list = list(
    #     bonds_with_ytm.values(
    #         "symbol",
    #         "number_of_share",
    #         "current_value",
    #         "yield_to_maturity",
    #         "total_current_value",
    #         "percentage_purchase",
    #         "nbr_shares_to_buy",
    #         "net_purchase_price",
    #         "purchase_amount"
    #     )
    # )
    # #print(f"1312 - bonds_list: {bonds_list}")

    ### Optionally convert Decimals to floats for JSON serialization
    for bond in bonds_list:
         for key, value in bond.items():
             if isinstance(value, Decimal):
                 bond[key] = float(value)

    #print(f"1328 - bond_list: {bonds_list}")
    ### Save to session
    request.session['pending_bonds'] = bonds_list

    context = {'bonds': bonds_with_ytm}
    return render(request, 'jdadev/partials/jdadev_simulation_number_of_bonds.html', context)

#////////////////////////////////////jdadev_simulation_confirm_stock_purchase/////////
from django.views.decorators.http import require_POST
@require_POST
@login_required
def jdadev_simulation_confirm_bond_purchase(request):
    bond_data = request.session.get('pending_bonds', [])
    #print(f"1329 - bond_data: {bond_data}")

    if not bond_data:
        # Handle empty session (user didn't select bonds yet)
        messages.error(request, "No bond data found in session.")
        #print(f"1333 - No bond data found in session")
        return redirect('some-page') # XXXX Fix redirection

    # bond_data is now a list of dicts, same structure as above
    for bond in bond_data:
        SimBondPurchasedModel.objects.create(
            client=request.user,
            bond_name=bond['symbol'],
            nbr_of_shares=bond['number_of_share'],
            current_value=bond['current_value'],
            yield_to_maturity=bond['yield_to_maturity'],
            total_current_value=bond['total_current_value'],
            percentage_purchase=bond['percentage_purchase'],
            nbr_shares_to_buy=bond['nbr_shares_to_buy'],
            net_purchase_price=bond['net_purchase_price'],
            purchase_amount=bond['purchase_amount'],
        )
    messages.success(request, f"Successfully  Purchased bonds")  # show is current bond and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    # Optionally clear session after saving
    del request.session['pending_bonds']
    # HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = '/jdadev/jdadev_simulation_bond_purchased'  # URL mapped to purchased bond page
    return response

#//////////////////////////////////jdadev_simulation_bond_purchased/////////////////////////////////
@login_required
def jdadev_simulation_bond_purchased(request):
    purchased_bonds = SimBondPurchasedModel.objects.filter(client=request.user).order_by('yield_to_maturity') #[:10]
    context={'purchased_bonds': purchased_bonds}
    return render(request, 'jdadev/jdadev_simulation_bond_purchased.html', context)


#\\\\\\\\\\\\\\\\\\\\\\\\\\\ BOND Stuff \\\\\\\\\\\\\\\\\\\

#\\\\\\\\\\\\\\\\\\\\\\\\ START MU Stuff
#//////////////////////////////////jdadev_simulation_mutual_fund_buy/////////////////////////////////
@login_required
def jdadev_simulation_mutual_fund_buy(request): #, workflow_bs, sec_tgt_ports, sec_port_aft_sale):
    #print("1604 -  jdadev_simulation_mutual_fund_buy")
    ### Get the sess_sec_tgt_ports and sess_sec_port_aft_sale
    sec_tgt_ports = request.session.get('sec_tgt_ports', [])
    sec_port_aft_sale = request.session.get('sec_port_aft_sale', [])
    #print(f"1608 - sess_sec_tgt_ports: {sec_tgt_ports}")
    #print(f"1609 - sess_sec_port_aft_sale: {sec_port_aft_sale}")

    ### First delete the previous simulation db data if it exists
    SimMutualFundPurchasedModel.objects.all().delete()

    user = request.user
    workflow_bs=None

    ### client_portfolio_balance is the difference between the portfolio after sale and the target portfolio for the product, mu
    client_portfolio_balance = float(sec_port_aft_sale[3]) - float(sec_tgt_ports[2])   #[2] & [3] for mu
    #print(f"1733- client_portfolio_balance: {client_portfolio_balance:,.2f}")

    ### Decision point: We need to buy mus if mu_after_sale < mu_tgt_port
    #Get the portfolio_balance after the initial sale
    if sec_port_aft_sale[3] < sec_tgt_ports[2]: #[3],[2] for mu
        #print(f"1738 true: {sec_port_aft_sale[3]} is less than {sec_tgt_ports[2]} buy mus if you have enough liquidity")
        ### check if you have enough lq up to 5% of lq from the init sale
        lq_5 = sec_port_aft_sale[0] * 0.95
        ### check if you bought stocks or bonds to adjust your lq balance since they are  the previous sequences
        total_stock_purchase_amt = SimStockPurchasedModel.objects.aggregate(total=Sum('purchase_amount'))['total'] or 0
        total_bond_purchase_amt = SimBondPurchasedModel.objects.aggregate(total=Sum('purchase_amount'))['total'] or 0
        curr_lq_balance = float(lq_5) - (float(total_stock_purchase_amt) + float(total_bond_purchase_amt))
        #print(f"1630 -curr_lq_balance: {curr_lq_balance}")
        if client_portfolio_balance <=curr_lq_balance:
            ### you have enough cash to purchase mutual funds
            #print("1748 - you have enough cash to purchase mutual funds")
            messages.success(request, f"Your have enough liquidity to purchase more mutual funds: Your current liquid balance is {curr_lq_balance:,.2f} given you want to spend: {client_portfolio_balance:,.2f}. ")

            workflow_bs ='Confirm Mutual Fund Purchase'
        else:
            # You don't have enough lq
            workflow_bs ='Stock Sale'
            #print(f"1754 - You don't have enough lq curr bal is {curr_lq_balance:,.2f}")
            #print("1755 redirecting to prev")
            messages.error(request, f"Your dont't have enough liquidity to purchase mutual funds: Your current liquid balance is {curr_lq_balance:,.2f} given you want to spend: {client_portfolio_balance:,.2f}.")
            return redirect('jdadev_simulation_bond_purchased')
    else:
        messages.warning(request, f"Your Mutual Fund portfolio after sale is {sec_port_aft_sale[3]:,.2f} is greater than your Mututal Fund target portfolio : {sec_tgt_ports[2]:,.2f}. No need to buy more mutual funds. Proceed to next workflow - Sell Stocks")
        workflow_bs ='Stock Sale'
        #print("1759 You can't buy mutual funds... ")


    context ={'client_portfolio_balance':client_portfolio_balance, 'workflow_bs':workflow_bs}
    return render(request, 'jdadev/jdadev_simulation_mutual_fund_buy.html', context)

#////////////////////////////////////jdadev_simulation_get_number_of_mutual_funds/////////////////
def jdadev_simulation_get_number_of_mutual_funds(request, client_portfolio_balance):
    mutual_fund_count = int(request.GET.get('mutual_fund_count', 0))
    #print(f"1655 - mutual_fund_count: {mutual_fund_count}")
    #print(f"1656 - client_portfolio_balance: {client_portfolio_balance}")
    client_id = request.user.id

    total_portfolio_balance= float(client_portfolio_balance)
    percentage_per_mutual_fund = round(100.0 / mutual_fund_count, 2)

    # Subquery to get number_of_share from ClientEquityAndRightsModel
    number_of_share_subquery = ClientMutualFundsModel.objects.filter(opcvm=OuterRef('opcvm'),client=request.user).values('mu_nbr_of_share')[:1]

    ###  START UPDATES FROM HERE ###
    mututal_funds_with_perf=MutualFundModel.objects.filter(current_value__gt=0).annotate(
        mu_nbr_of_share=Coalesce(
            Subquery(number_of_share_subquery, output_field=IntegerField()),
            Value(0),
            output_field=IntegerField()
        ),
        mu_total_current_value=ExpressionWrapper(
            F('current_value') * F('nbr_of_share'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        ),
        percentage_purchase=ExpressionWrapper(
            Value(percentage_per_mutual_fund),
            output_field=FloatField()
        ),
        purchase_amount=ExpressionWrapper(
            Value(total_portfolio_balance) * Value(percentage_per_mutual_fund) / Value(100),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        ),
        nbr_shares_to_buy=ExpressionWrapper(
            (Value(total_portfolio_balance) * Value(percentage_per_mutual_fund) / Value(100)) / F('current_value'),
            output_field=IntegerField()
        ),
        net_purchase_price=ExpressionWrapper(
            F('nbr_shares_to_buy') * F('current_value'),
            output_field=DecimalField(max_digits=18, decimal_places=2)
        )


    ).order_by('-performance')[:mutual_fund_count]

    ### Convert queryset into list of dicts for session storage
    mutual_funds_list = list(
        mututal_funds_with_perf.values(
            "opcvm",
            "nbr_of_share",
            "current_value",
            "performance",
            "mu_total_current_value",
            "percentage_purchase",
            "nbr_shares_to_buy",
            "net_purchase_price",
            "purchase_amount"
        )
    )
    #print(f"1312 - bonds_list: {mutual_funds_list}")

    ### Optionally convert Decimals to floats for JSON serialization
    for mu in mutual_funds_list:
        for key, value in mu.items():
            if isinstance(value, Decimal):
                mu[key] = float(value)

    #print(f"1328 - bond_list: {mutual_funds_list}")
    ### Save to session
    request.session['pending_mutual_funds'] = mutual_funds_list

    context = {'mutual_funds': mututal_funds_with_perf}
    return render(request, 'jdadev/partials/jdadev_simulation_number_of_mutual_funds.html', context)

#///////////////////////////////jdadev_simulation_confirm_mutual_fund_purchase////////////////////////////
@require_POST
@login_required
def jdadev_simulation_confirm_mutual_fund_purchase(request):
    mutual_fund_data = request.session.get('pending_mutual_funds', [])
    #print(f"1498The  - mutual_fund_data: {mutual_fund_data}")

    if not mutual_fund_data:
        # Handle empty session (user didn't select bonds yet)
        messages.error(request, "No bond data found in session.")
        #print(f"1333 - No bond data found in session")
        return redirect('some-page') # XXXX Fix redirection

    # bond_data is now a list of dicts, same structure as above
    for mu in mutual_fund_data:
        SimMutualFundPurchasedModel.objects.create(
            client=request.user,
            opcvm=mu['opcvm'],
            mu_nbr_of_share=mu['nbr_of_share'],
            mu_current_value=mu['current_value'],
            performance=mu['performance'],
            total_current_value=mu['mu_total_current_value'],
            percentage_purchase=mu['percentage_purchase'],
            nbr_shares_to_buy=mu['nbr_shares_to_buy'],
            net_purchase_price=mu['net_purchase_price'],
            purchase_amount=mu['purchase_amount'],
        )
    messages.success(request, f"Successfully  Purchased Mutual Funss")  # show is current bond and cash balanced: {client_portfolio_balance}. ")
    # Now update the target_portfolio

    # Optionally clear session after saving
    del request.session['pending_mutual_funds']
    # HTMX redirect header
    response = HttpResponse()
    response['HX-Redirect'] = '/jdadev/jdadev_simulation_mutual_fund_purchased'  # URL mapped to purchased bond page
    return response

#//////////////////////////////////jdadev_simulation_bond_purchased/////////////////////////////////
@login_required
def jdadev_simulation_mutual_fund_purchased(request):
    purchased_mutual_funds = SimMutualFundPurchasedModel.objects.filter(client=request.user).order_by('-performance') #[:10]

    context={'purchased_mutual_funds': purchased_mutual_funds}
    return render(request, 'jdadev/jdadev_simulation_mutual_fund_purchased.html', context)

#\\\\\\\\\\\\\\\\\\\\\\\\ END MU Stuff



# #//////////////////////////////////jdadev_simulation_bond_buy/////////////////////////////////
# def jdadev_simulation_bond_buy(request):
#     user = request.user
#
#     #client_portfolio_balance
#     client_portfolio_balance = ClientPortfolioModel.objects.aggregate(
#         portfolio_balance=Sum(
#             ExpressionWrapper(
#                 F('liquid_assets') + F('equity_and_rights') + F('bonds') + F('mutual_funds'),
#                 output_field=DecimalField(max_digits=18, decimal_places=2)
#             )
#         )
#     )
#
#
#     context ={'client_portfolio_balance':client_portfolio_balance['portfolio_balance']}
#     return render(request, 'jdadev/jdadev_simulation_bond_buy.html', context)

#
# #//////////////////////////////////////////////////////jdadev_simulation_get_number_of_bonds/////////////////
# def jdadev_simulation_get_number_of_bonds(request):
#     bond_count = int(request.GET.get('bond_count', 0))
#     # Customize these
#     client_id = request.user.id  # Replace with actual client/user ID (e.g., request.user.id)
#
#     #client_portfolio_balance
#     client_portfolio_balance = ClientPortfolioModel.objects.aggregate(
#         portfolio_balance=Sum(
#             ExpressionWrapper(
#                 F('liquid_assets') + F('equity_and_rights') + F('bonds') + F('mutual_funds'),
#                 output_field=DecimalField(max_digits=18, decimal_places=2)
#             )
#         )
#     )
#     total_portfolio_balance= client_portfolio_balance['portfolio_balance']
#     percentage_per_stock = round(100.0 / bond_count, 2)
#
#     # Subquery to get number_of_share from ClientBondsModel
#     number_of_share_subquery = ClientBondsModel.objects.filter(
#         bond_name=OuterRef('nbr_of_shares'),
#         client_id=client_id
#     ).values('nbr_of_shares')[:1]
#
#     # Base query
#     bonds_with_gp = (
#         BondModel.objects
#             .filter(current_value__gt=0)
#             .annotate(
#             gp=ExpressionWrapper(
#                 F('current_value') / F('original_value'),
#                 output_field=DecimalField(max_digits=18, decimal_places=4)
#             ),
#             number_of_share=Coalesce(
#                 Subquery(number_of_share_subquery, output_field=IntegerField()),
#                 Value(0),
#                 output_field=IntegerField()
#             ),
#             total_current_value=ExpressionWrapper(
#                 F('current_value') * F('number_of_share'),
#                 output_field=DecimalField(max_digits=18, decimal_places=2)
#             ),
#             purchase_percentage=ExpressionWrapper(
#                 Value(percentage_per_stock),
#                 output_field=FloatField()
#             ),
#             purchase_amount=ExpressionWrapper(
#                 Value(total_portfolio_balance) * Value(percentage_per_stock) / Value(100),
#                 output_field=DecimalField(max_digits=18, decimal_places=2)
#             ),
#             nbr_shares_to_buy=ExpressionWrapper(
#                 (Value(total_portfolio_balance) * Value(percentage_per_stock) / Value(100)) / F('current_value'),
#                 output_field=IntegerField()
#             ),
#             net_purchase_price=ExpressionWrapper(
#                 F('nbr_shares_to_buy') * F('current_value'),
#                 output_field=DecimalField(max_digits=18, decimal_places=2)
#             )
#         )
#             .order_by('-gp')[:bond_count]
#     )
#
#
#     context = {'bonds':bonds_with_gp}
#     return render(request, 'jdadev/partials/jdadev_simulation_number_of_bonds.html', context)
#//////////////////////////////// adjusted_per_bn //////////////////////////////////
#@login_required
def adjusted_per_bn(portfolio_type, per_tot, per_bn, per_mu):
    #print(f"626 per_tot: {per_tot}")
    #print(f"395 per_bn: {per_bn} - per_mu: {per_mu}")
    adj_bn = 0
    adj_mu = 0
    adj_vals=[]
    if portfolio_type =='dynamic':
        if per_bn+per_mu >per_tot*Decimal(.20):
            #print(f"401 If per_bn+per_mu: {per_bn+per_mu} > per_tot*20: {per_tot*Decimal(.20)}")
            x_mu=per_tot*Decimal(.20)-per_mu
            #print(f"403 - x_mu: {x_mu}")
            if x_mu <0:
                adj_bn=0
                adj_mu =.20
            else:
                adj_bn=x_mu
                adj_mu=per_mu

            #print(f"411 x_mu: {x_mu} - per_mu:{per_mu}- adj_bn: {adj_bn} - adj_mu: {adj_mu}")
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
    #print(f"444 - adj_bn:{adj_bn} - adj_mu:{adj_mu}")


    return adj_vals

#///////////////////////////////////jdadev_view_client_list////////////////////////////////
@login_required
#@allowed_users(allowed_roles=['admins','managers','staffs'])
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
    #print(client)
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




#//////////////////////////////reload_symbols////////////////////////////////
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def reload_opcvm(request, soc_text):
    #print(f"261: soc_text:{soc_text}")
    latest_entry_date = MutualFundModel.objects.order_by('-entry_date').values_list('entry_date', flat=True).first()
    if soc_text == "":

        opcvm = MutualFundModel.objects.filter(entry_date=latest_entry_date).order_by('opcvm')
        #print(f"depositaire all:{depositaire}")
    else:
        opcvm = MutualFundModel.objects.filter(entry_date=latest_entry_date).filter(depositaire=soc_text).order_by('opcvm').distinct()
        # opc=[]
        # for i in opcvm:
        #     opc.append(i.opcvm)
        # unique_dep = list(set(opc))

    context ={'opcvm':opcvm}
    return render(request, 'jdadev/partials/jdadev_opcvm.html', context)



#//////////////////////////////reload_mu_original_value////////////////////////////////
@login_required
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
@login_required
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
@login_required
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
@login_required
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
    #print(stock_id)

    #latest_entry_date = StockDailyValuesModel.objects.order_by('-entry_date').values_list('entry_date', flat=True).first()

    #stock = StockDailyValuesModel.objects.filter(entry_date=latest_entry_date).filter(id=stock_id)

    stock = get_object_or_404(StockDailyValuesModel, id=stock_id)
    data = {'daily_value': stock.daily_value,}
    #print(f"data: {data}")
    return JsonResponse(data)



#/////////////////////////////// upload_file //////////////////////////////////////////////////////////
@login_required
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                excel_file = request.FILES['file']
                df = pd.read_excel(excel_file)

                # Convert DataFrame to list of model instances
                objects_to_create = []
                duplicates = 0
                created = 0
                today = timezone.now().date()

                for index, row in df.iterrows():
                    ticker = row['Ticker']
                    daily_value = row['Daily Value']
                    target_value = row.get('Target Value', 0.00)  # Use get to handle missing columns

                    # Check if this ticker already exists for today
                    exists = StockDailyValuesModel.objects.filter(
                        ticker=ticker,
                        entry_date=today
                    ).exists()

                    if exists:
                        duplicates += 1
                        # Optional: Update existing records instead of skipping
                        # StockDailyValuesModel.objects.filter(ticker=ticker, entry_date=today).update(
                        #     daily_value=daily_value,
                        #     target_value=target_value
                        # )
                    else:
                        objects_to_create.append(StockDailyValuesModel(
                            ticker=ticker,
                            daily_value=daily_value,
                            target_value=target_value,
                            # Let entry_date default to today
                        ))
                        created += 1

                # Bulk create for better performance
                if objects_to_create:
                    StockDailyValuesModel.objects.bulk_create(objects_to_create)

                messages.success(request, f'Successfully processed {len(df)} rows. Created {created} new records. Found {duplicates} duplicates.')
                return render(request, 'jdadev/jdadev_upload_success.html')

            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'jdadev/jdadev_upload_file.html', {'form': form})
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/jdadev_upload_file.html', {'form': form})
# def upload_file(request):
#     #print("file upload")
#     if request.method == 'POST':
#         form = UploadFileForm(request.POST, request.FILES)
#         if form.is_valid():
#             excel_file = request.FILES['file']
#             df = pd.read_excel(excel_file)
#             for index, row in df.iterrows():
#                 StockDailyValuesModel.objects.create(
#                     ticker=row['Ticker'],
#                     daily_value=row['Daily Value'],
#                     target_value=row['Target Value'],
#                 )
#             return render(request, 'success.html')
#     else:
#         form = UploadFileForm()
#     return render(request, 'jdadev/jdadev_upload_success.html', {'form': form})

#///////////////////////////////////////upload_excel//////////////////////////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def upload_excel(request):
    #print("1716 file upload ")
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
                        if "UNIQUE constraint failed" in str(e):
                            #print("Found the keyword!")
                            #print(f"1327 Exception e:{e}")
                            return render(request, 'jdadev/upload_error.html', {'error_message': f"The file data already exists. Click below to delete and reload", 'stocks_delete':'True'})
                        else:
                            print(f"1330 Exception e:{e}")
                        #return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
                            return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                print(f"1329 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            return render(request, 'jdadev/upload_success.html')
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})


#/////////////////////////////////////jdadev_clear_stock_data/////////////////////////////////
#@allowed_users(allowed_roles=['admins','managers', 'staffs'])
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_clear_stock_data(request):
    if request.method == 'POST':
        try:
            # Option 1: Delete only today's records
            today = timezone.now().date()
            deleted, _ = StockDailyValuesModel.objects.filter(entry_date=today).delete()
            messages.success(request, f"Successfully cleared {deleted} stock records for today.")

            # Option 2: Delete records for a specific ticker
            # ticker = request.POST.get('ticker')
            # if ticker:
            #     deleted, _ = StockDailyValuesModel.objects.filter(ticker=ticker).delete()
            #     messages.success(request, f"Successfully cleared {deleted} records for {ticker}.")

        except Exception as e:
            messages.error(request, f"Error clearing stock data: {str(e)}")

    return redirect('upload_excel')

#/////////////////////////////////////jdadev_clear_custom_profile/////////////////////////////////
#@allowed_users(allowed_roles=['admins','managers', 'staffs'])
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_clear_custom_profile(request):
    user = request.user  # Get the logged-in user
    #print(f"user: {user}")

    try:
        # Option 1: Delete only today's records
        today = timezone.now().date()
        deleted, _ = ClientProfileModel.objects.filter(client=user).filter(profile_type='custom').delete()
        messages.success(request, f"Successfully cleared {deleted} user {user} custom profile records.")
        #print("del success")

        # Option 2: Delete records for a specific ticker
        # ticker = request.POST.get('ticker')
        # if ticker:
        #     deleted, _ = StockDailyValuesModel.objects.filter(ticker=ticker).delete()
        #     messages.success(request, f"Successfully cleared {deleted} records for {ticker}.")

    except Exception as e:
        #print(f"E: {e}")
        messages.error(request, f"Error clearing custom user profile data: {str(e)}")

    return redirect("jdadev_home")
    #return redirect('jdadev_overall_portfolio', portfolio_type='custom')
    #return render(request, 'jdadev/jdadev_overall_portfolio.html', {})


#///////////////////////////////////////upload_bond_excel//////////////////////////////
#@allowed_users(allowed_roles=['admins','managers', 'staffs'])
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
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
                        yield_to_maturity = row['yield_to_maturity']
                        BondModel.objects.create(symbol=symbol,
                                                 bond_name=bond_name,
                                                 original_value=original_value,
                                                 coupon=coupon,
                                                 current_value =current_value,
                                                 nbr_of_shares=nbr_of_shares,
                                                 total_value=total_value,
                                                 institution_type=institution_type,
                                                 yield_to_maturity=yield_to_maturity)
                    except Exception as e:
                        #print(f"92 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                #print(f"95 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            # Bond ddata upload is successful.  Now insert intitution types data into the InstitutionTypeModel
            insert_distinct_institution_types(request)
            return render(request, 'jdadev/upload_success.html')
    else:
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})

#/////////////////////////////////////jdadev_clear_bond_data/////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_clear_bond_data(request):
    if request.method == 'POST':
        try:
            # Option 1: Delete only today's records
            today = timezone.now().date()
            deleted, _ = BondModel.objects.filter(entry_date=today).delete()
            messages.success(request, f"Successfully cleared {deleted} today's bond records.")

            # Option 2: Delete records for a specific ticker
            # ticker = request.POST.get('ticker')
            # if ticker:
            #     deleted, _ = StockDailyValuesModel.objects.filter(ticker=ticker).delete()
            #     messages.success(request, f"Successfully cleared {deleted} records for {ticker}.")

        except Exception as e:
            messages.error(request, f"Error clearing bond data: {str(e)}")

    return redirect('upload_excel')
#///////////////////////////////////////upload_mutual_fund_excel//////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def upload_mutual_fund_excel(request):
    print("2337 mutual fund file upload ")
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
                print(f"2354 Pre: {df}")
                # Preprocess the data
                #df['sociate_de_gession'] = df['sociate_de_gession'].apply(lambda x: None if pd.isna(x) else float(x))
                #df['depositaire'] = df['depositaire'].apply(lambda x: None if pd.isna(x) else float(x))
                #df['opcvm'] = df['opcvm'].apply(lambda x: None if pd.isna(x) else float(x))
                df['original_value'] = df['original_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['current_value'] = df['current_value'].apply(lambda x: None if pd.isna(x) else float(x))
                df['nbr_of_share'] = df['nbr_of_share'].apply(lambda x: None if pd.isna(x) else int(x))
                df['performance'] = df['performance'].apply(lambda x: 0.00 if pd.isna(x) or x == '' else float(x))
                #print(f"2363 - {df['performance']}")


                # Replace NaN with a temporary placeholder
                # Replace the temporary placeholder with None

                df['original_value'] = df['original_value'].replace('', 0.00)
                df['current_value'] = df['current_value'].replace('', 0.00)
                df['nbr_of_share'] = df['nbr_of_share'].replace('', 0)
                df['performance'] = df['performance'].replace('', 0.00)
                # Convert numeric fields safely

                # Replace NaN with None so Django ORM can store it properly
                df = df.where(pd.notnull(df), None)

                #print("495 Done with data validation")
                #print(f"Post: {df}")
                #print(f"497 {df['sociate_de_gession']}-----{df['depositaire']}-----{df['opcvm']}-----{df['original_value']}-----{df['nbr_of_share']}")
            except pd.errors.ParserError as pe:
                print(f"2388 Exception pe: {pe}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                print(f"2391 Exception e: {e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: " + str(e)})

            except pd.errors.ParserError:
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error reading Excel file: Invalid file format or corrupted file."})
            except Exception as e:
                print(f"2387 Exception e: {e}")
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
                        performance = row['performance']
                        print(f"2417 - performance: {performance}")

                        MutualFundModel.objects.create(sociate_de_gession=sociate_de_gession,
                                                 depositaire=depositaire,
                                                 opcvm=opcvm,
                                                 original_value=original_value,
                                                 current_value=current_value,
                                                 nbr_of_share=nbr_of_share,
                                                 performance=performance)
                    except Exception as e:
                        print(f"2415 Exception e:{e}")
                        return render(request, 'jdadev/upload_error.html', {'error_message': f"Error creating object from Excel data at row {index + 1}: {str(e)}"})
            except Exception as e:
                print(f"2438 Exception e:{e}")
                return render(request, 'jdadev/upload_error.html', {'error_message': "Error creating objects from Excel data: " + str(e)})

            # Bond ddata upload is successful.  Now insert intitution types data into the InstitutionTypeModel
            #insert_distinct_institution_types(request)
            return render(request, 'jdadev/upload_success.html')
    else:
        #print("543 UploadFileForm")
        form = UploadFileForm()

    return render(request, 'jdadev/upload_excel.html', {'form': form})

#/////////////////////////////////////jdadev_clear_mutual_fund_data/////////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_clear_mutual_fund_data(request):
    if request.method == 'POST':
        try:
            # Option 1: Delete only today's records
            today = timezone.now().date()
            deleted, _ = MutualFundModel.objects.filter(entry_date=today).delete()
            messages.success(request, f"Successfully cleared {deleted} today's Mutual fund records.")

            # Option 2: Delete records for a specific ticker
            # ticker = request.POST.get('ticker')
            # if ticker:
            #     deleted, _ = StockDailyValuesModel.objects.filter(ticker=ticker).delete()
            #     messages.success(request, f"Successfully cleared {deleted} records for {ticker}.")

        except Exception as e:
            messages.error(request, f"Error clearing mutual fund data: {str(e)}")

    return redirect('upload_excel')
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
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
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
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
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
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
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
#@allowed_users(allowed_roles=['admins','managers', 'staffs'])
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
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
@login_required
def jdadev_stock_report(request):
    stocks = StockDailyValuesModel.objects.all()

    context = {'stocks': stocks}
    return render(request, 'jdadev/jdadev_stock_report.html', context)

#/////////////////////////////////jdadev_bond_report////////////////////////////////
@login_required
def jdadev_bond_report(request):
    bonds = BondModel.objects.all()

    context = {'bonds': bonds}
    return render(request, 'jdadev/jdadev_bond_report.html', context)


#/////////////////////////////////jdadev_mututal_fund_report////////////////////////////////
@login_required
def jdadev_mutual_fund_report(request):
    mutual_funds = MutualFundModel.objects.all()

    context = {'mutual_funds': mutual_funds}
    return render(request, 'jdadev/jdadev_mutual_fund_report.html', context)


#////////////////////////// jdadev_client_portfolio ///////////////////////
@login_required
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


#///////////////////////////////////////// jdadev_ai_validator_home /////////////////////////////
@login_required
@allowed_users(allowed_roles=['admins','managers', 'staffs'])
def jdadev_ai_validator_home(request):
    return render(request, "jdadev/jdadev_ai_validator_home.html")


#///////////////////////////////////////// jdadev_ai_validator /////////////////////////////
# views.py


from django.shortcuts import render
from .models import StockDailyValuesModel, ValidatorModel
from openai import OpenAI
import os

def jdadev_ai_validator_report(request):
    # Get the latest date
    latest_entry_date = StockDailyValuesModel.objects.order_by('-entry_date').values_list('entry_date', flat=True).first()
    print(f"latest_entry_date: {latest_entry_date}")

    if not latest_entry_date:
        return render(request, "jdadev/partials/jdadev_ai_validator_report.html", {"report": None})

    # Check cache
    cached = ValidatorModel.objects.filter(entry_date=latest_entry_date).first()
    #print(f"cached: {cached}")
    if cached:
        return render(request, "jdadev/partials/jdadev_ai_validator_report.html", {
            "report": {
                "anomalies": cached.anomalies,
                "missing_data": cached.missing_data,
                "insights": cached.insights
            },
            "cached": True
        })

    # Gather data
    data = StockDailyValuesModel.objects.filter(entry_date=latest_entry_date)
    #print(f"data: {data}")
    formatted_data = "\n".join([
        f"{obj.entry_date} | {obj.ticker} | Value: {obj.daily_value} | Target: {obj.target_value}"
        for obj in data
    ])

    prompt = f"""
    Please analyze the following stock data and return a markdown-formatted report with **these exact section headers**:
    
    # Anomalies  
    # Missing Data  
    # Insights
    
    Only include these three sections — even if one is empty, still include its header with a short explanation. Here's the data:
    
    {formatted_data}
    """

    # Call OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4",
        #tools=[{"type": "web_search_preview"}], # Uncomment for web search functionality
        messages=[
            {"role": "system", "content": "You are a financial data analyst."},
            {"role": "user", "content": prompt}
        ]
    )

    content = response.choices[0].message.content
    #print(f"content: {content}")

    anomalies = jdadev_ai_extract_section(content, "Anomalies")
    missing_data = jdadev_ai_extract_section(content, "Missing Data")
    insights = jdadev_ai_extract_section(content, "Insights")

    #print(f"anomalies: {anomalies}")
    #print(f"missing_data: {missing_data}")
    #print(f"insights: {insights}")

    # Save it
    ValidatorModel.objects.create(
        entry_date=latest_entry_date,
        anomalies=anomalies,
        missing_data=missing_data,
        insights=insights
    )

    return render(request, "jdadev/partials/jdadev_ai_validator_report.html", {
        "report": {
            "anomalies": anomalies,
            "missing_data": missing_data,
            "insights": insights
        },
        "cached": False
    })

#/////////////////////////////////////////////// jdadev_ai_extract_section //////////////////////////////
import re

def jdadev_ai_extract_section(content, section_name):
    pattern = rf"#\s*{section_name}\s*\n(.*?)(?=\n#|$)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


#/////////////////////////////////////////////// jdadev_ai_validator //////////////////////////////
# stock_validator/views.py
#from django.shortcuts import render
#from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
#import datetime
#import pandas as pd
from openai import OpenAI
#from .models import StockDailyValuesModel

#@csrf_exempt
# def jdadev_ai_validator(request):
#     """
#     Function-based view for validating stock data using OpenAI.
#     """
#     if request.method == 'GET':
#         # Handle GET requests to show the validation form
#         return render(request, 'jdadev/jdadev_ai_validator_report.html')
#
#     elif request.method == 'POST':
#         # Handle POST requests to validate the data
#         try:
#             data = json.loads(request.body)
#             date_range = data.get('date_range', 30)  # Default to last 30 days
#             ticker_filter = data.get('ticker', None)
#
#             # Get the data from the database
#             validation_result = perform_validation(date_range, ticker_filter)
#
#             return JsonResponse({
#                 'success': True,
#                 'validation_result': validation_result
#             })
#
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             }, status=400)

# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from django.shortcuts import render
# import json
# # views.py
# # views.py
# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from django.views.decorators.csrf import ensure_csrf_cookie
# import json
#
# @ensure_csrf_cookie
# @require_http_methods(["GET", "POST"])
# def jdadev_ai_validator(request):
#     if request.method == 'GET':
#         return render(request, 'jdadev/jdadev_ai_validator_report.html')
#
#     elif request.method == 'POST':
#         try:
#             # Handle both form data and JSON
#             if request.content_type == 'application/json':
#                 data = json.loads(request.body)
#                 date_range = data.get('date_range', 30)
#                 ticker_filter = data.get('ticker', None)
#             else:
#                 date_range = request.POST.get('date_range', 30)
#                 ticker_filter = request.POST.get('ticker', None)
#
#             # Convert to proper types
#             try:
#                 date_range = int(date_range)
#             except (ValueError, TypeError):
#                 date_range = 30
#
#             if ticker_filter == '':
#                 ticker_filter = None
#
#             # Perform validation
#             validation_result = perform_validation(date_range, ticker_filter)
#
#             return JsonResponse({
#                 'success': True,
#                 'validation_result': validation_result
#             })
#
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': str(e)
#             }, status=400)
#
# def perform_validation(date_range=30, ticker_filter=None):
#     """
#     Validate stock data for missing values and generate insights.
#
#     Args:
#         date_range (int): Number of days to look back
#         ticker_filter (str, optional): Filter for a specific ticker
#
#     Returns:
#         dict: Validation results and insights
#     """
#     # Calculate the start date
#     end_date = datetime.datetime.now().date()
#     start_date = end_date - datetime.timedelta(days=date_range)
#
#     # Query the database
#     queryset = StockDailyValuesModel.objects.filter(entry_date__gte=start_date)
#     if ticker_filter:
#         queryset = queryset.filter(ticker=ticker_filter)
#
#     # Convert to DataFrame for easier analysis
#     stock_data = pd.DataFrame(list(queryset.values()))
#
#     if stock_data.empty:
#         return {
#             'status': 'error',
#             'message': 'No data found for the specified criteria'
#         }
#
#     # Check for missing values only
#     missing_values_check = check_missing_values(stock_data)
#
#     # Get OpenAI insights
#     ai_insights = get_openai_insights(stock_data, missing_values_check)
#
#     return {
#         'status': 'success',
#         'data_stats': {
#             'record_count': len(stock_data),
#             'date_range': {
#                 'start': start_date.isoformat(),
#                 'end': end_date.isoformat()
#             },
#             'unique_tickers': stock_data['ticker'].nunique(),
#         },
#         'missing_values_check': missing_values_check,
#         'ai_insights': ai_insights
#     }
#
# def check_missing_values(df):
#     """
#     Check for missing values in the DataFrame.
#
#     Args:
#         df (DataFrame): The stock data
#
#     Returns:
#         dict: Missing values report
#     """
#     results = {
#         'missing_values': {},
#         'complete_records_percentage': 0
#     }
#
#     # Check for missing values in each column
#     missing_counts = df.isnull().sum().to_dict()
#     results['missing_values'] = {k: int(v) for k, v in missing_counts.items() if v > 0}
#
#     # If no missing values were found, add a message
#     if not results['missing_values']:
#         results['missing_values_message'] = "No missing values found in the data."
#
#     # Calculate percentage of complete records
#     complete_records = df.dropna().shape[0]
#     results['complete_records_percentage'] = round((complete_records / df.shape[0]) * 100, 2)
#
#     # Missing dates in sequence for each ticker
#     ticker_groups = df.groupby('ticker')
#     missing_dates_by_ticker = {}
#
#     for ticker, group in ticker_groups:
#         dates = sorted(group['entry_date'])
#
#         if len(dates) <= 1:
#             continue
#
#         # Create a complete date range
#         date_range = pd.date_range(start=min(dates), end=max(dates), freq='D')
#         missing_dates = [d.date() for d in date_range if d.date() not in dates]
#
#         if missing_dates:
#             missing_dates_by_ticker[ticker] = [date.isoformat() for date in missing_dates]
#
#     if missing_dates_by_ticker:
#         results['missing_dates'] = missing_dates_by_ticker
#
#     return results
# #////////////
# def get_openai_insights(df, missing_values_check):
#     """
#     Get insights from OpenAI about the stock data.
#
#     Args:
#         df (DataFrame): The stock data
#         missing_values_check (dict): Results of missing values check
#
#     Returns:
#         dict: OpenAI insights
#     """
#     try:
#         # Initialize OpenAI client
#         client = OpenAI()
#
#         # Enhanced custom JSON encoder function
#         def custom_encoder(obj):
#             # Handle NumPy numeric types
#             if pd.api.types.is_float_dtype(type(obj)) or isinstance(obj, (np.floating, float)):
#                 return float(obj)
#             elif pd.api.types.is_integer_dtype(type(obj)) or isinstance(obj, (np.integer, int)):
#                 return int(obj)
#             # Handle Decimal types
#             elif isinstance(obj, Decimal):
#                 return float(obj)
#             # Handle date/datetime
#             elif isinstance(obj, (datetime.date, datetime.datetime, pd.Timestamp)):
#                 return obj.isoformat()
#             # Handle pandas NA/null values
#             elif pd.isna(obj):
#                 return None
#             # Handle NumPy array-like objects
#             elif isinstance(obj, (np.ndarray, pd.Series)):
#                 return obj.tolist()
#             # Handle other non-serializable objects
#             raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")
#
#         # Prepare data summary for OpenAI
#         data_summary = {
#             'ticker_count': int(df['ticker'].nunique()),  # Ensure native Python type
#             'unique_tickers': df['ticker'].unique().tolist(),
#             'date_range': {
#                 'start': custom_encoder(df['entry_date'].min()),
#                 'end': custom_encoder(df['entry_date'].max())
#             },
#             'record_count': int(len(df)),  # Ensure native Python type
#             'missing_values_check': missing_values_check,
#             'sample_data': df.head(5).apply(lambda x: x.map(custom_encoder) if pd.api.types.is_numeric_dtype(x) else x)
#                 .to_dict(orient='records') if not df.empty else []
#         }
#
#         # Calculate summary stats by ticker with type conversion
#         summary_stats = {}
#         for ticker in df['ticker'].unique():
#             ticker_data = df[df['ticker'] == ticker]
#             if not ticker_data.empty:
#                 summary_stats[ticker] = {
#                     'daily_value': {
#                         'mean': custom_encoder(ticker_data['daily_value'].mean()),
#                         'min': custom_encoder(ticker_data['daily_value'].min()),
#                         'max': custom_encoder(ticker_data['daily_value'].max())
#                     },
#                     'target_value': {
#                         'mean': custom_encoder(ticker_data['target_value'].mean()),
#                         'min': custom_encoder(ticker_data['target_value'].min()),
#                         'max': custom_encoder(ticker_data['target_value'].max())
#                     }
#                 }
#
#         data_summary['summary_stats_by_ticker'] = summary_stats
#
#         # Create a prompt for OpenAI
#         prompt = f"""
#         You are a data quality expert and financial analyst. Analyze the following stock data and provide key insights:
#
#         DATA SUMMARY:
#         {json.dumps(data_summary, indent=2, default=custom_encoder)}
#
#         Provide:
#         1. Data quality assessment: Focus on missing values and their potential impact.
#         2. Data insights: Provide 3-5 key insights about the stock performance.
#         3. Recommendations: Suggest any actions to improve data completeness.
#
#         Format your response as JSON with these keys: "quality_assessment", "insights", "recommendations".
#         """
#
#         # Make request to OpenAI
#         response = client.chat.completions.create(
# 