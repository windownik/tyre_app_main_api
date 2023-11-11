import os

from fastapi import Depends
import starlette.status as _status
from lib import sql_connect as conn
from starlette.responses import JSONResponse

from lib.response_examples import send_push_res
from lib.routes.admins.admin_routes import check_admin
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@app.post(path='/users_count_push', tags=['Push'], responses=send_push_res)
async def check_users_push_count(access_token: str, content_type: str, db=Depends(data_b.connection)):
    """
    Use it route for create massive sending message for users with filter\n\n
    access_token: users token\n
    content_type: can be: text for text message and img for img message\n
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != bool:
        return res

    if content_type != 'text' or content_type != 'img':
        return JSONResponse(content={"ok": False,
                                     'description': "bad content_type"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    users_id = await conn.read_data_without(db=db, table="users", id_name="push_token", id_data="0")

    return JSONResponse(content={'ok': True,
                                 "all_users_count": len(users_id)},
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/sending_push', tags=['Push'], responses=send_push_res)
async def start_sending_push_msg(access_token: str, content_type: str, title: str, short_text: str,
                                 main_text: str = None, url: str = None,
                                 db=Depends(data_b.connection)):
    """
    Use it route for create massive sending message for users with filter\n\n
    access_token: users token\n
    content_type: can be: text for text message and img for img message\n
    title: Tittle of message\n
    short_text: short text of push message\n
    main_text: main text of message for content type 0\n
    url: url to img in internet for content type 0\n
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != bool:
        return res

    if content_type != 'text' or content_type != 'img':
        return JSONResponse(content={"ok": False,
                                     'description': "bad content_type"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    users_id = await conn.read_data_without(db=db, name="user_id", table="users", id_name="push_token", id_data="0")

    for user in users_id:
        await conn.msg_to_user(db=db, user_id=user[0], title=title, short_text=short_text, main_text=main_text,
                               img_url=url, push_type=content_type, push_msg_id=0)

    return JSONResponse(content={'ok': True, 'desc': 'successfully created'},
                        headers={'content-type': 'application/json; charset=utf-8'})
