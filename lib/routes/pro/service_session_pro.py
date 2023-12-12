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
async def worker_work_in_service_session(access_token: str, session_id: int,
                                         delivery: bool = False,
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
    ss_data = await conn.read_data(db=db, table="service_session", id_data=session_id, id_name="session_id")
    if not ss_data:
        return JSONResponse(content={"ok": False, "description": "Bad session_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    if start_work and not finish_work and not in_service_work and not delivery:
        worker_id = res.json()['user_id']
        other_ss = await conn.read_workers_ss(db=db, worker_id=worker_id)
        if other_ss:
            return JSONResponse(content={"ok": False, "description": "Worker not free for new session"},
                                status_code=_status.HTTP_409_CONFLICT)
        status = "in work"
    elif not start_work and finish_work and not in_service_work and not delivery:
        status = "success"
    elif not start_work and not finish_work and in_service_work and not delivery:
        status = "in_service"
    elif not start_work and not finish_work and not in_service_work and delivery:
        status = "delivery"
    else:
        return JSONResponse(content={"ok": False, "description": "Bad start_work and finish_work and in_service_work "
                                                                 "flags"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_inform(db=db, table="service_session", id_name="session_id", id_data=session_id, name='status',
                             data=status)
    return JSONResponse(content={"ok": True,
                                 "description": "Successful updating"
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})

