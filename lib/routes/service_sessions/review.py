import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Review, ServiceSession

from lib import sql_connect as conn
from lib.response_examples import *
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.post(path='/review', tags=['Review'], responses=get_login_res)
async def create_review(access_token: str, session_id: int, text: str, score: int, db=Depends(data_b.connection)):
    """
    Create review with information\n
    score integer can be: 1...5
    """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    service_data = await conn.read_data(db=db, table='service_session', id_name='session_id', id_data=session_id)
    if not service_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service session with this session_id is not registered"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    if score not in (1, 2, 3, 4, 5):
        return JSONResponse(content={"ok": False,
                                     'description': "Wrong score"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    review = await conn.create_review(db=db, client_id=user_id, score=score, session_id=session_id, text=text)
    review: Review = Review.parse_obj(review[0])
    return JSONResponse(content={"ok": True,
                                 'review': review.dict()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/review', tags=['Review'], responses=get_login_res)
async def get_review(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Get service_session by service_session_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    service_data = await conn.read_data(db=db, table='review', id_name='session_id', id_data=session_id)
    if not service_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    review: Review = Review.parse_obj(service_data[0])
    return JSONResponse(content={"ok": True,
                                 'service_session': review.dict()
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/review', tags=['Review'], responses=get_login_res)
async def delete_review(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Delete service_session in service by session_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='service_session', id_name='session_id', id_data=session_id)
    if not vehicle_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service_session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_inform(db=db, table="service_session", name='status', data='deleted', id_name='session_id',
                             id_data=session_id)

    return JSONResponse(content={"ok": True,
                                 'description': "Service_session was successful delete"
                                 },
                        status_code=_status.HTTP_200_OK)
