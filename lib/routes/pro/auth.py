import os

import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import User
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_admin
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
    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with login account",
                                     },
                            status_code=500)
    user: User = User.parse_obj(user_data[0])

    return JSONResponse(content={"ok": True,
                                 'user': user.dict(),
                                 # "vehicles": vehicles,
                                 # "service_sessions": services_sessions
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/create_worker_account', tags=['Auth Worker'], responses=post_create_account_res)
async def create_account_user(access_token: str, login: str, password: str, surname: str, contractor_id: int,
                              db=Depends(data_b.connection)):
    """Create new worker account in service with login, password, name and surname"""
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    params = {
        "login": login,
        "password": password,
    }
    res = requests.post(f'{auth_url}/create_account_login', params=params)
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.save_worker(db=db, user_id=user_id, name=login, surname=surname)
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Error with create account",
                                     },
                            status_code=500)
    await conn.save_user_to_contractor(db=db, user_id=user_data[0]["user_id"], contractor_id=contractor_id)

    user: User = User.parse_obj(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'worker': user.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/check_login', tags=['Auth Worker'], responses=post_create_account_res)
async def create_account_user(access_token: str, login: str, db=Depends(data_b.connection)):
    """Create new worker account in service with login, password, name and surname"""
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


