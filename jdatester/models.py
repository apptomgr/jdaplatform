from django.db import models


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

