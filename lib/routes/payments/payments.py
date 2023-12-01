import datetime
import os
import time

import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Payment
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_con_owner_or_admin
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


@app.post(path='/payment', tags=['Payment'], responses=create_payment_res)
async def create_new_payment(access_token: str, session_id: int, sw_id_list: str, currency: str = "GBP",
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
    sw_id_list = sw_id_list.split(", ")
    ss_work_data = await conn.get_ss_work_list_by_set(ss_work_id=sw_id_list, db=db)
    amount = 0
    for one in ss_work_data:
        amount += one["price"]

    pay = create_payment_stripe(amount)
    pay_data = await conn.create_payment(db=db, user_id=user_id, session_id=session_id, amount=amount,
                                         session_work_id=sw_id_list, currency=currency, intent=pay.client_secret,
                                         pay_id=pay.id)

    payment: Payment = Payment.parse_obj(pay_data[0])
    return JSONResponse(content={"ok": True,
                                 "payment": payment.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/payment', tags=['Payment'], responses=get_user_res)
async def get_payments_list(access_token: str, payment_id: int = 0, session_id: int = 0, db=Depends(data_b.connection)):
    """Get payments by payment_id or all payments for services session"""
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


@app.get(path='/payment_withdrawal', tags=['Payment'], responses=get_user_res)
async def get_payments_list_ready_for_withdrawal(access_token: str, contractor_id: int, db=Depends(data_b.connection)):
    """Get payments list in contractor which ready for withdrawal"""
    res = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(res) != int:
        return res

    payments_data = await conn.read_payments_for_withdrawal(db=db, contractor_id=contractor_id)

    pay_list = []
    for one in payments_data:
        payment: Payment = Payment.parse_obj(one)
        pay_list.append(payment.dict())
    return JSONResponse(content={"ok": True,
                                 "payment_list": pay_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/payment_status', tags=['Payment'], responses=get_user_res)
async def get_payments_list(access_token: str, payment_id: int = 0, db=Depends(data_b.connection)):
    """Get payment status"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    pay_data = await conn.read_data(db=db, id_name="pay_id", id_data=payment_id, table='payments')
    res = stripe.PaymentIntent.retrieve(pay_data[0]["stripe_id"])
    if res.status == "succeeded":
        await conn.update_inform(db=db, table="payments", name="status", data="paid", id_name="pay_id",
                                 id_data=payment_id)
        create_date = datetime.datetime.now()
        create_date = int(time.mktime(create_date.timetuple()))
        await conn.update_inform(db=db, table="payments", name="pay_date", data=create_date, id_name="pay_id",
                                 id_data=payment_id)
        await conn.update_inform(db=db, table="service_session", name="status", data="search", id_name="session_id",
                                 id_data=pay_data[0]["session_id"])
    return JSONResponse(content={"ok": True,
                                 "status": res.status,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


def create_payment_stripe(amount: int, ):
    res = stripe.PaymentIntent.create(
        amount=amount,
        currency="gbp",
        automatic_payment_methods={"enabled": True},
    )
    return res
