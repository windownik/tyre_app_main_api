import datetime
import os
import time
from math import ceil

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib.response_examples import *
from lib.routes.admins.admin_routes import check_admin, on_page
from lib.sql_create_tables import data_b, app
from lib import sql_connect as conn
from lib.db_objects import Payment, User, Worker, Withdrawal, WithdrawalInvoice

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/admin_payment', tags=['Admin payment'], responses=get_user_res)
async def get_payments_list(access_token: str, page: int = 1, contractor_id: int = 0, worker_id: int = 0,
                            session_id: int = 0, client_id: int = 0, db=Depends(data_b.connection)):
    """Get """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    if contractor_id != 0:
        payments_list = await conn.read_data_offset(table='payments', order="pay_id", limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, id_name="contractor_id",
                                                    id_data=contractor_id)
    elif worker_id != 0:
        payments_list = await conn.read_data_offset(table='payments', order="pay_id", limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, id_name="worker_id",
                                                    id_data=worker_id)
    elif client_id != 0:
        payments_list = await conn.read_data_offset(table='payments', order="pay_id", limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, id_name="user_id",
                                                    id_data=client_id)
    elif session_id != 0:
        payments_list = await conn.read_data_offset(table='payments', order="pay_id", limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, id_name="session_id",
                                                    id_data=session_id)
    else:
        payments_list = await conn.read_all_offset(table='payments', order="pay_id", limit=on_page,
                                                   offset=(page - 1) * on_page, db=db)
    payments_count = await conn.read_all_count(table='payments', db=db)
    pay_count = 0
    if not payments_count == False:
        pay_count = payments_count[0][0]
    list_payments = []
    set_users = set()
    set_workers = set()
    for one in payments_list:
        payment: Payment = Payment.parse_obj(one)
        list_payments.append(payment.dict())

        set_workers.add(payment.worker_id)
        set_users.add(payment.user_id)

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
                                 "payment_list": list_payments,
                                 "users": list_user,
                                 "workers": list_workers,
                                 "total_count": pay_count,
                                 "pages": ceil(pay_count / on_page),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/admin_withdrawal', tags=['Admin payment'], responses=get_user_res)
async def get_payments_list(access_token: str, page: int = 1, contractor_id: int = 0, worker_id: int = 0,
                            session_id: int = 0, client_id: int = 0, only_new: bool = False,
                            db=Depends(data_b.connection)):
    """Admin get all withdrawals with few filters"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    if contractor_id != 0:
        wi_data = await conn.read_data_offset(table='withdrawal', order="withdrawal_id DESC", limit=on_page,
                                              offset=(page - 1) * on_page, db=db, id_name="contractor_id",
                                              id_data=contractor_id)
        count = await conn.read_data_count(table='withdrawal', db=db, id_name="contractor_id", id_data=contractor_id)

    elif worker_id != 0:
        wi_data = await conn.read_withdrawal_filter(where_name='worker_id', limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, where_data=worker_id)
        count = await conn.read_withdrawal_count(where_name='worker_id', db=db, where_data=worker_id)

    elif client_id != 0:
        wi_data = await conn.read_withdrawal_filter(where_name='user_id', limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, where_data=client_id)
        count = await conn.read_withdrawal_count(where_name='user_id', db=db, where_data=session_id)
    elif session_id != 0:
        wi_data = await conn.read_withdrawal_filter(where_name='session_id', limit=on_page,
                                                    offset=(page - 1) * on_page, db=db, where_data=session_id)
        count = await conn.read_withdrawal_count(where_name='session_id', db=db, where_data=client_id)

    elif only_new:
        wi_data = await conn.read_data_offset(table='withdrawal', limit=on_page, offset=(page - 1) * on_page, db=db,
                                              id_name="confirm_date", id_data=0, order="withdrawal_id DESC")
        count = await conn.read_data_count(table='withdrawal', db=db, id_name="contractor_id", id_data=contractor_id)
    else:
        wi_data = await conn.read_all_offset(table='withdrawal', db=db, limit=on_page, offset=(page - 1) * on_page,
                                             order="withdrawal_id DESC")
        count = await conn.read_data_count(table='withdrawal', db=db, id_name="contractor_id", id_data=contractor_id)

    wi_list = []
    for one in wi_data:
        withdrawal: Withdrawal = Withdrawal.parse_obj(one)
        wi_list.append(withdrawal.dict())
    if not count:
        count_number = 0
    else:
        count_number = count[0][0]
    return JSONResponse(content={"ok": True,
                                 "total_count": count_number,
                                 "withdrawal_list": wi_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/admin_withdrawal_invoice', tags=['Admin payment'], responses=get_user_res)
async def get_payments_list(access_token: str, page: int = 0, only_new: bool = False, db=Depends(data_b.connection)):
    """Admin get all withdrawals with few filters"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    if only_new:
        wi_data = await conn.read_data_offset(table='withdrawal_invoice', limit=on_page, offset=(page - 1) * on_page,
                                              db=db,
                                              id_name="confirm_date", id_data=0, order="wi_id DESC")
        count = await conn.read_data_count(table='withdrawal_invoice', db=db, id_name="confirm_date", id_data=0)
    else:
        wi_data = await conn.read_all_offset(table='withdrawal_invoice', limit=on_page, offset=(page - 1) * on_page,
                                             order="wi_id DESC", db=db, )
        count = await conn.read_all_count(table='withdrawal_invoice', db=db, )

    wi_list = []
    for one in wi_data:
        withdrawal: WithdrawalInvoice = WithdrawalInvoice.parse_obj(one)
        wi_list.append(await withdrawal.to_json(db=db))
    if not count:
        count_number = 0
    else:
        count_number = count[0][0]
    return JSONResponse(content={"ok": True,
                                 "total_count": count_number,
                                 "pages": ceil(count_number / on_page),
                                 "wi_list": wi_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/admin_confirm_withdrawal', tags=['Admin payment'], responses=get_user_res)
async def admin_confirm_withdrawal_invoice(access_token: str, withdrawal_id: int, db=Depends(data_b.connection)):
    """Admin confirm withdrawal invoice status to confirm"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    wi_data = await conn.read_data(table='withdrawal_invoice', db=db, id_name="wi_id", id_data=withdrawal_id)

    if not wi_data:
        return JSONResponse(content={"ok": False,
                                     "description": "Bad withdrawal_id",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST,
                            headers={'content-type': 'application/json; charset=utf-8'})
    now = datetime.datetime.now()
    await conn.update_inform(db=db, table="withdrawal_invoice", name="confirm_date",
                             data=int(time.mktime(now.timetuple())), id_name="wi_id", id_data=withdrawal_id)
    await conn.update_inform(db=db, table="withdrawal", name="confirm_date",
                             data=int(time.mktime(now.timetuple())), id_name="wi_id", id_data=withdrawal_id)

    await conn.update_inform(db=db, table="withdrawal_invoice", name="admin_user_id", data=res, id_name="wi_id",
                             id_data=withdrawal_id)
    await conn.update_inform(db=db, table="withdrawal", name="admin_user_id", data=res, id_name="wi_id",
                             id_data=withdrawal_id)

    amount = await conn.read_data_sum(db=db, id_name="wi_id", id_data=withdrawal_id, table="withdrawal",
                                                     sum_name='amount')
    amount = int(amount[0][0]) / 100
    await conn.msg_to_push_logs(db=db, creator_id=res, title="Successful withdrawal",
                                short_text=f"Withdrawal of £{amount} confirmed. Thank you for your cooperation.",
                                main_text="0",
                                img_url="0", content_type="text", users_ids=str(wi_data[0]["user_id"]))

    await conn.msg_to_user(db=db, user_id=wi_data[0]["user_id"], title="Successful withdrawal",
                           short_text=f"Withdrawal of £{amount} confirmed. Thank you for your cooperation.",
                           main_text="0",
                           img_url="0", push_type="text", push_msg_id=0, app_type='pro')

    return JSONResponse(content={"ok": True,
                                 "description": "Invoice information was successfully updated.",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
