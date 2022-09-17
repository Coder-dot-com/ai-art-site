from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from emails.models import UserEmail
from .tasks import delete_email_with_sendinblue, sync_email_with_sendinblue

from subscriptions.models import UserPaymentStatus


@receiver(post_save, sender=UserEmail, dispatch_uid='sync_email_to_sib')
def save_email(sender, instance, created, **kwargs):
    user_email_obj = instance
    if user_email_obj.promo_consent:
        sync_email_with_sendinblue.delay(user_email_obj.email)
    #Delay celery task which syncs with SIB/checks if in SIB if not creates

@receiver(pre_delete, sender=UserEmail, dispatch_uid='delete_email_to_sib')
def delete_email(sender, instance, **kwargs):
    user_email_obj = instance
    if user_email_obj.promo_consent:
        delete_email_with_sendinblue.delay(user_email_obj.email)   