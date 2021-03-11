from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from expense_app.models import Expense
from income_app.models import Income
from datetime import timedelta
from django.db.models import Sum
from django.http import HttpResponse
import xlwt
from django.utils.timezone import localtime

@login_required(login_url='login')
def dashboard(request):
    today_date_time = localtime()
    week_date_time = today_date_time - timedelta(days=7) 
    start_today_data = today_date_time.replace(hour=0, minute=0, second=0, microsecond=0)
    end_today_data = today_date_time.replace(hour=23, minute=59, second=59, microsecond=999999)
    incomes_today = Income.objects.filter(user=request.user,created_at__range=(start_today_data,end_today_data)).order_by('-created_at')
    expenses_today = Expense.objects.filter(user=request.user,created_at__range=(start_today_data,end_today_data)).order_by('-created_at')
    expenses_month = Expense.objects.filter(user=request.user,created_at__year=today_date_time.year,created_at__month=today_date_time.month)
    expenses_year = Expense.objects.filter(user=request.user,created_at__year=today_date_time.year)
    expenses_week = Expense.objects.filter(user=request.user,created_at__gte=week_date_time)
    spent_month_count = expenses_month.count()
    spent_year_count = expenses_year.count()
    spent_week_count = expenses_week.count()
    spent_month = expenses_month.aggregate(Sum('amount'))
    spend_today = expenses_today.aggregate(Sum('amount'))
    spent_week = expenses_week.aggregate(Sum('amount'))
    spent_year = expenses_year.aggregate(Sum('amount'))
    return render(request,'dashboard.html',{
        'expenses':expenses_today,
        'incomes':incomes_today,
        'spent_today':spend_today['amount__sum'],
        'spent_month':spent_month['amount__sum'],
        'spent_month_count':spent_month_count,
        'spent_year':spent_year['amount__sum'],
        'spent_year_count':spent_year_count,
        'spent_week':spent_week['amount__sum'],
        'spent_week_count':spent_week_count,
    })

@login_required(login_url='login')
def complete_spreadsheet_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Incomes-Expenses-'+ str(request.user.username) + str(localtime())+".xls"
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('All Data')
    row_number = 1
    fontStyle = xlwt.XFStyle()
    fontStyle.font.bold = True
    columns = ['Date','Source','Category','Description','Amount In', 'Amount Out']
    for col_num in range(len(columns)):
        ws.write(row_number,col_num,columns[col_num],fontStyle)
    fontStyle = xlwt.XFStyle()
    incomes = Income.objects.filter(user=request.user).order_by('date')
    expenses = Expense.objects.filter(user=request.user).order_by('date')
    income_list = incomes.values_list('date','source__source','description','amount')
    expense_list = expenses.values_list('date','category__name','description','amount')
    rows = income_list
    for row in rows:
        row_number += 1
        ws.write(row_number,0,str(row[0]),fontStyle)
        ws.write(row_number,1,str(row[1]),fontStyle)
        ws.write(row_number,3,str(row[2]),fontStyle)
        ws.write(row_number,4,str(row[3]),fontStyle)
    row_number += 1
    rows = expense_list
    for row in rows:
        row_number += 1
        ws.write(row_number,0,str(row[0]),fontStyle)
        ws.write(row_number,2,str(row[1]),fontStyle)
        ws.write(row_number,3,str(row[2]),fontStyle)
        ws.write(row_number,5,str(row[3]),fontStyle)
    row_number +=2
    style = xlwt.easyxf('font: colour red, bold True;')
    ws.write(row_number,0,'TOTAL',style)
    ws.write(row_number,6,'Balance',style)
    style = xlwt.easyxf('font: colour black, bold True;')
    income_total = incomes.aggregate(Sum('amount'))['amount__sum']
    expense_total = expenses.aggregate(Sum('amount'))['amount__sum']
    ws.write(row_number,4,str(income_total),style)
    ws.write(row_number,5,str(expense_total),style)
    style = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;''font: colour red, bold True;')
    ws.write(row_number,7,str(income_total - expense_total),style)
    wb.save(response)
    return response