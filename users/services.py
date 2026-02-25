import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name, description=None):
    try:
        product = stripe.Product.create(
            name=name,
            description=description or '',
        )
        return product
    except stripe.error.StripeError as e:
        raise Exception(f'Ошибка создания продукта в Stripe: {str(e)}')


def create_stripe_price(product_id, amount, currency='usd'):
    try:
        price = stripe.Price.create(
            product=product_id,
            unit_amount=int(amount * 100),
            currency=currency,
        )
        return price
    except stripe.error.StripeError as e:
        raise Exception(f'Ошибка создания цены в Stripe: {str(e)}')


def create_stripe_session(price_id, success_url, cancel_url):
    try:
        session = stripe.checkout.Session.create(
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
    except stripe.error.StripeError as e:
        raise Exception(f'Ошибка создания сессии в Stripe: {str(e)}')


def retrieve_stripe_session(session_id):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.StripeError as e:
        raise Exception(f'Ошибка получения сессии из Stripe: {str(e)}')