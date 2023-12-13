import os
import requests

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import ServiceSession, WorkType, SessionWork

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


@app.post(path='/service_session', tags=['Service session'], responses=get_login_res)
async def create_service_session(access_token: str, vehicle_id: int, session_type: str, session_date: int,
                                 work_type_id: str, lat: float, long: float, address: str, bolt_key: bool = False,
                                 wheel_fr: bool = False, wheel_fl: bool = False, wheel_rr: bool = False,
                                 wheel_rl: bool = False, db=Depends(data_b.connection)):
    """
    Create service_session with information\n
    vehicle_id: id number of vehicle\n
    service_session string can be: now, schedule
    """
    work_type_id = work_type_id.split(',')
    for one in work_type_id:
        try:
            a = int(one)
        except Exception as e:
            print(e)
            return JSONResponse(content={"ok": False,
                                         "list": f"{work_type_id}",
                                         'description': "Bad list of integers in work_type_id"},
                                status_code=_status.HTTP_400_BAD_REQUEST)
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
                                                     session_type=session_type, bolt_key=bolt_key,
                                                     session_date=session_date, lat=lat, long=long, address=address)
    service_session: ServiceSession = ServiceSession.parse_obj(session_data[0])

    list_ss_work = []

    for one in work_type_id:
        one = int(one)
        work_type_data = await conn.read_data(db=db, table="work_types", id_data=one, id_name='work_id')
        work_type: WorkType = WorkType.parse_obj(work_type_data[0])
        ss_work = await conn.create_ss_work(db=db, session_id=session_data[0][0], currency=work_type.currency,
                                            name_en=work_type.name_en, price=work_type.price,
                                            work_type_id=work_type.work_id, wheel_rr=wheel_rr, wheel_rl=wheel_rl,
                                            wheel_fl=wheel_fl, wheel_fr=wheel_fr)
        session_work: SessionWork = SessionWork.parse_obj(ss_work[0])
        list_ss_work.append(session_work)
    return JSONResponse(content={"ok": True,
                                 'service_session': await service_session.to_json(db=db, session_work_list=list_ss_work)
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/service_session', tags=['Service session'], responses=get_login_res)
async def get_service_session(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Get service_session by service_session_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    service_data = await conn.read_data(db=db, table='service_session', id_name='session_id', id_data=session_id)
    if not service_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    service_session: ServiceSession = ServiceSession.parse_obj(service_data[0])
    return JSONResponse(content={"ok": True,
                                 'service_session': await service_session.to_json(db=db, session_work_list=[])
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/service_session', tags=['Service session'], responses=get_login_res)
async def delete_service_session(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Delete service_session in service by session_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        pass
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    vehicle_data = await conn.read_data(db=db, table='service_session', id_name='session_id', id_data=session_id)
    if not vehicle_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service_session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_inform(db=db, table="service_session", name='status', data='deleted', id_name='session_id',
                             id_data=session_id)

    return JSONResponse(content={"ok": True,
                                 'description': "Service_session was successful delete"
                                 },
                        status_code=_status.HTTP_200_OK)


@app.get(path='/client_service_session', tags=['Service session'], responses=get_login_res)
async def get_service_session(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Get service_session by service_session_id"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    status_code = res.status_code
    if status_code == 200:
        user_id = res.json()['user_id']
    else:
        return JSONResponse(content=res.json(),
                            status_code=status_code)

    service_data = await conn.read_data(db=db, table='service_session', id_name='client_id', id_data=user_id)
    if not service_data:
        return JSONResponse(content={"ok": False,
                                     'description': "The service session with this session_id is not registered",
                                     },
                            status_code=_status.HTTP_400_BAD_REQUEST)
    service_list = []
    for one in service_data:
        service_session: ServiceSession = ServiceSession.parse_obj(one)
        service_list.append(await service_session.to_json(db=db, session_work_list=[]))
    return JSONResponse(content={"ok": True,
                                 'service_session_list': service_list
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
