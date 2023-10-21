import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Vehicle

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


@app.post(path='/vehicle', tags=['Vehicle'], responses=get_login_res)
async def create_vehicle(access_token: str, reg_num: str, make: str, model: str, year: int, front_rim_diameter: int,
                         front_aspect_ratio: int, front_section_width: int, rear_rim_diameter: int,
                         rear_aspect_ratio: int, rear_section_width: int, bolt_key: bool,
                         db=Depends(data_b.connection)):
    """Create vehicle in service by information"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='vehicle', id_name='reg_num', id_data=reg_num)
    if vehicle_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The vehicle with this reg_num is registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    vehicle_data = await conn.create_vehicle(db=db, bolt_key=bolt_key, reg_num=reg_num, year=year, model=model,
                                             front_aspect_ratio=front_aspect_ratio, make=make, owner_id=user_id,
                                             front_rim_diameter=front_rim_diameter,
                                             front_section_width=front_section_width,
                                             rear_aspect_ratio=rear_aspect_ratio, rear_rim_diameter=rear_rim_diameter,
                                             rear_section_width=rear_section_width
                                             )
    vehicle: Vehicle = Vehicle.parse_obj(vehicle_data[0])
    return JSONResponse(content={"ok": True,
                                 'vehicle': vehicle.dict()
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/vehicle', tags=['Vehicle'], responses=get_login_res)
async def get_vehicle(access_token: str, reg_num: str, vehicle_id: int, db=Depends(data_b.connection)):
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


@app.delete(path='/vehicle', tags=['Vehicle'], responses=get_login_res)
async def delete_vehicle(access_token: str, vehicle_id: int, db=Depends(data_b.connection)):
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
