import os

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
                                 "workers": list_workers
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
async def get_payments_list(access_token: str, page: int = 1, only_new: bool = False, db=Depends(data_b.connection)):
    """Admin get all withdrawals with few filters"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    if only_new:
        wi_data = await conn.read_data_offset(table='withdrawal_invoice', limit=on_page, offset=(page - 1) * on_page, db=db,
                                              id_name="confirm_date", id_data=0, order="wi_id DESC")
        count = await conn.read_data_count(table='withdrawal_invoice', db=db, id_name="confirm_date", id_data=0)
    else:
        wi_data = await conn.read_all_offset(table='withdrawal_invoice', limit=on_page, offset=(page - 1) * on_page,
                                             order="wi_id DESC", db=db, )
        count = await conn.read_all_count(table='withdrawal_invoice', db=db,)

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
                                 "wi_list": wi_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
