from django.urls import path
from . import views,api
from django.views.generic import TemplateView

urlpatterns = [
    path('view/',views.income_page,name="income"),
    path('add-income/',views.add_income,name="add_income"),
    path('add-source/',views.add_income_source,name="add_income_source"),
    path('delete-income-source/<int:id>/',views.delete_income_source,name="delete_income_source"),
    path('edit-income/<int:id>/',views.edit_income,name="edit_income"),
    path('delete-income/<int:id>/',views.delete_income,name="delete_income"),
    path('income-summary-data',api.income_summary,name="income_summary_data"),
    path('income-summary/',TemplateView.as_view(template_name="income_app/income_summary.html"),name="income_summary"),
    path('download-excel/<str:filter_by>',views.download_as_excel,name = 'income_download_as_excel'),
]