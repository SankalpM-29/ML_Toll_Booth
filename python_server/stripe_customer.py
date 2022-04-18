import stripe
from fastapi import FastAPI
stripe.api_key = ""

### Stripe accepts balance in terms of "paise" for Indian currency

car_class_types = {'small': 20, 'medium': 40, 'large': 70} # values in rupees

app = FastAPI()

@app.post("/stripe_create_customer")
async def get_body(customer_stripe_id: str, initial_balance: int):

    # initial_balance = enter value in rupees
    customer_stripe_id = customer_stripe_id.replace(" ", "") # remove spaces in rfid tag ID

    customer = stripe.Customer.create(
    id = customer_stripe_id,
    description = customer_stripe_id,    # needed to identify customers on dashboard
    balance = initial_balance * 100     # converting rupees to paise for stripe API
    )

    return customer


@app.post("/stripe_update_customer")
async def get_body(customer_stripe_id: str, car_class: str):

    customer_stripe_id = customer_stripe_id.replace(" ", "") # remove spaces in rfid tag ID
 
    customer_data = stripe.Customer.retrieve(customer_stripe_id)

    existing_balance = customer_data.to_dict()['balance']

    updated_balance = (existing_balance/100) - car_class_types[car_class] # converting existing paise value to rupees and then subtracting toll

    customer = stripe.Customer.modify(
    customer_stripe_id,
    balance = int(updated_balance * 100),    # converting rupees to paise for stripe API and also into to integer value
    )

    return customer







