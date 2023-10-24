import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Vehicle, ServiceSession

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


@app.post(path='/service_session', tags=['Service session'], responses=get_login_res)
async def create_service_session(access_token: str, vehicle_id: int, session_type: str, session_date: int,
                                 wheel_fr: int = 0, wheel_fl: int = 0, wheel_rr: int = 0, wheel_rl: int = 0,
                                 db=Depends(data_b.connection)):
    """
    Create service_session with information\n
    service_session string can be: now, schedule
    """
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='vehicle', id_name='vehicle_id', id_data=vehicle_id)
    if not vehicle_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The vehicle with this vehicle_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    if session_type not in ('now', 'schedule'):
        return JSONResponse(content={"ok": False,
                                     'description': "Wrong session_type"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    session_data = await conn.create_service_session(db=db, client_id=user_id, vehicle_id=vehicle_id,
                                                     wheel_fr=wheel_fr, wheel_fl=wheel_fl, session_type=session_type,
                                                     session_date=session_date, wheel_rl=wheel_rl, wheel_rr=wheel_rr)
    service_session: ServiceSession = ServiceSession.parse_obj(session_data[0])
    return JSONResponse(content={"ok": True,
                                 'service_session': await service_session.to_json(db=db)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/service_session', tags=['Service session'], responses=get_login_res)
async def get_service_session(access_token: str, reg_num: str, vehicle_id: int, db=Depends(data_b.connection)):
    """Get vehicle in service by reg_num or vehicle_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='vehicle', id_name='reg_num', id_data=reg_num)
    if not vehicle_data:
        vehicle_data = await conn.read_data(db=db, table='vehicle', id_name='vehicle_id', id_data=vehicle_id)
        if not vehicle_data:
            return JSONResponse(content={"ok": False,
                                         'description': "The vehicle with this reg_num or vehicle_id is not registered",
                                         },
                                status_code=_status.HTTP_400_BAD_REQUEST)

    vehicle: Vehicle = Vehicle.parse_obj(vehicle_data[0])
    return JSONResponse(content={"ok": True,
                                 'vehicle': vehicle.dict()
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/service_session', tags=['Service session'], responses=get_login_res)
async def delete_service_session(access_token: str, vehicle_id: int, db=Depends(data_b.connection)):
    """Delete vehicle in service by vehicle_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='vehicle', id_name='vehicle_id', id_data=vehicle_id)
    if not vehicle_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The vehicle with this reg_num or vehicle_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_inform(db=db, table="vehicle", name='status', data='deleted', id_name='vehicle_id',
                             id_data=vehicle_id)

    return JSONResponse(content={"ok": True,
                                 'description': "Vehicle was successful delete"
                                 },
                        status_code=_status.HTTP_200_OK)
