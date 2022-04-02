from functools import lru_cache
import os
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from fastapi import Depends, FastAPI, Request
from twilio.rest import Client
import stripe
from dotenv import load_dotenv

cred = credentials.Certificate('./toll-booth.json')
firebase_admin.initialize_app(cred)

app = FastAPI()
env = load_dotenv()
db = firestore.client()

# stripe config
stripe.api_version = '2020-08-27'
stripe.api_key = os.environ.get('STRIPE_API_KEY')

class Item(BaseModel):
    tag_id: str
    number: int
    plate: str

class Tag(BaseModel):
    tag_id: str

#  route for adding user to the database
@app.post("/add_user")
async def upload(item: Item):

    doc_ref = db.collection(u'cardata').document(item.tag_id)
    doc = doc_ref.get()
    if doc.exists: return {"message": "Aldready Present"}
    doc_ref.set({
        u'tag_id': item.tag_id,
        u'number': item.number,
        u'plate': item.plate,
    })

    return {"message" : "Entry Added"}

# getting the number of a particular user
# @app.post("/get_number")
# async def upload(tag: Tag):

#     db = firestore.client()

#     # Create a reference to the cities collection
#     tag_ref = db.collection(u'cardata')

#     # Create a query against the collection
#     docs = tag_ref.where(u'tag_id', u'==', tag.tag_id).stream()

#     for doc in docs:
#         doc_to_dict = doc.to_dict()
#         number = doc_to_dict['number']

#     print(number)
#     return {"mobile_number" : number}


# send message to a user based on the tag id
@app.post("/send_message")
async def upload(tag: Tag):

    doc_ref = db.collection(u'cardata').document(tag.tag_id)
    doc = doc_ref.get()

    print(doc)

    if doc.exists:
        number = doc.get("number")
        # to = "whatsapp:+91"+str(number)
        to = "+91"+str(number)
        from_="+18449023426"
        client = Client(os.environ.get("ACCOUNT_SID"), os.environ.get("AUTH_TOKEN"))
        client.studio.v2.flows(os.environ.get("FLOW_ID")).executions.create(to=to, from_=from_)
    else: pass

    return { "message" : "send message"}

# stripe payment api
@app.post("/pay")
async def pay():
    # write your stripe code here
    stripe.api_key = os.environ.get('STRIPE_API_KEY')
    customer = stripe.Customer.retrieve('cus_LQSbRmECb2onEY')

    stripe.PaymentIntent.create(
        amount=20,
        currency='inr',
        customer=customer['id'],
        payment_method_types=['customer_balance'],
        payment_method_data={
            "type": "customer_balance",
        },
        payment_method_options={
            "customer_balance": {
                "funding_type": "bank_transfer",
                "bank_transfer": {
                    "type": "jp_bank_transfer",
                },
            },
        },
        confirm=True,
    )
    return

# ??
@app.post("/response")
async def get_body(request: Request):

    print(request.json())
    res = await request.json()
    return res