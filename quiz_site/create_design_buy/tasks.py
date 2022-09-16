from quiz_site.celery import app
from create_design_buy.models import Order, OrderProduct
from decouple import config
from django.core.mail import send_mail


API_KEY = config('SENDBLUE_API_SECRET')
SENDER_SITE_EMAIL = config('SITE_EMAIL')

@app.task
def order_placed_email(payment_intent):
        order = Order.objects.get(payment_intent_id=payment_intent)

        message = f"""Thank you, your order has been placed, it should arrive in the next 2-3 weeks.
        or instantly if digital. Your order number is {order.order_number}. Total paid: {order.order_total} {order.currency.currency_code}.
        
        If you have any questions please don't hesitate emailing us.
        """
        recipient = OrderProduct.objects.filter(order=order)[0].design_request.email.email

        if not order.order_conf_email_sent:
            send_mail(
                subject=f'Thank you for your order',  #Subject
                message=message, #message
                from_email=f'{SENDER_SITE_EMAIL}', #from
                recipient_list=[recipient], #to
                fail_silently=False,
            )

        order.order_conf_email_sent = True
        order.save()
