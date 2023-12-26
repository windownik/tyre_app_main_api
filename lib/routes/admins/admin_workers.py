import os
from math import ceil

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Worker

from lib import sql_connect as conn
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_admin, check_con_owner_or_admin, on_page
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/admin_workers', tags=['Admin worker'], responses=get_login_res)
async def admin_get_workers(access_token: str, search: str = '0', page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get workers with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    user_data = await conn.read_workers(db=db, )

    new_user_list = []
    for i in user_data:
        if search == "0":
            new_user_list.append(i)
            continue
        if search in i[2]:
            new_user_list.append(i)
        elif search in i[3]:
            new_user_list.append(i)
        elif search in str(i[1]):
            new_user_list.append(i)
        elif search in str(i[0]):
            new_user_list.append(i)

    crop_user_list = new_user_list[page * on_page: (page + 1) * on_page]

    list_user = []
    for one in crop_user_list:
        user: Worker = Worker.parse_obj(one)
        list_user.append(user.dict())

    return JSONResponse(content={"ok": True,
                                 'list_users': list_user,
                                 "pages": ceil(len(list_user) / on_page),
                                 "all_users_count": len(user_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/contractor_workers', tags=['Admin worker'], responses=get_login_res)
async def admin_get_contractors_workers(access_token: str, contractor_id: int, db=Depends(data_b.connection)):
    """
    Admin get all contractor's workers
    """
    res = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(res) != int:
        return res

    user_data = await conn.read_contractors_workers(db=db, contractor_id=contractor_id)

    list_worker = []
    for one in user_data:
        worker: Worker = Worker.parse_obj(one)
        list_worker.append(worker.dict())

    return JSONResponse(content={"ok": True,
                                 'list_workers': list_worker,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/worker', tags=['Admin Worker'], responses=post_create_account_res)
async def create_worker_account(access_token: str, login: str, password: str, worker_name: str, contractor_id: int,
                                db=Depends(data_b.connection)):
    """Create new worker account in service with login, password, name and surname"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    params = {
        "login": login,
        "password": password,
        "app_name": "tyre_app_pro"
    }
    res = requests.post(f'{auth_url}/create_account_login', params=params)
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.save_worker(db=db, user_id=user_id, login=login, worker_name=worker_name,
                                       contractor_id=contractor_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with create account",
                                     }, status_code=400)

    return JSONResponse(content={"ok": True,
                                 'description': "Worker created successful",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/check_worker_login', tags=['Admin Worker'], responses=post_create_account_res)
async def admin_check_new_worker_login(access_token: str, login: str, db=Depends(data_b.connection)):
    """Admin should check new worker login before create it."""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    login_data = await conn.read_data(db=db, table="auth", name="login", id_name="login", id_data=login)
    if login_data:
        return JSONResponse(content={"ok": False,
                                     'description': "I have the same login in services",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content={"ok": True,
                                 'description': "Login is free for account",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/worker', tags=['Admin Worker'], responses=get_user_res)
async def update_worker_name(access_token: str, name: str, worker_id: int, db=Depends(data_b.connection)):
    """Update worker's name for worker with worker_id"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    user_data = await conn.read_data(db=db, table='workers', id_name='user_id', id_data=worker_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad worker_id",
                                     }, status_code=400)

    await conn.update_inform(db=db, table="workers", name="worker_name", data=name, id_name="user_id",
                             id_data=worker_id)

    return JSONResponse(content={"ok": True,
                                 'description': "Worker name successful updated",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/worker', tags=['Admin Worker'], responses=get_user_res)
async def update_workers_status(access_token: str, active: bool, worker_id: int, db=Depends(data_b.connection)):
    """Delete or activate worker with worker_id"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    user_data = await conn.read_data(db=db, table='workers', id_name='user_id', id_data=worker_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad worker_id",
                                     }, status_code=400)

    status = "active" if active else "deleted"
    await conn.update_inform(db=db, table="workers", name="status", data=status, id_name="user_id", id_data=worker_id)

    return JSONResponse(content={"ok": True,
                                 'description': f"Worker's status successful updated to {status}",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
