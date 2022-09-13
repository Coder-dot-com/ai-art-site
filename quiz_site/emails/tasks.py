from django.core.mail import send_mail
from django.template.loader import render_to_string
from decouple import config
from quiz_site.celery import app
from subscriptions.models import UserSubscriptions 

API_KEY = config('SENDBLUE_API_SECRET')
SENDER_SITE_EMAIL = config('SITE_EMAIL')

@app.task
def password_reset_email(user, reset_link):

    # Fix template as total is alreayd converted and show currency and also discount

        #Create email template and send
        #Then handle this link in view below

        message = render_to_string('emails/password_reset_mail.html', {
                    'user': user,
                    'reset_link': reset_link,

                })

        try:

            send_mail(
                subject=f'Reset your password - {user.username}',  #Subject
                message=message, #message
                from_email=f'{SENDER_SITE_EMAIL}', #from
                recipient_list=[user.email], #to
                fail_silently=False,
                html_message=message,
            )
        except Exception as e:
            print(e)






@app.task
def subscription_confirmed_email(subscription_id):
     
    subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
    context = {}

    if not subscription.subscription_confirmation_email_sent:
        print("FINISH LOGIC FOR EMAIL SUBSCRIPTION CONFS")
        context['user_subscription'] = subscription



        message = render_to_string('emails/subscription_confirmed.html', context=context)

        site_email = config('SITE_EMAIL')

        send_mail(
            subject=f'Thank you for your subscription',  
            message=message, 
            from_email=f'{site_email}', 
            recipient_list=[subscription.user_payment_status.user.email], 
            fail_silently=False,
            html_message=message,
        )

        subscription.subscription_confirmation_email_sent = True 
        subscription.save()
    else:
        print("Subscription confirmed Email already sent")


@app.task
def subscription_cancelled(subscription_id, failed_payment=None):
     
    subscription = UserSubscriptions.objects.get(subscription_id=subscription_id)
    context = {}


    context['user_subscription'] = subscription
    
    if failed_payment:
        context['failed_payment'] = True


    message = render_to_string('emails/subscription_cancelled.html', context=context)

    site_email = config('SITE_EMAIL')

    send_mail(
            subject=f'Your subscription was cancelled',  
            message=message, 
            from_email=f'{site_email}', 
            recipient_list=[subscription.user_payment_status.user.email], 
            fail_silently=False,
            html_message=message,
        )

