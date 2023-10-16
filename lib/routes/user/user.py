import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import User

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


@app.put(path='/user', tags=['User'], responses=get_login_res)
async def update_user(access_token: str, name: str, surname: str, email: str, db=Depends(data_b.connection)):
    """Update user information"""
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
    await conn.update_user(db=db, name=name, surname=surname, email=email, user_id=user_id)
    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    user: User = User.parse_obj(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 },
                        status_code=_status.HTTP_200_OK)


@app.delete(path='/user', tags=['User'], responses=delete_user_res)
async def login_user(access_token: str, db=Depends(data_b.connection)):
    """Create vehicle in service by information"""
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
                                     'description': "Error with user information, please login account",
                                     },
                            status_code=500)

    await conn.update_inform(db=db, name='status', id_name='user_id', id_data=user_id, table='users', data='deleted')
    return JSONResponse(content={"ok": True,
                                 'description': "User account is deleted",
                                 },
                        status_code=_status.HTTP_200_OK)
