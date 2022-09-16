from create_design_buy.tasks import order_placed_email
from ..models import Order


def post_payment_success(payment_intent):
    order = Order.objects.get(payment_intent_id=payment_intent)
    order.status = "paid"
    order.save()
    order_placed_email.delay(payment_intent)