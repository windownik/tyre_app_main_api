import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.response_examples import *
from lib.sql_create_tables import data_b, app
import stripe



ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"

str_secret = os.environ.get("STRIPE_SECRET")

stripe.api_key = str_secret


@app.post(path='/payment', tags=['Payment'], responses=get_user_res)
async def create_new_payment(access_token: str, list_items: list, db=Depends(data_b.connection)):
    """Update user information"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     }, status_code=400)
    amount = 1000
    payment_intent = create_payment_stripe(amount)
    return JSONResponse(content={"ok": True,
                                 "amount": amount,
                                 "payment_intent": payment_intent,
                                 'list_items': str(list_items),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


def create_payment_stripe(amount: int) -> str:
    res = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        automatic_payment_methods={"enabled": True},
    )
    return res.client_secret

