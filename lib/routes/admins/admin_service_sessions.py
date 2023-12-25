from math import ceil

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import User, ServiceSession, Worker

from lib import sql_connect as conn
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_admin
from lib.routes.push.push import on_page
from lib.sql_create_tables import data_b, app


@app.get(path='/get_all_ss', tags=['Admin service sessions'], responses=get_login_res)
async def admin_get_service_sessions(access_token: str, search: str = 0, page: int = 0, sort: str = "DESC",
                                     db=Depends(data_b.connection)):
    """
    Admin get service_sessions with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    ss_data = await conn.read_admin_ss(db=db, sort=sort)

    new_ss_list = []
    for i in ss_data:
        if search == "0":
            new_ss_list.append(i)
            continue
        if search in i[1]:
            new_ss_list.append(i)
        elif search in i[3]:
            new_ss_list.append(i)
        elif search in i[4]:
            new_ss_list.append(i)

    crop_ss_list = new_ss_list[page * on_page: (page + 1) * on_page]

    ss_list, list_user, list_worker = await get_ss_users_workers(db=db, ss_data=crop_ss_list)

    return JSONResponse(content={"ok": True,
                                 'ss_list': ss_list,
                                 "pages": ceil(len(ss_data) / on_page),
                                 "users": list_user,
                                 "workers": list_worker,
                                 "all_ss_count": len(ss_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/contractor_ss', tags=['Admin service sessions'], responses=get_login_res)
async def admin_get_contractors_or_worker_ss(access_token: str, contractor_id: int = 0, worker_id: int = 0,
                                             page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get all contractors services sessions
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res
    if contractor_id == 0 and worker_id == 0:
        return JSONResponse(content={"ok": False,
                                     'description':
                                         "Error with contractor_id and worker_id. One of these must not equal 0",
                                     }, status_code=400)
    elif contractor_id != 0:
        ss_data = await conn.read_data(db=db, table='service_session', id_name="contractor_id", id_data=contractor_id,
                                       order=" ORDER BY session_id DESC")
    else:
        ss_data = await conn.read_data(db=db, table='service_session', id_name="worker_id", id_data=worker_id,
                                       order=" ORDER BY session_id DESC")

    crop_ss_list = ss_data[page * on_page: (page + 1) * on_page]
    ss_list, list_user, list_worker = await get_ss_users_workers(db=db, ss_data=crop_ss_list)

    return JSONResponse(content={"ok": True,
                                 'ss_list': ss_list,
                                 "pages": ceil(len(ss_data) / on_page),
                                 "users": list_user,
                                 "workers": list_worker,
                                 "all_ss_count": len(ss_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


async def get_ss_users_workers(db: Depends, ss_data: list[dict]):
    co_list = []
    set_users = set()
    set_workers = set()
    for one in ss_data:
        ss: ServiceSession = ServiceSession.parse_obj(one)
        set_users.add(ss.client_id)
        set_workers.add(ss.worker_id)
        co_list.append(await ss.to_json(db=db, session_work_list=[]))

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

    return co_list, list_user, list_workers

