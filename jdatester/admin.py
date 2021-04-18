from django.contrib import admin
from .models import Student, Course, TestModel, Book, Author, jdatesterBalanceSheetModel, jdatesterCompanyModel, jdatesterLineModel, jdatesterLinkModel

#admin.site.register(Student)
#admin.site.register(Course)
admin.site.register(TestModel)
admin.site.register(Book)
admin.site.register(Author)


admin.site.register(jdatesterBalanceSheetModel)
admin.site.register(jdatesterCompanyModel)
admin.site.register(jdatesterLineModel)
admin.site.register(jdatesterLinkModel)


