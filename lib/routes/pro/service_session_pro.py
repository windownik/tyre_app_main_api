import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import ServiceSession, WorkType, SessionWork

from lib import sql_connect as conn
from lib.response_examples import *
from lib.routes.pro.auth import check_owner_pro
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/service_session_pro', tags=['Service session'], responses=get_login_res)
async def get_all_service_session_for_pro(access_token: str, contractor_id: int = 0, db=Depends(data_b.connection)):
    """Get service_session by service_session_id"""
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
        service_data = await conn.read_data(db=db, table='service_session', id_name='contractor_id', id_data=contractor_id)
    else:
        service_data = await conn.read_data(db=db, table='service_session', id_name='worker_id', id_data=user_id)

    list_s_s = []
    for one in service_data:
        session: ServiceSession = ServiceSession.parse_obj(one)
        list_s_s.append(await session.to_json(db=db, session_work_list=[]))

    return JSONResponse(content={"ok": True,
                                 'list_service_session': list_s_s
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})

