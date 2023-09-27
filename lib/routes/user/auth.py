import os

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import User
from lib.response_examples import *
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@app.post(path='/login', tags=['Auth'], responses=get_login_res)
async def login_user(phone: int, sms_code: int, device_id: str, device_name: str, db=Depends(data_b.connection)):
    """Login user in service by phone number, device_id and device_name"""
    """Create new account in service with phone number, device_id and device_name"""
    params = {
        "phone": phone,
        "sms_code": sms_code,
        "device_id": device_id,
        "device_name": device_name,
    }
    res = requests.post('http://127.0.0.1:10050/login', params=params)
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
    user: User = User.parse_obj(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 'access_token': res.json()['access_token'],
                                 'refresh_token': res.json()['refresh_token']
                                 },
                        status_code=_status.HTTP_200_OK)


@app.post(path='/create_account', tags=['Auth'], responses=post_create_account_res)
async def create_account_user(phone: int, sms_code: int, device_id: str, device_name: str, name: str, surname: str,
                              db=Depends(data_b.connection)):
    """Create new account in service with phone number, device_id and device_name"""
    params = {
        "phone": phone,
        "sms_code": sms_code,
        "device_id": device_id,
        "device_name": device_name,
    }
    res = requests.post('http://127.0.0.1:10050/create_account', params=params)
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
                        status_code=_status.HTTP_200_OK)
