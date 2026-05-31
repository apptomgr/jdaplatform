from django.db import migrations


def rename_half_year_results(apps, schema_editor):
    PublicationModel = apps.get_model("jdapublicationsapp", "PublicationModel")
    PublicationModel.objects.filter(
        research_type="Half Year Results"
    ).update(research_type="Semi-annual Results")


def reverse_rename(apps, schema_editor):
    PublicationModel = apps.get_model("jdapublicationsapp", "PublicationModel")
    PublicationModel.objects.filter(
        research_type="Semi-annual Results"
    ).update(research_type="Half Year Results")


class Migration(migrations.Migration):

    dependencies = [
        ("jdapublicationsapp", "0018_alter_publicationmodel_research_type"),
    ]

    operations = [
        migrations.RunPython(rename_half_year_results, reverse_code=reverse_rename),
    ]
