from datetime import datetime
from django.utils.dateparse import parse_date
from django.db import models
from dateutil.relativedelta import relativedelta

def get_rpt_range_period(date, rpt_date):
    #print(f"utils5: date:{date} - rpt_date {rpt_date} date.month: {date.month} ")
    lst_range=[]
    if (rpt_date == 'Quarterly'):
        #print(f"utils 11: rpt_date: {rpt_date} date.month: {date.month}")
        if date.month in range(10, 13):  # Q4 range takes 1 month out
            lst_range = [10, 12]
            print(f"utils14: lst_range: {lst_range}")
        elif date.month in range(7, 10):
            #print(f"utils16: rpt_date{rpt_date}")
            lst_range = [7, 9]
        elif date.month in range(4, 7):
            print(f"utils19: rpt_date{rpt_date}")
            lst_range = [4, 6]
        elif date.month in range(1, 4):
            #print(f"utils22: rpt_date{rpt_date}")
            lst_range = [1, 3]
    elif (rpt_date == 'Semi-annually'):
        #print(f'22: rpt_date for Semi {date.month}')
        if date.month in range(1,7):
            #print(f"utils23: date.month {date.month} rpt_date{rpt_date}")
            lst_range = [1, 6]
        elif date.month in range(7, 13):
            #print(f"utils26: rpt_date{rpt_date}")
            lst_range = [7, 12]
    elif (rpt_date == 'Annually'):
        lst_range = [1, 12]
    else:
        rpt_date ='Unknown'
        #print(f"utils: {rpt_date}////////////Ukn rpt_date")
        lst_range =None

    return lst_range

#///////////////// get_publication_period ////////////////////////////
def get_publication_period(date):
    lst_range = []
    #dt= date
    if date.month in range(10, 13):  # Q4 range takes 1 month out
        dt = datetime(date.year, 12, 31).strftime('%Y-%m-%d')
    elif date.month in range(7, 10):
        dt = datetime(date.year, 9, 30).strftime('%Y-%m-%d')
    elif date.month in range(4, 7):
        dt=datetime(date.year, 6, 30).strftime('%Y-%m-%d')
    elif date.month in range(1, 4):
        dt=datetime(date.year, 3, 30).strftime('%Y-%m-%d')

    else:
        rpt_date ='Unknown'
        dt =None

    #print(dt.strftime('%d/%m/%Y'))
    return dt



#///////////////// get_publication_period_old ////////////////////////////
def get_publication_period_old(date):
    lst_range=[]
    if date.month in range(10, 13):  # Q4 range takes 1 month out
        lst_range = [10, 12]
    elif date.month in range(7, 10):
        lst_range = [7, 9]
    elif date.month in range(4, 7):
        lst_range = [4, 6]
    elif date.month in range(1, 4):
        lst_range = [1, 3]
    else:
        rpt_date ='Unknown'
        lst_range =None

    return lst_range



def get_period(date, company_rpt_period):
    period=''
    if company_rpt_period == 'Quarterly':
        if date.month in range(10, 13):  # Q4 range takes 1 month out
            period='Q4'
        elif date.month in range(7, 10):
            period='Q3'
        elif date.month in range(4, 7):
            period='Q2'
        elif date.month in range(1, 4):
            period='Q1'
    elif company_rpt_period == 'Semi-annually':
        if date.month in range(1, 7):   #  S1
            period='S1'
        elif date.month in range(7, 13):   #  S2
            period='S2'

    else:
        period ='DK_Q'

    return period




def jdatester_publication_date(rpt_period):
    publication_date_obj=None
    if rpt_period == 'Q1':
        publication_date_obj = datetime.strptime('2021-03-31', '%Y-%m-%d').date()
    elif rpt_period == 'Q2':
        publication_date_obj = datetime.strptime('2021-06-30', '%Y-%m-%d').date()
    elif rpt_period == 'Q3':
        publication_date_obj = datetime.strptime('2021-09-30', '%Y-%m-%d').date()
    elif rpt_period == 'Q4':
        publication_date_obj = datetime.strptime('2021-12-31', '%Y-%m-%d').date()
    else:
        dt="DK date"
    return publication_date_obj



def jdafinancialsapp_migrate_bal_link_data(lines, link_data, MODELNAME): # add try/catch block

    for idx, i in enumerate(lines,0):
        #print(f"124: {idx} - {i} - {i.id}")

        if idx == 0:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_0, amort=link_data.amort_0, net=link_data.net_0)
        elif idx == 1:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_1, amort=link_data.amort_1, net=link_data.net_1)
        elif idx == 2:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_2, amort=link_data.amort_2, net=link_data.net_2)
        elif idx == 3:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_3, amort=link_data.amort_3, net=link_data.net_3)
        elif idx == 4:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_4, amort=link_data.amort_4, net=link_data.net_4)
        elif idx == 5:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_5, amort=link_data.amort_5, net=link_data.net_5)
        elif idx == 6:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_6, amort=link_data.amort_6, net=link_data.net_6)
        elif idx == 7:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_7, amort=link_data.amort_7, net=link_data.net_7)
        elif idx == 8:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_8, amort=link_data.amort_8, net=link_data.net_8)
        elif idx == 9:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_9, amort=link_data.amort_9, net=link_data.net_9)
        elif idx == 10:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_10, amort=link_data.amort_10, net=link_data.net_10)
        elif idx == 11:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_11, amort=link_data.amort_11, net=link_data.net_11)
        elif idx == 12:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_12, amort=link_data.amort_12, net=link_data.net_12)
        elif idx == 13:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_13, amort=link_data.amort_13, net=link_data.net_13)
        elif idx == 14:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_14, amort=link_data.amort_14, net=link_data.net_14)
        elif idx == 15:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_15, amort=link_data.amort_15, net=link_data.net_15)
        elif idx == 16:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_16, amort=link_data.amort_16, net=link_data.net_16)
        elif idx == 17:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_17, amort=link_data.amort_17, net=link_data.net_17)
        elif idx == 18:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_18, amort=link_data.amort_18, net=link_data.net_18)
        elif idx == 19:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_19, amort=link_data.amort_19, net=link_data.net_19)
        elif idx == 20:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_20, amort=link_data.amort_20, net=link_data.net_20)
        elif idx == 21:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_21, amort=link_data.amort_21, net=link_data.net_21)
        elif idx == 22:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_22, amort=link_data.amort_22, net=link_data.net_22)
        elif idx == 23:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_23, amort=link_data.amort_23, net=link_data.net_23)
        elif idx == 24:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_24, amort=link_data.amort_24, net=link_data.net_24)
        elif idx == 25:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_25, amort=link_data.amort_25, net=link_data.net_25)
        elif idx == 26:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_26, amort=link_data.amort_26, net=link_data.net_26)
        elif idx == 27:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_27, amort=link_data.amort_27, net=link_data.net_27)
        elif idx == 28:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_28, amort=link_data.amort_28, net=link_data.net_28)
        elif idx == 29:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_29, amort=link_data.amort_29, net=link_data.net_29)
        elif idx == 30:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_30, amort=link_data.amort_30, net=link_data.net_30)
        elif idx == 31:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_31, amort=link_data.amort_31, net=link_data.net_31)
        elif idx == 32:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_32, amort=link_data.amort_32, net=link_data.net_32)
        elif idx == 33:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_33, amort=link_data.amort_33, net=link_data.net_33)
        elif idx == 34:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_34, amort=link_data.amort_34, net=link_data.net_34)
        elif idx == 35:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_35, amort=link_data.amort_35, net=link_data.net_35)
        elif idx == 36:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_36, amort=link_data.amort_36, net=link_data.net_36)
        elif idx == 37:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_37, amort=link_data.amort_37, net=link_data.net_37)
        elif idx == 38:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_38, amort=link_data.amort_38, net=link_data.net_38)
        elif idx == 39:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_39, amort=link_data.amort_39, net=link_data.net_39)
        elif idx == 40:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_40, amort=link_data.amort_40, net=link_data.net_40)
        elif idx == 41:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_41, amort=link_data.amort_41, net=link_data.net_41)
        elif idx == 42:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_42, amort=link_data.amort_42, net=link_data.net_42)
        elif idx == 43:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_43, amort=link_data.amort_43, net=link_data.net_43)
        elif idx == 44:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_44, amort=link_data.amort_44, net=link_data.net_44)
        elif idx == 45:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_45, amort=link_data.amort_45, net=link_data.net_45)
        elif idx == 46:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_46, amort=link_data.amort_46, net=link_data.net_46)
        elif idx == 47:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_47, amort=link_data.amort_47, net=link_data.net_47)
        elif idx == 48:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_48, amort=link_data.amort_48, net=link_data.net_48)
        elif idx == 49:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_49, amort=link_data.amort_49, net=link_data.net_49)
        elif idx == 50:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_50, amort=link_data.amort_50, net=link_data.net_50)
        elif idx == 51:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_51, amort=link_data.amort_51, net=link_data.net_51)
        elif idx == 52:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_52, amort=link_data.amort_51, net=link_data.net_42)
        elif idx == 53:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_53, amort=link_data.amort_53, net=link_data.net_53)
        elif idx == 54:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_54, amort=link_data.amort_54, net=link_data.net_54)
        elif idx == 55:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_55, amort=link_data.amort_55, net=link_data.net_55)
        elif idx == 56:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_56, amort=link_data.amort_56, net=link_data.net_56)
        elif idx == 57:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_57, amort=link_data.amort_57, net=link_data.net_57)
        elif idx == 58:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_58, amort=link_data.amort_58, net=link_data.net_58)
        #elif idx == 59:
        #    MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_59, amort=link_data.amort_59, net=link_data.net_59)

        else:
            print(f"{idx} unknow line ID")

    return


def jdafinancialsapp_migrate_inc_link_data(lines, link_data, MODELNAME): # add try/catch block

    for idx, i in enumerate(lines,0):
        #print(f"254: {idx} - {i} - {i.id}")

        if idx == 0:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_0)
        elif idx == 1:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_1)
        elif idx == 2:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_2)
        elif idx == 3:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_3)
        elif idx == 4:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_4)
        elif idx == 5:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_5)
        elif idx == 6:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_6)
        elif idx == 7:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_7)
        elif idx == 8:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_8)
        elif idx == 9:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_9)
        elif idx == 10:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_10)
        elif idx == 11:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_11)
        elif idx == 12:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_12)
        elif idx == 13:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_13)
        elif idx == 14:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_14)
        elif idx == 15:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_15)
        elif idx == 16:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_16)
        elif idx == 17:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_17)
        elif idx == 18:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_18)
        elif idx == 19:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_19)
        elif idx == 20:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_20)
        elif idx == 21:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_21)
        elif idx == 22:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_22)
        elif idx == 23:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_23)
        elif idx == 24:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_24)
        elif idx == 25:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_25)
        elif idx == 26:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_26)
        elif idx == 27:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_27)
        elif idx == 28:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_28)
        elif idx == 29:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_29)
        elif idx == 30:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_30)
        elif idx == 31:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_31)
        elif idx == 32:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_32)
        elif idx == 33:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_33)
        elif idx == 34:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_34)
        elif idx == 35:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_35)
        elif idx == 36:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_36)
        elif idx == 37:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_37)
        elif idx == 38:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_38)
        elif idx == 39:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_39)
        elif idx == 40:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_40)
        elif idx == 41:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_41)
        elif idx == 42:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_42)

        else:
            print(f"{idx} unknow line ID")

    return


def jdafinancialsapp_migrate_inv_acct_link_data(lines, link_data, MODELNAME): # add try/catch block

    for idx, i in enumerate(lines,0):
        #print(f"254: {idx} - {i} - {i.id}")

        if idx == 0:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date, brut=link_data.brut_0, amort=link_data.amort_0)
        elif idx == 1:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_1, amort=link_data.amort_1)
        elif idx == 2:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_2, amort=link_data.amort_2)
        elif idx == 3:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_3, amort=link_data.amort_3)
        elif idx == 4:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_4, amort=link_data.amort_4)
        elif idx == 5:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_5, amort=link_data.amort_5)
        elif idx == 6:
            MODELNAME.objects.create(company_id=link_data.company.id, financial_statement_line_id=i.id, entry_date=link_data.entry_date,brut=link_data.brut_6, amort=link_data.amort_6)

        else:
            print(f"{idx} unknow line ID")

    return





def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)

# ////////////////////// Merge_two_lists ////////////////////////////
def merge_two_lists(list1, list2):
    merge_list_head = [('', 'Issue')]
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    merged_list = merge_list_head + merged_list
    return merged_list

def merge_company_lists(list1, list2):
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
    merged_list = merged_list
    return merged_list
#date = datetime.now()
#print(get_publication_period(date))

#now = datetime.now()
#currentDate = datetime.datetime.strptime('01/08/2015','%d/%m/%Y').date()
#res= datetime.datetime.strptime(get_publication_period(date), '%Y-%m-%d').date()
#print(now)
#date.strftime('%d/%m/%Y')
#x = 7
#if x in range(1,7):
#	print(f'{x} in range (1,7)')
#else:
#    print(f'{x} in {range (1,4)}')

#print(get_rpt_range_period(parse_date('2021-07-01'), 'Semi-annually'))