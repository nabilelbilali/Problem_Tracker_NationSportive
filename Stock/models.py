
from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name="products")
    quantity_in_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.quantity_in_stock})"


class StockEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="entries")
    quantity_added = models.PositiveIntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Update product stock
        self.product.quantity_in_stock += self.quantity_added
        self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_added} of {self.product.name} added on {self.date_added}"



class Distribution(models.Model):
    club = models.ForeignKey('clubs.Club', on_delete=models.CASCADE, related_name="distributions")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="distributions")
    quantity_distributed = models.PositiveIntegerField()
    date_distributed = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Reduce product stock
        if self.quantity_distributed > self.product.quantity_in_stock:
            raise ValueError("Not enough stock available")
        self.product.quantity_in_stock -= self.quantity_distributed
        self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity_distributed} of {self.product.name} sent to {self.club.name} on {self.date_distributed}"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # If the user is a superuser, show all distributions
        if request.user.is_superuser:
            return queryset

        # Otherwise, filter by the club associated with the user's profile
        if hasattr(request.user, 'profile') and request.user.profile.club:
            return queryset.filter(club=request.user.profile.club)

        # If the user has no club, show nothing
        return queryset.none()


def has_view_permission(self, request, obj=None):
    if request.user.is_superuser:
        return True

    # Allow access only if the user is associated with a club
    return hasattr(request.user, 'profile') and request.user.profile.club is not None



class StockCheck(models.Model):
    distribution = models.OneToOneField(Distribution, on_delete=models.CASCADE, related_name="stock_check")
    confirmed_by = models.ForeignKey('clubs.UserProfile', on_delete=models.CASCADE)
    confirmed_at = models.DateTimeField()
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Confirmed {self.distribution} by {self.confirmed_by.username}"


   