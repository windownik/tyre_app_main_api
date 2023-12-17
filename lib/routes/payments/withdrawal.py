import os

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse, FileResponse

from lib import sql_connect as conn
from lib.db_objects import Contractor, WithdrawalInvoice, Withdrawal, Payment, User, Worker, SessionWork
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_con_owner_or_admin
from lib.routes.payments.create_pdf import create_file_pdf
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


@app.post(path='/withdrawal', tags=['Payment'], responses=create_payment_res)
async def create_new_payment(access_token: str, contractor_id: int, db=Depends(data_b.connection)):
    """Create new withdrawal for contractor"""

    user_id = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(user_id) != int:
        return user_id
    payments_data = await conn.read_payments_for_withdrawal(db=db, contractor_id=contractor_id)
    if not payments_data:
        return JSONResponse(content={"ok": False, "description": "Haven't payments for withdrawal", }, status_code=400)

    co_data = await conn.read_data(db=db, table="contractor", id_name="contractor_id", id_data=contractor_id)
    co: Contractor = Contractor.parse_obj(co_data[0])

    wi_data = await conn.create_withdrawal_invoice(db=db, contractor_id=contractor_id, user_id=user_id,
                                                   acc_num=co.acc_num, vat_number=co.vat_number, sort_code=co.sort_code,
                                                   post_code=co.post_code, beneficiary_name=co.beneficiary_name)

    wi_invoice: WithdrawalInvoice = WithdrawalInvoice.parse_obj(wi_data[0])
    for one in payments_data:
        _wi_data = await conn.create_withdrawal(db=db, wi_id=wi_invoice.wi_id, amount=one["amount"],
                                                currency=one["currency"], contractor_id=contractor_id,
                                                pay_id=one["pay_id"])
        await conn.update_inform(db=db, table="payments", id_name="pay_id", id_data=one["pay_id"], name="withdrawal_id",
                                 data=_wi_data[0][0])

    return JSONResponse(content={"ok": True,
                                 "wi_invoice": await wi_invoice.to_json(db=db, ),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/wi', tags=['Payment'], responses=create_payment_res)
async def get_withdrawal_invoice(access_token: str, withdrawal_invoice_id: int, db=Depends(data_b.connection)):
    """Get withdrawal invoice with withdrawal list"""

    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    wi_data = await conn.read_data(db=db, table="withdrawal_invoice", id_name="wi_id", id_data=withdrawal_invoice_id)

    user_id = await check_con_owner_or_admin(access_token=access_token, co_id=wi_data[0]["contractor_id"], db=db)
    if type(user_id) != int:
        return user_id

    wi_invoice: WithdrawalInvoice = WithdrawalInvoice.parse_obj(wi_data[0])
    wi_invoice, wi_list = await wi_invoice.to_json_with_withdrawals(db=db, )

    return JSONResponse(content={"ok": True,
                                 "wi_invoice": wi_invoice,
                                 "withdrawal_list": wi_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/payments_of_wi', tags=['Payment'], responses=create_payment_res)
async def get_all_payments_of_withdrawal_invoice(access_token: str, wi_id: int, db=Depends(data_b.connection)):
    """Get withdrawal invoice with withdrawal list"""

    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    wi_data = await conn.read_withdrawal_invoice_payments(db=db, wi_id=wi_id)
    pay_list = []
    set_users = set()
    set_workers = set()
    for one in wi_data:
        payment: Payment = Payment.parse_obj(one)
        set_users.add(payment.user_id)
        set_workers.add(payment.worker_id)
        pay_list.append(payment.dict())
    list_user = []
    if len(set_users) != 0:
        crop_user_list = await conn.get_user_by_set(db=db, set_id=set_users)

        for one in crop_user_list:
            user: User = User.parse_obj(one)
            list_user.append(user.dict())

    list_workers = []
    if len(set_workers) != 0:
        crop_user_list = await conn.get_workers_by_set(db=db, set_id=set_workers)

        for one in crop_user_list:
            worker: Worker = Worker.parse_obj(one)
            list_workers.append(worker.dict())

    return JSONResponse(content={"ok": True,
                                 "payments_list": pay_list,
                                 "users": list_user,
                                 "workers": list_workers,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/withdrawal_all', tags=['Payment'], responses=create_payment_res)
async def get_withdrawal_invoice(access_token: str, worker_id: int = 0, contractor_id: int = 0,
                                 db=Depends(data_b.connection)):
    """Get withdrawal invoice with withdrawal list"""
    if contractor_id != 0:
        user_id = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
        if type(user_id) != int:
            return user_id
        wi_data = await conn.read_data(db=db, table="withdrawal", id_name="contractor_id",
                                       id_data=contractor_id)
    else:
        res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
        if res.status_code != 200:
            return res

        user_id = res.json()['user_id']
        if worker_id != 0:
            user_id = worker_id

        wi_data = await conn.read_worker_withdrawal(db=db, worker_id=user_id)

    wi_list = []
    for one in wi_data:
        withdrawal: Withdrawal = Withdrawal.parse_obj(one)
        wi_list.append(withdrawal.dict())

    return JSONResponse(content={"ok": True,
                                 "withdrawal_list": wi_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/contractor_withdrawal', tags=['Payment'], responses=create_payment_res)
async def get_all_withdrawal_invoice(access_token: str, contractor_id: int = 0,
                                     db=Depends(data_b.connection)):
    """Get withdrawal invoices of one contractor"""
    user_id = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(user_id) != int:
        return user_id
    wi_data = await conn.read_data(db=db, table="withdrawal_invoice", id_name="contractor_id",
                                   id_data=contractor_id, order=" ORDER BY wi_id DESC")

    wi_list = []
    for one in wi_data:
        withdrawal: WithdrawalInvoice = WithdrawalInvoice.parse_obj(one)
        wi_list.append(await withdrawal.to_json(db=db))

    return JSONResponse(content={"ok": True,
                                 "wi_list": wi_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/withdrawal_pdf', tags=['Payment'], responses=create_payment_res)
async def get_all_withdrawal_invoice(access_token: str, wi_id: int, contractor_id: int, db=Depends(data_b.connection)):
    """Get withdrawal invoices of one contractor"""
    user_id = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(user_id) != int:
        return user_id
    co_data = await conn.read_data(db=db, table='contractor', id_data=contractor_id, id_name="contractor_id")
    data = await conn.read_withdrawal_invoice_for_pdf(db=db, wi_id=wi_id)
    ss_w_dict = await get_sessions(db, data)
    create_file_pdf(data=data, invoice_id=wi_id, co_name=co_data[0]['co_name'], address=co_data[0]['address'])

    return FileResponse(path="invoice.pdf", media_type='application/pdf', filename=f"invoice_{wi_id}.pdf")


async def get_sessions(db: Depends, data: tuple) -> dict:
    ss_w_id_list = []
    for one in data:
        ss_w = one["session_work_id"]
        list_ss_w = str(ss_w).split(",")
        for _one in list_ss_w:
            ss_w_id_list.append(_one)

    ss_work_data = await conn.get_ss_work_list_by_set(db=db, ss_work_id=ss_w_id_list)
    ss_w_dict = {}
    for one in ss_work_data:
        session_work: SessionWork = SessionWork.parse_obj(one)
        ss_w_dict[str(session_work.sw_id)] = session_work
    return ss_w_dict
