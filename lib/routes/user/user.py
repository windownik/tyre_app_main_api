# import os
# import requests
#
# import starlette.status as _status
# from fastapi import Depends
# from starlette.responses import JSONResponse
# from lib.db_objects import User
#
# from lib import sql_connect as conn
# from lib.response_examples import *
# from lib.sql_connect import data_b, app
#
# ip_server = os.environ.get("IP_SERVER")
# ip_port = os.environ.get("PORT_SERVER")
#
# ip_port = 80 if ip_port is None else ip_port
# ip_server = "127.0.0.1" if ip_server is None else ip_server
#
#
# @app.post(path='/create_vehicle', tags=['Vehicle'], responses=get_login_res)
# async def login_user(access_token: str, reg_num: str, make: str, model: str, year: int, front_rim_diameter: int,
#                      front_aspect_ratio: int, front_section_width: int, rear_rim_diameter: int, rear_aspect_ratio: int,
#                      rear_section_width: int, bolt_key: bool, db=Depends(data_b.connection)):
#     """Create vehicle in service by information"""
#     res = requests.post('http://127.0.0.1:10050/user_id', params={"access_token": access_token})
#     status_code = res.status_code
#     if status_code == 200:
#         user_id = res.json()['user_id']
#     else:
#         return JSONResponse(content=res.json(),
#                             status_code=status_code)
#
#     user_data = await conn.read_data(db=db, table='users', id_name='user_id', id_data=user_id)
#     if not user_data:
#         return JSONResponse(content={"ok": False,
#                                      'description': "Error with login account",
#                                      },
#                             status_code=500)
#     user: User = User.parse_obj(user_data[0])
#     return JSONResponse(content={"ok": True,
#                                  'user': user.dict(),
#                                  'access_token': res.json()['access_token'],
#                                  'refresh_token': res.json()['refresh_token']
#                                  },
#                         status_code=_status.HTTP_200_OK)
