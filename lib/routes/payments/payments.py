import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Payment
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
async def create_new_payment(access_token: str, session_id: int, sw_id_list: list, currency: str = "GBP",
                             db=Depends(data_b.connection)):
    """Create new payment for session. Amount calculated from every price of service session work (sw_id_list) """
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

    ss_work_data = await conn.get_ss_work_list_by_set(ss_work_id=sw_id_list, db=db)
    amount = 0
    for one in ss_work_data:
        amount += one["price"]

    payment_intent = create_payment_stripe(amount)
    pay_data = await conn.create_payment(db=db, user_id=user_id, session_id=session_id, amount=amount,
                                         session_work_id=sw_id_list,currency=currency, intent=payment_intent)
    payment: Payment = Payment.parse_obj(pay_data[0])
    return JSONResponse(content={"ok": True,
                                 "payment": payment.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/payment', tags=['Payment'], responses=get_user_res)
async def get_payments_list(access_token: str, payment_id: int = 0, session_id: int = 0, db=Depends(data_b.connection)):
    """Get """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    if session_id != 0:
        pay_data = await conn.read_data(db=db, id_name="session_id", id_data=session_id, table='payments')
    elif payment_id != 0:
        pay_data = await conn.read_data(db=db, id_name="pay_id", id_data=payment_id, table='payments')
    else:
        return JSONResponse(content={
            "ok": False,
            "description": "Wrong session_id and payment_id. Only one of them should be 0",
        },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    pay_list = []
    for one in pay_data:
        payment: Payment = Payment.parse_obj(one)
        pay_list.append(payment.dict())
    return JSONResponse(content={"ok": True,
                                 "payment_list": pay_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/payment_status', tags=['Payment'], responses=get_user_res)
async def get_payments_list(access_token: str, payment_id: int = 0, db=Depends(data_b.connection)):
    """Get """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    pay_data = await conn.read_data(db=db, id_name="pay_id", id_data=payment_id, table='payments')
    res = stripe.PaymentIntent.confirm(pay_data[0]["intent"])
    return JSONResponse(content={"ok": True,
                                 "status": res.status,
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

