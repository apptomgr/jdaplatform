from django.shortcuts import render, redirect
from .forms import IndexForm, UploadExcelForm, SecurityFilterForm
from .models import IndexModel, IndexPriceModel, SecurityModel, SecurityPriceModel
import xlrd
from datetime import datetime
import pytz
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts .decorators import allowed_users


def get_user_grp(request):
    grp = None
    if request.user.groups.all():
        grp = request.user.groups.all()[0].name
    return grp

@login_required
def jdaanalyticsapp_home(request):

    grp = get_user_grp(request)
    print(f"22 - user_grp: {grp}")
    context = {'user_grp': grp}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_home.html', context)


# //////////////////////////////////////////////// jdaanalyticsapp_upload_form /////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
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
                    #print(f"idx:{idx} - i: {i} - cols[0]: {cols[0]} - cols[7]: {type(cols[7])}")

                # check if datetime exists in DB/ Opt1: delete and reload Opt2:

                if IndexPriceModel.objects.filter(index_date = dt_obj):
                    messages.info(request, f"Market data as of {dt_obj} already loaded")
                else:
                    # get index info & save it to DB only if new indexes
                    for i in range(6, 15):  # index price info in spreadsheet starting from row 6 to row 15th
                        cols = sheet.row_values(i)
                        #check if index not in IndexModel tbl then save it else skip it
                        if not IndexModel.objects.filter(index=cols[0]):
                            IndexModel.objects.create(index=cols[0])
                            #IndexPriceModel.objects.create(index_date=dt_obj, index=cols[0], value=cols[1])

                    # get indexPrice info & save it to DB base on existing indexes
                    for i in range(6, 15):  # index price info in spreadsheet starting from row 6 to row 15th
                        cols = sheet.row_values(i)
                        idx = IndexModel.objects.get(index=cols[0])

                        if idx: #indexPriceModel vals based on existing indexes
                            IndexPriceModel.objects.create(index_date=dt_obj, index=idx, value=cols[1])
                            #print(f"IndexPriceModel.objects.create(index_date={dt_obj}, index={idx}, value={cols[1]})")
                        else: # save based on non-existing indexes
                            IndexPriceModel.objects.create(index_date=dt_obj, index=cols[0], value=cols[1])
                            #print(f"IndexPriceModel.objects.create(index_date={dt_obj}, index=cols{cols[0]}, value={cols[1]})")

                    # get Security info & save it to DB only for new Securities from row 18 through the end of the page
                    for i in range(18, nbr_rows):  # security info index price info in spreadsheet
                         cols =sheet.row_values(i)
                         # check if sec not in SecurityModel tbl then save it else skip it
                         if not SecurityModel.objects.filter(ticker=cols[0], isin=cols[1], name=cols[2]):
                             SecurityModel.objects.create(ticker=cols[0], isin=cols[1], name=cols[2])
                             print(f"SecurityModel.objects.create(ticker={cols[0]}, isin={cols[1]}, name={cols[2]})")

                    # get SecurityPriceModel vals based on existing securities
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

    grp = get_user_grp(request)
    context = {'user_grp': grp,'form':form}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_upload_form.html', context)



@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
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

    grp = get_user_grp(request)
    context = {'user_grp': grp,'filterForm':filterForm, 'index':index, 'security_price':security_price, 'rpt_date':now}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)


#/////////////////////// jdaanalyticsapp_sec_filter /////////////////////
@login_required
@allowed_users(allowed_roles=['admins', 'managers','staffs'])
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

    grp = get_user_grp(request)
    context = {'user_grp': grp,'filterForm':filterForm,'index': index, 'security_price': security_price, 'rpt_date': now}
    return render(request, 'jdaanalyticsapp/jdaanalyticsapp_rpt.html', context)

