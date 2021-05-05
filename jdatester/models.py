from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.CharField(max_length=30)
    student = models.ManyToManyField(Student)

    def __str__(self):
        return self.name



class Author(models.Model):
   name = models.CharField(max_length=100)

   def __str__(self):
       return self.name

class Book(models.Model):
   title = models.CharField(max_length=100)
   author = models.ForeignKey(Author, on_delete=models.CASCADE)


   def __str__(self):
       return self.title



class TestModel(models.Model):
    x = models.FloatField(default=0.00)
    y = models.FloatField(default=0.00)
    computed =  models.FloatField(default=0.00)

    class Meta:
        verbose_name_plural ='TestModel'


    def get_computed(self):
        result =int(self.x) + int(self.y)
        return result

    def save(self, *args, **kwargs):
        self.computed=self.get_computed()
        super(TestModel, self).save(*args, **kwargs)
    #
    # def save(self, *args, **kwargs):
    #     self.computed = self.get_computed()
    #     super(TestModel, self).save(*args, **kwargs)


class jdatesterCompanyModel(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural ='jdatesterCompanyModel'


class jdatesterLineModel(models.Model):
    lbl = models.CharField(max_length=100)

    def __str__(self):
        return self.lbl

    class Meta:
        verbose_name_plural ='jdatesterLineModel'


class jdatesterBalanceSheetModel(models.Model):
    company = models.ForeignKey(jdatesterCompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    lbl     = models.ForeignKey(jdatesterLineModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)
    brut = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)


    def __str__(self):
        return f"{self.company} - {self.entry_date} - {self.lbl}"

    class Meta:
        verbose_name_plural ='jdatesterBalanceSheetModel'
        # models.UniqueConstraint(fields=['entry_date', 'lbl'], name='unique_entry_date_line')
        # #unique_together = ("entry_date", "lbl")


class jdatesterLinkModel(models.Model):
    company = models.ForeignKey(jdatesterCompanyModel, on_delete=models.CASCADE, null=False, blank=False)
    #lbl = models.ForeignKey(jdatesterLineModel, on_delete=models.CASCADE, null=False, blank=False)
    entry_date  = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False)

    brut_1 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    brut_2 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    amort_1 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    amort_2 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    net_1 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)
    net_2 = models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.company}  - {self.entry_date}"

    class Meta:
        verbose_name_plural ='jdatesterLinkModel'



class Employee(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(blank=True)
    day_started = models.DateField()
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.first_name


class UploadExcelModel(models.Model):
    #first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=60)
    #email = models.EmailField(blank=True)
    #day_started = models.DateField()
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.last_name


class IndexPriceModel(models.Model):
    index_date = models.DateTimeField(blank=False, null=False)
    index = models.CharField(max_length=10, blank=False, null=False)
    value =  models.DecimalField(default=0.00, max_digits=18, decimal_places=2, blank=True, null=True)

    #def __str(self):
    #    return f"{self.index} quoted at {self.value} as of {self.index_date}"

    def __str__(self):
        return self.index_date

    class Meta:
        verbose_name_plural = 'IndexPriceModel'


class SecurityModel(models.Model):
    ticker = models.CharField(max_length=12, blank=False, null=False)
    isin = models.CharField(max_length=12, blank=False, null=False)
    name = models.CharField(max_length=200, blank=False, null=False)

    def __str(self):
        return f"{self.ticker} - {self.name}"


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

    def __str(self):
        return f"{self.security__ticker} - {self.security_date}"
        #return f"{self.security} - {self.avg_price} - {self.security_date}"





class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    name = models.CharField(max_length=150)

    class Meta():
        app_label = "jdatester" #"permissions"
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        permissions = [('can_edit_team', 'Can edit team'),]



class Blog(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()

    def __str(self):
        return self.title
