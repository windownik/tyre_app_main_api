import requests
import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse
from lib.db_objects import Worker, SPhoto

from lib import sql_connect as conn
from lib.response_examples import *
from lib.routes.pro.auth import check_worker, auth_url
from lib.sql_create_tables import data_b, app


@app.post(path='/session_img', tags=['SS Images'], responses=get_login_res)
async def save_new_img_id_to_ss(access_token: str, session_id: int, img_id: int, before_work: bool = False,
                                after_work: bool = False, db=Depends(data_b.connection)):
    """Get all service sessions in contractor or made by worker. This route only for contractor's owners"""
    worker = await check_worker(db=db, access_token=access_token)
    if type(worker) != Worker:
        return JSONResponse(content=worker[1],
                            status_code=worker[0],
                            headers={'content-type': 'application/json; charset=utf-8'})
    ss_data = await conn.read_data(db=db, table="service_session", id_data=session_id, id_name="session_id")
    if not ss_data:
        return JSONResponse(content={"ok": False, "description": "Bad session_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    if before_work and not after_work:
        before = True
    elif not before_work and after_work:
        before = False
    else:
        return JSONResponse(content={"ok": False, "description": "Bad session_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    session_img_data = await conn.read_data(db=db, table="photo", id_data=session_id, id_name="session_id")
    if not session_img_data:
        session_img_data = await conn.create_photo_for_ss(db=db, session_id=session_id)

    status = await save_img_to_ss(ss_img_data=session_img_data, img_id=img_id, before=before, db=db)
    if not status:
        return JSONResponse(content={"ok": False,
                                     'description': "Limit for save image to service session"},
                            status_code=_status.HTTP_403_FORBIDDEN, )

    return JSONResponse(content={"ok": True,
                                 'description': "Image successful saved"},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/session_img', tags=['SS Images'], responses=get_ss_img_res)
async def get_all_imgs_to_ss(access_token: str, session_id: int, db=Depends(data_b.connection)):
    """Get all images in service session"""
    res = requests.get(f'{auth_url}/user_id', params={"access_token": access_token})
    if res.status_code == 200:
        pass
    else:
        return res

    ss_data = await conn.read_data(db=db, table="photo", id_data=session_id, id_name="session_id")
    if not ss_data:
        photo: SPhoto = SPhoto(session_id=session_id)
        res = photo.dict()
    else:
        photo: SPhoto = SPhoto(data=ss_data[0])
        res = photo.dict()
    return JSONResponse(content=res,
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


async def save_img_to_ss(ss_img_data: tuple, img_id: int, before: bool, db: Depends) -> bool:
    session_id = ss_img_data[0]["session_id"]
    index = 1
    if before:
        sql_text = "photo_before_"
    else:
        sql_text = "photo_after_"
    while index < 5:
        if ss_img_data[0][f"{sql_text}{index}"] == 0:
            await conn.update_inform(table="photo", name=f"{sql_text}{index}", data=img_id, id_name="session_id",
                                     id_data=session_id, db=db)
            return True
        index += 1
    return False
