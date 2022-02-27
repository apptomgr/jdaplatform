from django.contrib import admin
from .models import IndexModel, IndexPriceModel, SecurityPriceModel, SecurityModel, ExchangeModel, StockModel, BondModel
# from .models import Author, Book

admin.site.register(IndexModel)
admin.site.register(IndexPriceModel)
admin.site.register(SecurityPriceModel)
admin.site.register(ExchangeModel)
admin.site.register(SecurityModel)
admin.site.register(StockModel)
admin.site.register(BondModel)


# class BookInLineAdmin(admin.TabularInline):
#     model = Book
#
# class AuthorAdmin(admin.ModelAdmin):
#     inlines = [BookInLineAdmin]
#
# admin.site.register(Author, AuthorAdmin)
