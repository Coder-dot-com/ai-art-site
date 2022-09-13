from django.apps import AppConfig


class EmailMarketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'email_marketing'

    # add this
    def ready(self):
        import email_marketing.signals  

