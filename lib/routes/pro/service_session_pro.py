import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import ServiceSession, Payment

from lib import sql_connect as conn
from lib.response_examples import *
from lib.routes.admins.admin_routes import on_page
from lib.routes.pro.auth import check_owner_pro
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/service_session_pro', tags=['Pro Service session'], responses=get_login_res)
async def get_all_service_session_for_pro(access_token: str, contractor_id: int = 0, worker_id: int = 0,
                                          db=Depends(data_b.connection)):
    """Get all service sessions in contractor or made by worker. This route only for contractor's owners"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    if contractor_id != 0:
        check = await check_owner_pro(db=db, worker_id=user_id, contractor_id=contractor_id)
        if not check:
            return JSONResponse(content="Haven't enough rights",
                                status_code=_status.HTTP_400_BAD_REQUEST)
        service_data = await conn.owner_read_ss(db=db, id_name='contractor_id', id_data=contractor_id)
    else:
        service_data = await conn.owner_read_ss(db=db, id_name='worker_id',
                                                id_data=user_id if worker_id == 0 else worker_id)

    list_s_s = []
    for one in service_data:
        session: ServiceSession = ServiceSession.parse_obj(one)
        list_s_s.append(await session.to_json(db=db, session_work_list=[]))

    return JSONResponse(content={"ok": True,
                                 'list_service_session': list_s_s
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/pro_payments_statistic', tags=['Pro Service session'], responses=get_login_res)
async def get_all_service_session_for_pro(access_token: str, contractor_id: int = 0, db=Depends(data_b.connection)):
    """Get worker's payment statistic all payments without withdrawal"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    pay_data_all = await conn.read_worker_payments(db=db, worker_id=user_id, contractor_id=contractor_id)
    pay_list_all = []
    for one in pay_data_all:
        payment: Payment = Payment.parse_obj(one)
        pay_list_all.append(payment.dict())

    return JSONResponse(content={"ok": True,
                                 "payment_list": pay_list_all,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/pro_ss_archive', tags=['Pro Service session'], responses=get_login_res)
async def get_all_service_session_in_archive(access_token: str, page: int = 1, contractor_id: int = 0,
                                             db=Depends(data_b.connection)):
    """Get worker's or contractors service sessions for archive"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    if contractor_id != 0:
        check = await check_owner_pro(db=db, worker_id=user_id, contractor_id=contractor_id)
        if not check:
            return JSONResponse(content={"ok": False, "description": "Haven't enough rights"},
                                status_code=_status.HTTP_400_BAD_REQUEST)

    ss_all = await conn.read_service_session_archive(db=db, worker_id=user_id, offset=(page - 1) * on_page,
                                                     limit=on_page,
                                                     contractor_id=contractor_id)
    total_count = await conn.count_service_session_archive(db=db, worker_id=user_id, contractor_id=contractor_id)
    ss_list_all = []
    for one in ss_all:
        session: ServiceSession = ServiceSession.parse_obj(one)
        ss_list_all.append(await session.to_json(db=db, session_work_list=[]))

    return JSONResponse(content={"ok": True,
                                 "total_count": total_count[0][0],
                                 "list_service_session": ss_list_all,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/pro_session_status', tags=['Pro Service session'], responses=get_login_res)
async def worker_work_in_service_session(access_token: str, session_id: int, worker_lat: float = 0,
                                         worker_long: float = 0,
                                         distant: float = 0,
                                         cancel: bool = False,
                                         delivery: bool = False,
                                         new_bill: bool = False,
                                         start_work: bool = False,
                                         finish_work: bool = False,
                                         in_service_work: bool = False,
                                         db=Depends(data_b.connection)):
    """Worker update status of service session"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    worker_id = res.json()['user_id']
    ss_data = await conn.read_data(db=db, table="service_session", id_data=session_id, id_name="session_id")
    title = "Tire repair session"
    push_user_id = ss_data[0]['client_id']
    app_type = "simple"

    if not ss_data:
        return JSONResponse(content={"ok": False, "description": "Bad session_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    if start_work and not finish_work and not in_service_work and not delivery and not cancel and not new_bill:
        await update_payments(db=db, worker_id=worker_id, session_id=session_id)
        text = "Our technician has started repairing your tire."
        status = "in work"

    elif not start_work and finish_work and not in_service_work and not delivery and not cancel and not new_bill:
        await update_payments(db=db, worker_id=worker_id, session_id=session_id)
        text = "Our specialist has successfully repaired your tire. Thank you for your cooperation."
        status = "success"

    elif not start_work and not finish_work and in_service_work and not delivery and not cancel and not new_bill:
        await update_payments(db=db, worker_id=worker_id, session_id=session_id)
        text = "Your tire repair will be completed at a service center."
        status = "in_service"

    elif not start_work and not finish_work and not in_service_work and delivery and not cancel and not new_bill:
        other_ss = await conn.read_workers_ss(db=db, worker_id=worker_id)
        if other_ss:
            return JSONResponse(content={"ok": False, "description": "Worker not free for new session"},
                                status_code=_status.HTTP_409_CONFLICT)
        await update_payments(db=db, worker_id=worker_id, session_id=session_id)
        await conn.update_start_worker_pos_ss(db=db, distant=distant, long=worker_long, lat=worker_lat,
                                              session_id=session_id)
        text = "Our worker is coming to you to repair your tire."
        status = "delivery"

    elif not start_work and not finish_work and not in_service_work and not delivery and not cancel and new_bill:
        await update_payments(db=db, worker_id=worker_id, session_id=session_id)
        text = "You need to pay an additional invoice in your service session."
        status = "waiting payment"

    elif not start_work and not finish_work and not in_service_work and not delivery and cancel and not new_bill:
        client_id = await conn.read_data(db=db, table="service_session", name="client_id", id_name="session_id",
                                         id_data=session_id)
        if worker_id != client_id[0][0]:
            return JSONResponse(content={"ok": False, "description": "No access rights"},
                                status_code=_status.HTTP_409_CONFLICT)
        text = "The order was canceled by the customer"
        push_user_id = ss_data[0]['worker_id']
        app_type = "pro"
        status = "cancel"
    else:
        return JSONResponse(content={"ok": False, "description": "Bad flags in service session"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.create_push_for_user(db=db, user_id=push_user_id, session_id=session_id, title=title, text=text,
                                    app_type=app_type)
    await conn.update_inform(db=db, table="service_session", id_name="session_id", id_data=session_id, name='status',
                             data=status)
    await conn.update_ss_last_update(db=db, session_id=session_id)
    return JSONResponse(content={"ok": True,
                                 "description": "Successful updating"
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/ss_custom_work', tags=['Pro'], responses=get_login_res)
async def create_service_session_custom_work(access_token: str, session_id: int, work_name: str, price: int,
                                             currency: str = "GBP", db=Depends(data_b.connection)):
    """Worker create custom ss work in session"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return JSONResponse(content=res.json(),
                            status_code=res.status_code)
    worker_id = res.json()['user_id']
    service_data = await conn.read_data(db=db, table='service_session', id_name='session_id', id_data=session_id)
    if not service_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    service_session: ServiceSession = ServiceSession.parse_obj(service_data[0])
    if service_session.worker_id != worker_id:
        return JSONResponse(content={"ok": False,
                                     'description': "No access rights"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.create_ss_work(db=db, session_id=session_id, currency=currency, name_en=work_name, price=price,
                              work_type_id=0, wheel_rr=False, wheel_rl=False,
                              wheel_fl=False, wheel_fr=False)

    return JSONResponse(content={"ok": True,
                                 'service_session': await service_session.to_json(db=db, session_work_list=[])
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


async def update_payments(db: Depends, worker_id: int, session_id: int):
    contr = await conn.read_data(db=db, table="workers", name="contractor_id", id_name="user_id", id_data=worker_id)

    await conn.update_inform(db=db, name="worker_id", data=worker_id, table="payments", id_name="session_id",
                             id_data=session_id)
    await conn.update_inform(db=db, name="contractor_id", data=contr[0][0], table="payments",
                             id_name="session_id", id_data=session_id)
    await conn.update_inform(db=db, name="worker_id", data=worker_id, table="service_session", id_name="session_id",
                             id_data=session_id)
    await conn.update_inform(db=db, name="contractor_id", data=contr[0][0], table="service_session",
                             id_name="session_id", id_data=session_id)
