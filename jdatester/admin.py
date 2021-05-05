from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Student, Course, TestModel, Book, Author, jdatesterBalanceSheetModel, jdatesterCompanyModel, jdatesterLineModel, jdatesterLinkModel
from .models import Employee, Blog

admin.site.register(Blog)
#admin.site.register(Course)
admin.site.register(TestModel)
admin.site.register(Book)
admin.site.register(Author)


admin.site.register(jdatesterBalanceSheetModel)
admin.site.register(jdatesterCompanyModel)
admin.site.register(jdatesterLineModel)
admin.site.register(jdatesterLinkModel)





@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    pass