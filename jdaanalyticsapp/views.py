from django.shortcuts import render, redirect
from .forms import IndexForm, UploadExcelForm, SecurityFilterForm
from .models import IndexPriceModel, SecurityModel, SecurityPriceModel
import xlrd
from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts .decorators import allowed_users


@login_required
def jdaanalyticsapp_home(request):
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_home.html')


# //////////////////////////////////////////////// jdaanalyticsapp_upload_form /////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'staffs'])
def jdaanalyticsapp_upload_form(request):
    if request.method == 'POST':
        form = IndexForm(request.POST, request.FILES)
        if form.is_valid():
            wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['excel'].read())  # The key point is here
            sheet = wb.sheets()[0]
            nbr_rows = sheet.nrows
            nbr_cols = sheet.ncols

            # print(f"nbr_rows: {nbr_rows} - nbr_cols: {nbr_cols}")
            # col_0_val=sheet.row_values(0, start_colx=0, end_colx=1)
            col_0_val = sheet.cell(0,0).value
            if col_0_val == "Liste des cours":  # check if it's the right file
                # get file datetime
                date_cell = sheet.cell(3, 1)
                dt = xlrd.xldate_as_tuple(date_cell.value, wb.datemode)
                dt_obj = datetime(dt[0], dt[1], dt[2], dt[3], dt[4], dt[5], tzinfo=pytz.UTC)

                for idx, i in enumerate(range(18, nbr_rows), 0):
                    cols = sheet.row_values(i)
                    print(f"idx:{idx} - i: {i} - cols[0]: {cols[0]} - cols[7]: {type(cols[7])}")

                # print(f"487: {dt_obj}")
                # check if datetime exists in DB/ Opt1: delete and reload Opt2:
                if IndexPriceModel.objects.filter(index_date = dt_obj):
                    messages.info(request, f"Market data as of {dt_obj} already loaded")
                else:
                    # get index info save it to DB
                    for i in range(6, 15): # index price info in spreadsheet starting from row 6 to row 15th
                        cols = sheet.row_values(i)
                        IndexPriceModel.objects.create(index_date=dt_obj, index=cols[0], value=cols[1])

                    #get security info
                    for i in range(18, nbr_rows): # security info
                        cols =sheet.row_values(i)
                        SecurityModel.objects.create(ticker=cols[0], isin=cols[1], name=cols[2])

                    #get SecurityPriceModel info
                    for idx, i in enumerate(range(18, nbr_rows), 0):
                        cols = sheet.row_values(i)

                        if isinstance(cols[7], str):
                            cols[7]=None
                        if isinstance(cols[10], str):
                            cols[10]=None
                        if isinstance(cols[11], str):
                            cols[11]=None
                        if isinstance(cols[13], str):
                            cols[13]=None
                        if isinstance(cols[14], str):
                            cols[14]=None
                        if isinstance(cols[15], str):
                            cols[15]=None
                        if isinstance(cols[16], str):
                            cols[16]=None
                        if isinstance(cols[17], str):
                            cols[17]=None
                        if isinstance(cols[18], str):
                            cols[18]=None
                        if isinstance(cols[19], str):
                            cols[19]=None
                        #print(f"idx:{idx} - i: {i} - cols[0]: {cols[0]} - cols[7]:{cols[7]} type: {type(cols[7])}")
                        sec_id =SecurityModel.objects.all()[idx].id
                        SecurityPriceModel.objects.create(security_id=sec_id, security_date=dt_obj, avg_price=cols[7], open=cols[10], close=cols[11], high=cols[13], low=cols[14], ask=cols[15], bid=cols[16], trans_total=cols[17], volume=cols[18], trans_value=cols[19])
            else:
                messages.warning(request, f"Please make sure you loaded the right file with 'Liste des cours'")

            return  redirect('jdaanalyticsapp_rpt')

    else:
        form = UploadExcelForm()

    #index = IndexPriceModel.objects.all()
    #security = SecurityModel.objects.all()
    #security_price = SecurityPriceModel.objects.all()

    context={'form':form}#, 'index':index, 'security':security, 'security_price':security_price}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_upload_form.html', context)

@login_required
def jdaanalyticsapp_rpt(request):
    now = datetime.now()
    if IndexPriceModel.objects.all():
        max_index_dt = IndexPriceModel.objects.latest('index_date').index_date
        index = IndexPriceModel.objects.filter(index_date=max_index_dt)
        security_price = SecurityPriceModel.objects.filter(security_date = max_index_dt)

    else:
        index = IndexPriceModel.objects.all()
        #security = SecurityModel.objects.all()
        security_price = SecurityPriceModel.objects.all()

    filterForm = SecurityFilterForm()
    context={'filterForm':filterForm, 'index':index, 'security_price':security_price, 'rpt_date':now}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)


#/////////////////////// jdaanalyticsapp_sec_filter /////////////////////
@login_required
def jdaanalyticsapp_sec_filter(request):
    now = datetime.now()
    if request.method == 'POST':

        filterForm = SecurityFilterForm(request.POST)

        if filterForm.is_valid():
            security_date = filterForm.cleaned_data['security_date']
            ticker = filterForm.cleaned_data['ticker']
            index = filterForm.cleaned_data['index']

            #print(f"119://// security_date:{security_date} ticker:{ticker} index:{index}  ")

            # build querystring conditions
            if ticker==None and index==None: #all None bring back all index info and sec info based on security_date
                index = IndexPriceModel.objects.filter(index_date=security_date)
                security_price = SecurityPriceModel.objects.filter(security_date=security_date)

                if index and security_price:
                     messages.success(request, f"Found {index.count()}, {security_price.count()} item(s) as of {security_date}")
                     context = {'filterForm': filterForm, 'index': index, 'security_price': security_price, 'rpt_date': now}
                     return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)
                else:
                     messages.warning(request,f"Could not find any items associated with all empty filters")

            elif ticker!=None and index==None: #filter by ticker only based on security_date
                index = IndexPriceModel.objects.filter(index_date=security_date)
                security_price = SecurityPriceModel.objects.filter(security_date=security_date, security__ticker=ticker)

                if index and security_price:
                     messages.success(request, f"Found {index.count()}, {security_price.count()} item(s) as of {security_date}")
                     context = {'filterForm': filterForm, 'index': index, 'security_price': security_price, 'rpt_date': now}
                     return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)
                else:
                     messages.warning(request,f"Could not find any items associated with all empty filters")

            elif ticker==None and index!=None: #filter by index only based on security_date
                index = IndexPriceModel.objects.filter(index_date=security_date, index=index)
                security_price = SecurityPriceModel.objects.filter(security_date=security_date)

                if index and security_price:
                     messages.success(request, f"Found {index.count()}, {security_price.count()} item(s) as of {security_date}")
                     context = {'filterForm': filterForm, 'index': index, 'security_price': security_price, 'rpt_date': now}
                     return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)
                else:
                     messages.warning(request,f"Could not find any items associated with all empty filters")

            elif ticker!=None and index!=None: #filter by both index amd ticker based on security_date
                index = IndexPriceModel.objects.filter(index_date=security_date, index=index)
                security_price = SecurityPriceModel.objects.filter(security_date=security_date, security__ticker=ticker)

                if index and security_price:
                     messages.success(request, f"Found {index.count()}, {security_price.count()} item(s) as of {security_date}")
                     context = {'filterForm': filterForm, 'index': index, 'security_price': security_price, 'rpt_date': now}
                     return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)
                else:
                     messages.warning(request,f"Could not find any items associated with all empty filters")

        #else:
        #    print("147 invalid form")
        #    messages.error(request, filterForm.errors)
        #    print(f"149 form.errors {filterForm.errors} ///////")
        #    return redirect('jdaanalyticsapp_rpt')

    else:
        filterForm =SecurityFilterForm()


    if IndexPriceModel.objects.all():
        max_index_dt = IndexPriceModel.objects.latest('index_date').index_date
        #print(max_index_dt)
        index = IndexPriceModel.objects.filter(index_date=max_index_dt)
        security = SecurityModel.objects.all()
        security_price = SecurityPriceModel.objects.filter(security_date = max_index_dt)
    else:
        index = IndexPriceModel.objects.all()
        security = SecurityModel.objects.all()
        security_price = SecurityPriceModel.objects.all()

    context = {'filterForm':filterForm,'index': index, 'security_price': security_price, 'rpt_date': now}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)

