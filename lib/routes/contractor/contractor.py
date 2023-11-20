import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Contractor

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

on_page = 20


@app.post(path='/contractor', tags=['Admin contractor'], responses=get_login_res)
async def admin_create_contractor(access_token: str, owner_id: int, co_name: str, co_email: str, address: str,
                                  acc_num: str, vat_number: str, sort_code: int, post_code: int, beneficiary_name: str,
                                  db=Depends(data_b.connection)):
    """
    Admin create new contractor
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return JSONResponse(content="User with owner_id not found",
                            status_code=_status.HTTP_400_BAD_REQUEST)

    contr_data = await conn.create_contractor(db=db, owner_id=owner_id, co_name=co_name, co_email=co_email,
                                              address=address, acc_num=acc_num, vat_number=vat_number,
                                              post_code=post_code, sort_code=sort_code,
                                              beneficiary_name=beneficiary_name)
    contractor: Contractor = Contractor.parse_obj(contr_data[0])

    await conn.save_user_to_contractor(db=db, user_id=owner_id, contractor_id=contractor.contractor_id)

    return JSONResponse(content={"ok": True,
                                 'contractor': contractor.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/all_contractors', tags=['Admin contractor'], responses=get_login_res)
async def admin_get_all_contractors(access_token: str, search: str = "0", page: int = 0, db=Depends(data_b.connection)):
    """
    Admin get all contractors in service with all status with search
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res
    co_data = await conn.read_all(db=db, table='contractor', order="contractor_id")

    new_co_list = []
    for i in co_data:
        if search == "0":
            new_co_list.append(i)
            continue
        if search in i[2]:
            new_co_list.append(i)
        elif search in i[3]:
            new_co_list.append(i)
        elif search in i[4]:
            new_co_list.append(i)
        elif search in i[9]:
            new_co_list.append(i)

    crop_co_list = new_co_list[page * on_page: (page + 1) * on_page]
    co_list = []
    for one in crop_co_list:
        contractor: Contractor = Contractor.parse_obj(one)
        co_list.append(contractor.dict())
    return JSONResponse(content={"ok": True,
                                 'contractor_list': co_list,
                                 "pages": len(new_co_list),
                                 "all_contractors_count": len(co_data)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/contractor', tags=['For all'], responses=get_login_res)
async def admin_get_contractor(access_token: str, contractor_id: int, worker_id: int = 0,
                               db=Depends(data_b.connection)):
    """
    Admin get contractor by contractor_id or get all user's contractors with user_id
    """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return res

    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return JSONResponse(content="User with owner_id not found",
                            status_code=_status.HTTP_400_BAD_REQUEST)
    if worker_id == 0:
        co_data = await conn.read_data(db=db, table='contractor', id_data=contractor_id, id_name="contractor_id")
    else:
        co_data = await conn.get_contractors_by_user_id(db=db, worker_id=worker_id)
    co_list = []
    for one in co_data:
        contractor: Contractor = Contractor.parse_obj(one)
        co_list.append(contractor.dict())
    return JSONResponse(content={"ok": True,
                                 'contractor_list': co_list,
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/contractor', tags=['for all'], responses=get_login_res)
async def delete_or_activate_contractor(access_token: str, contractor_id: int, status: bool,
                                        db=Depends(data_b.connection)):
    """
    Admin delete or activate contractor by contractor_id
    """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return res

    contr_data = await conn.read_data(db=db, table='contractor', id_data=contractor_id, id_name="contractor_id")
    if not contr_data:
        return JSONResponse(content="Contractor with contractor_id not found",
                            status_code=_status.HTTP_400_BAD_REQUEST)

    new_status = "active" if status else "deleted"
    await conn.update_inform(db=db, table="contractor", name="status", data=new_status, id_data=contractor_id,
                             id_name="contractor_id")

    return JSONResponse(content={"ok": True,
                                 'description': f"Contractor status changed to {new_status}",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/contractor', tags=['Admin contractor'], responses=get_login_res)
async def admin_update_contractor(access_token: str, contractor_id: int, co_name: str, co_email: str, address: str,
                                  acc_num: str, vat_number: str, sort_code: int, post_code: int, beneficiary_name: str,
                                  db=Depends(data_b.connection)):
    """
    Admin create new contractor
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code != 200:
        return JSONResponse(content="User with owner_id not found",
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_contractor(db=db, contractor_id=contractor_id, co_name=co_name, co_email=co_email,
                                 address=address, acc_num=acc_num, vat_number=vat_number,
                                 post_code=post_code, sort_code=sort_code,
                                 beneficiary_name=beneficiary_name)

    return JSONResponse(content={"ok": True,
                                 'description': "Contractor information successful updated.",
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
