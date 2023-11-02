import os

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import User, Vehicle, ServiceSession
from lib.response_examples import *
from lib.sql_create_tables import data_b, app


ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/get_me', tags=['Auth'], responses=get_login_res)
async def login_user(access_token: str, db=Depends(data_b.connection)):
    """Get user in service by access token"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    vehicle_data = await conn.read_vehicles(db=db, user_id=user_id)
    user: User = User.parse_obj(user_data[0])
    vehicles = []
    for one in vehicle_data:
        vehicle: Vehicle = Vehicle.parse_obj(one)
        vehicles.append(vehicle.dict())

    session_data = await conn.read_service_session(db=db, client_id=user_id)
    services_sessions = []
    for one in session_data:
        session: ServiceSession = ServiceSession.parse_obj(one)
        services_sessions.append(await session.to_json(db=db, session_work_list=[]))

    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 "vehicles": vehicles,
                                 "service_sessions": services_sessions
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/create_account', tags=['Auth'], responses=post_create_account_res)
async def create_account_user(phone: int, device_id: str, device_name: str, name: str, surname: str,
                              db=Depends(data_b.connection)):
    """Create new account in service with phone number, device_id and device_name"""
    params = {
        "phone": phone,
        "device_id": device_id,
        "device_name": device_name,
    }
    res = requests.post(f'{auth_url}/create_account', params=params)
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.save_user(db=db, phone=phone, user_id=user_id, name=name, surname=surname)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with create account",
                                     },
                            status_code=500)
    user: User = User.parse_obj(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 'access_token': res.json()['access_token'],
                                 'refresh_token': res.json()['refresh_token']
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/push_token', tags=['Auth'], responses=get_login_res)
async def update_push_token(access_token: str, push_token: str, db=Depends(data_b.connection)):
    """Get user in service by access token"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    await conn.update_inform(db=db, table='users', name='push_token', id_name='user_id', data=push_token,
                             id_data=user_id)
    return JSONResponse(content={"ok": True,
                                 'description': "Push token was updated",
                                 },
                        status_code=_status.HTTP_200_OK)


@app.get(path='/get_admin', tags=['Auth'], responses=get_user_res)
async def update_user(access_token: str, user_id: int = 0, db=Depends(data_b.connection)):
    """Get admin information"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        if user_id == 0:
            user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    user: User = User.parse_obj(user_data[0])
    if user.status != 'admin':
        return JSONResponse(content={"ok": False,
                                     'description': "No rights",
                                     },
                            status_code=401)

    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
