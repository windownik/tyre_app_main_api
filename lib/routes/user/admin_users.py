import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import User

from lib import sql_connect as conn
from lib.response_examples import *
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"


@app.get(path='/admin_users', tags=['Admin users'], responses=get_login_res)
async def admin_get_users(access_token: str, search: str = 0, page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get users with search
    """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
    user: User = User.parse_obj(user_data[0])

    if user.user_type != 'admin':
        return JSONResponse(content={"ok": False,
                                     'description': "Not enough rights"},
                            status_code=500)

    user_data = await conn.read_users(db=db, )

    new_user_list = []
    for i in user_data:
        if search == "0":
            new_user_list.append(i)
            continue
        if search in i[1]:
            new_user_list.append(i)
        elif search in i[2]:
            new_user_list.append(i)
        elif search in i[4]:
            new_user_list.append(i)
        elif search in str(i[3]):
            new_user_list.append(i)
    users_one_page = 1
    new_user_list = new_user_list[page * users_one_page: (page + 1) * users_one_page]

    list_user = []
    for one in new_user_list:
        user: User = User.parse_obj(one)
        list_user.append(user.dict())

    return JSONResponse(content={"ok": True,
                                 'list_users': list_user,
                                 "pages": len(user_data) // users_one_page + 1
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
