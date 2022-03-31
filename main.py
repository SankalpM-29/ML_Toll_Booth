import re
from typing import Optional
from pydantic import BaseModel, NumberNotGeError
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from fastapi import FastAPI, Path, Request
from typing import Optional
from twilio.rest import Client



app = FastAPI()

cred = credentials.Certificate('./toll-booth.json')
firebase_admin.initialize_app(cred)

account_sid = "AC526b5b287c6306a4dc3f6c1e4779f5a8" # Enter your Account SID from twilio.com/console here
auth_token  = "abb60c1549593a21ceecf72a01c44004" # Enter your Auth Token from twilio.com/console here
flow_id = "FW5a469d7b65d21defe74021c8f33c436c"     # Find the Flow ID value from the trigger's REST API URL          # An +E.164 number that we'll be dialing. The unemployment office in my case!
# from_="whatsapp:+18449023426" 
from_="+18449023426" 
        # An +E.164 number that's initiating this execution. This is your Twilio phone number


class Item(BaseModel):
    tag_id: str
    number: int
    plate: str


@app.post("/add_user/")
async def upload(item: Item):

    db = firestore.client()

    doc_ref = db.collection(u'cardata').document()
    doc_ref.set({
        u'tag_id': item.tag_id,
        u'number': item.number,
        u'plate': item.plate,
    })

    return "Entry Added"

@app.post("/get_number/")
async def upload(tag_id: str):

    db = firestore.client()

    # Create a reference to the cities collection
    tag_ref = db.collection(u'cardata')

    # Create a query against the collection
    docs = tag_ref.where(u'tag_id', u'==', tag_id).stream()

    for doc in docs:
        doc_to_dict = doc.to_dict()
        number = doc_to_dict['number']

    print(number)
    return number


@app.post("/send_message/")
async def upload(number: int):


    # to = "whatsapp:+91"+str(number)
    to = "+91"+str(number)
    from_="+18449023426"
    client = Client(account_sid, auth_token)
    client.studio.v2.flows(flow_id).executions.create(to=to, from_=from_)

@app.post("/response/")
async def get_body(request: Request):

    print(request.json())
    return await request.json()
