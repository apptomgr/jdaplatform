from django.contrib import admin
from .models import PublicationModel, PublicationCompanyModel


admin.site.register(PublicationModel)
admin.site.register(PublicationCompanyModel)