from django.db import models


class IndexModel(models.Model):
    index = models.CharField(max_length=12, blank=False, null=False)

    def __str__(self):
        return self.index

    class Meta:
        verbose_name_plural = 'IndexModel'


class IndexPriceModel(models.Model):
    index_date = models.DateTimeField(blank=False, null=False)
    index = models.ForeignKey(IndexModel, on_delete=models.CASCADE, null=False, blank=False)
    value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.index

    class Meta:
        verbose_name_plural = 'IndexPriceModel'



# class IndexPriceModel(models.Model):
#     index_date = models.DateTimeField(blank=False, null=False)
#     index = models.CharField(max_length=12, blank=False, null=False)
#     value = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
#
#     #def __str(self):
#     #    return f"{self.index} quoted at {self.value} as of {self.index_date}"
#
#     def __str__(self):
#         return self.index
#
#     class Meta:
#         verbose_name_plural = 'IndexPriceModel'


class SecurityModel(models.Model):
    ticker = models.CharField(max_length=12, blank=False, null=False)
    isin = models.CharField(max_length=20, blank=False, null=False)
    name = models.CharField(max_length=200, blank=False, null=False)

    #def __str(self):
    #    return f"{self.ticker} - {self.name}"

    def __str__(self):
        return self.ticker

    class Meta:
        verbose_name_plural = 'SecurityModel'


class SecurityPriceModel(models.Model):
    security = models.ForeignKey(SecurityModel, on_delete=models.CASCADE, null=False, blank=False)
    security_date = models.DateTimeField(blank=False, null=False)
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    open = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    close = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    high = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    low = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ask = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    trans_total = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    volume = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    trans_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    #def __str(self):
    #    return f"{self.security} - {self.avg_price} - {self.security_date} - {self.security_date}"


    def __str__(self):
        #return f"{self.security} - {self.security_date}"
        return self.security.ticker

    class Meta:
        verbose_name_plural = 'SecurityPriceModel'
