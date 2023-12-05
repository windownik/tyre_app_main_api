import os

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Worker, ServiceSession, Contractor
from lib.response_examples import *
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/get_me_pro', tags=['Pro'], responses=get_login_res)
async def login_user(access_token: str, db=Depends(data_b.connection)):
    """Get user in service by access token"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    user_data = await conn.get_workers_by_set(db=db, set_id={user_id})
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    worker: Worker = Worker.parse_obj(user_data[0])

    workers_ss = await conn.owner_read_ss(db=db, id_data=worker.user_id, id_name="worker_id")
    list_active_ss = []
    for one in workers_ss:
        active_ss: ServiceSession = ServiceSession.parse_obj(one)

        list_active_ss.append(await active_ss.to_json(db=db, session_work_list=[]))

    contractor_data = await conn.read_data(db=db, table="contractor", id_name="contractor_id",
                                           id_data=worker.contractor_id)
    contractor: Contractor = Contractor.parse_obj(contractor_data[0])

    return JSONResponse(content={"ok": True,
                                 'worker': worker.dict(),
                                 "active_ss": list_active_ss,
                                 "contractor": contractor.dict()
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/start_stop_work', tags=['Pro'], responses=get_login_res)
async def login_user(access_token: str, lat: float, lng: float, get_push: bool, db=Depends(data_b.connection)):
    """Get user in service by access token"""
    worker = await check_worker(db=db, access_token=access_token)
    if type(worker) != Worker:
        return worker

    await conn.update_start_stop_search(db=db, lat=lat, long=lng, get_push=get_push, user_id=worker.user_id)
    return JSONResponse(content={"ok": True,
                                 'description': "The geolocation update was successful.",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


async def check_owner_pro(db: Depends, worker_id: int, contractor_id) -> bool:
    """check worker for ownership of contractor with contractor_id"""
    conn_data = await conn.read_data(table="contractor", id_name="contractor_id", id_data=contractor_id, db=db)
    for one in conn_data:
        if one["owner_id"] == worker_id:
            return True
    return False


async def check_worker(db: Depends, access_token: str):
    """check access token and return worker account"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code == 200:
        user_id = res.json()['user_id']
    else:
        return res

    user_data = await conn.get_workers_by_set(db=db, set_id={user_id})
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    worker: Worker = Worker.parse_obj(user_data[0])
    return worker
