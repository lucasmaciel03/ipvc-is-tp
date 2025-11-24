from django.apps import AppConfig


class CsvProcessorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.csv_processor'
    verbose_name = 'CSV Processor'
