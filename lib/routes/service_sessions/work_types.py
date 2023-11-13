import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import User, WorkType

from lib import sql_connect as conn
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


@app.post(path='/work_type', tags=['Work types'], responses=get_login_res)
async def create_work_type(access_token: str, name_en: str, price: int, currency: str = "GBP",
                           db=Depends(data_b.connection)):
    """
    Create work_types with name and price\n
    Price in cents\n
    example: price GBP 20 should send 2000
    """
    user_id = await check_admin(access_token=access_token, db=db)
    if type(user_id) != int:
        return user_id

    await conn.create_work_type(db=db, name_en=name_en, price=price, currency=currency)

    work_type_data = await conn.read_data(db=db, table="work_types", order=" ORDER BY work_id", id_name="status",
                                          id_data="active")

    work_types_list = []
    for one in work_type_data:
        work = WorkType.parse_obj(one)
        work_types_list.append(work.dict())

    return JSONResponse(content={"ok": True,
                                 'work_types': work_types_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/all_work_types', tags=['Work types'], responses=get_login_res)
async def get_all_work_types(access_token: str, deleted: bool = False, db=Depends(data_b.connection)):
    """Get all active service_session in service"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)
    if deleted:
        work_type_data = await conn.read_all(db=db, table="work_types", order="work_id",)
    else:
        work_type_data = await conn.read_data(db=db, table="work_types", order=" ORDER BY work_id", id_name="status",
                                              id_data="active")

    work_types_list = []
    for one in work_type_data:
        work = WorkType.parse_obj(one)
        work_types_list.append(work.dict())

    return JSONResponse(content={"ok": True,
                                 'work_types': work_types_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/work_type', tags=['Work types'], responses=get_login_res)
async def update_work_type(access_token: str, work_type_id: int, name_en: str, price: int,
                           db=Depends(data_b.connection)):
    """
    Update work_types with name and price\n
    Price in cents\n
    example: price GBP 20 should send 2000
    """
    user_id = await check_admin(access_token=access_token, db=db)
    if type(user_id) != int:
        return user_id

    work_data = await conn.read_data(db=db, table='work_types', id_name='work_id', id_data=work_type_id)
    if not work_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad work_type_id",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    await conn.update_inform(db=db, name="name_en", id_name="work_id", id_data=work_type_id, data=name_en,
                             table="work_types")
    await conn.update_inform(db=db, name="price", id_name="work_id", id_data=work_type_id, data=price,
                             table="work_types")
    work_type_data = await conn.read_data(db=db, table="work_types", order=" ORDER BY work_id", id_name="status",
                                          id_data="active")

    work_types_list = []
    for one in work_type_data:
        work = WorkType.parse_obj(one)
        work_types_list.append(work.dict())

    return JSONResponse(content={"ok": True,
                                 'work_types': work_types_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/change_status_work_type', tags=['Work types'], responses=get_login_res)
async def turn_on_of_work_type(access_token: str, work_type_id: int, db=Depends(data_b.connection)):
    """Delete Work types in service by work_type_id"""
    user_id = await check_admin(access_token=access_token, db=db)
    if type(user_id) != int:
        return user_id

    work_data = await conn.read_data(db=db, table='work_types', id_name='work_id', id_data=work_type_id)
    if not work_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad work_type_id",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    status = "deleted"
    if work_data[0][4] == "deleted":
        status = "active"

    await conn.update_inform(db=db, table="work_types", name='status', data=status, id_name='work_id',
                             id_data=work_type_id)

    return JSONResponse(content={"ok": True,
                                 'description': f"Work type status change to: {status}"
                                 },
                        status_code=_status.HTTP_200_OK)
