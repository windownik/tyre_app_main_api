import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Vehicle, User, ServiceSession

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

on_page = 20


@app.get(path='/admin_users', tags=['Admin funcs'], responses=get_login_res)
async def admin_get_users(access_token: str, search: str = 0, page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get users with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != bool:
        return res

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

    crop_user_list = new_user_list[page * on_page: (page + 1) * on_page]

    list_user = []
    for one in crop_user_list:
        user: User = User.parse_obj(one)
        list_user.append(user.dict())

    return JSONResponse(content={"ok": True,
                                 'list_users': list_user,
                                 "pages": len(new_user_list) // on_page + 1,
                                 "all_users_count": len(user_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/get_all_vehicles', tags=['Admin funcs'], responses=get_login_res)
async def admin_get_users(access_token: str, search: str = 0, page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get vehicles with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != bool:
        return res

    vehicle_data = await conn.read_admin_vehicles(db=db)

    new_vehicle_list = []
    for i in vehicle_data:
        if search == "0":
            new_vehicle_list.append(i)
            continue
        if search in i[1]:
            new_vehicle_list.append(i)
        elif search in i[3]:
            new_vehicle_list.append(i)
        elif search in i[4]:
            new_vehicle_list.append(i)

    crop_user_list = new_vehicle_list[page * on_page: (page + 1) * on_page]

    list_vehicles = []
    set_users = set()
    for one in crop_user_list:
        vehicle: Vehicle = Vehicle.parse_obj(one)
        list_vehicles.append(vehicle.dict())

        set_users.add(vehicle.owner_id)

    list_user = []
    if len(set_users) != 0:
        crop_user_list = await conn.get_user_by_set(db=db, set_id=set_users)

        for one in crop_user_list:
            user: User = User.parse_obj(one)
            list_user.append(user.dict())

    return JSONResponse(content={"ok": True,
                                 'list_vehicles': list_vehicles,
                                 "pages": len(new_vehicle_list) // on_page + 1,
                                 "users": list_user,
                                 "all_vehicles_count": len(vehicle_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/get_all_ss', tags=['Admin funcs'], responses=get_login_res)
async def admin_get_service_sessions(access_token: str, search: str = 0, page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get service_sessions with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != bool:
        return res

    ss_data = await conn.read_admin_ss(db=db)

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

    crop_user_list = new_ss_list[page * on_page: (page + 1) * on_page]

    list_ss = []
    set_users = set()
    for one in crop_user_list:
        ss: ServiceSession = ServiceSession.parse_obj(one)
        set_users.add(ss.session_id)
        list_ss.append(ss.dict())

    list_user = []
    if len(set_users) != 0:
        crop_user_list = await conn.get_user_by_set(db=db, set_id=set_users)

        for one in crop_user_list:
            user: User = User.parse_obj(one)
            list_user.append(user.dict())

    return JSONResponse(content={"ok": True,
                                 'list_sessions': list_ss,
                                 "pages": len(new_ss_list) // on_page + 1,
                                 "users": list_user,
                                 "all_sessions_count": len(ss_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


async def check_admin(access_token: str, db: Depends):
    """Check services access token for admin"""
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
    return True


# abcd = [1, 2, 3, 4, 4, 5, 5, 6]
# a = set()
# for one in abcd:
#     a.add(one)
#
# sql_id = ""
#
# for i in a:
#     print(i)
#     sql_id = f"{sql_id} user_id={i} OR"
# sql_id = sql_id[0: -3]
# DDD = f"SELECT * FROM users WHERE{sql_id};"
# print(DDD)
