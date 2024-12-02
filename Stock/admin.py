from django.contrib import admin
from .models import ProductCategory, Product, StockEntry, Distribution, StockCheck
from .forms import StockCheckForm


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity_in_stock')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(StockEntry)
class StockEntryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_added', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('product__name',)

@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('club', 'product', 'quantity_distributed', 'date_distributed')
    list_filter = ('club', 'date_distributed')
    search_fields = ('product__name', 'club__name')








import logging

logger = logging.getLogger(__name__)



@admin.register(StockCheck)
class StockCheckAdmin(admin.ModelAdmin):
    list_display = ('distribution', 'confirmed_by', 'confirmed_at', 'remarks')
    search_fields = ('distribution__product__name', 'confirmed_by__username')

    form = StockCheckForm

    
    def get_form(self, request, obj=None, **kwargs):
        """
        Pass the request object to the form during initialization.
        """
        #form = super().get_form(request, obj, **kwargs)
        #form.request = request  # Add the request to the form
        #return form


        form_class = super().get_form(request, obj, **kwargs)

        class RequestInjectedForm(form_class):
            def __init__(self, *args, **kwargs):
                kwargs['request'] = request  # Pass the request object
                super().__init__(*args, **kwargs)

        return RequestInjectedForm

    def get_queryset(self, request):
        """
        Limit objects displayed in the admin based on user profile (optional).
        """
        qs = super().get_queryset(request)
        if hasattr(request.user, 'userprofile') and request.user.userprofile.club:
            return qs.filter(distribution__club=request.user.userprofile.club)
        return qs

