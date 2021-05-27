from django.db import models
from django.conf import settings
#User = settings.AUTH_USER_MODEL
from django.contrib.auth.models import User # new
import os



# ///////////////////////////////// PublicationCompanyModel /////////////////////////////////

class PublicationCompanyModel(models.Model):
    company_name = models.CharField(max_length=200, blank=False, null=False, unique=True)

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name_plural = 'PublicationCompanyModel'


# ///////////////////////////////// PublicationModel /////////////////////////////////
class PublicationModel(models.Model):
    CATEGORY_CHOICES = (
        ('Models', 'Models'),
        ('Newsletters', 'Newsletters'),
        ('Commentaries', 'Commentaries'),
        ('Reports', 'Reports'),
    )
    TYPE_CHOICES = (
        ('', 'Type'),
        ('Valuation Models', 'Valuation Models'),
        ('Daily Market Briefing', 'Daily Market Briefing'),
        ('Weekly comments', 'Weekly comments'),
        ('Quarterly Results', 'Quarterly Results'),
        ('Half Year Results', 'Half Year Results'),
        ('Annual Results', 'Annual Results'),
        ('Annual Shareholder Meeting', 'Annual Shareholder Meeting'),
        ('IPO Analysis', 'IPO Analysis'),
        ('Research Notes', 'Research Notes'),
        ('Sector Reports', 'Sector Reports'),
        ('Strategic Reports', 'Strategic Reports'),
        ('Economic Notes', 'Economic Notes'),
        ('Investor Conference', 'Investor Conference')
    )

    #author = models.CharField(max_length=100, blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE) # new
    publication_date = models.DateField(blank=False, null=False)
    research_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, null=False, blank=False)
    research_type = models.CharField(max_length=100, choices=TYPE_CHOICES, null=False, blank=False)
    subject = models.CharField(max_length=150)
    publication_desc = models.CharField(max_length=250)
    file_name = models.FileField(upload_to='publications/%Y/%m/') #%Y/%m/%d
    #tmp_pdf_file = models.FileField(upload_to='publications/%Y/%m/', null=True, blank=True)  # %Y/%m/%d  this will hold watermarked pdf files
    uploaded_at = models.DateTimeField(auto_now_add=True)
    visible_flag = models.BooleanField(default=True)
    edited_by = models.CharField(max_length=100, blank=True, null=True)
    company = models.ForeignKey(PublicationCompanyModel, blank=True, null=True, on_delete=models.CASCADE)
    #publication_date = models.DateField(auto_now_add=True, blank=False, null=False)


    def __str__(self):
        return self.subject

    def delete(self, *args, **kwargs):
        self.file_name.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'PublicationModel'


class PubTempModel(models.Model):
    watermark_pdf = models.FileField(upload_to='publications/%Y/%m/')

    def __str__(self):
        return self.watermark_pdf
