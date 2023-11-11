import os

from fastapi import Depends
import starlette.status as _status
from lib import sql_connect as conn
from starlette.responses import JSONResponse

from lib.db_objects import PushLogs, User
from lib.response_examples import send_push_res
from lib.routes.admins.admin_routes import check_admin
from lib.sql_create_tables import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

on_page = 20


@app.get(path='/users_count_push', tags=['Admin funcs'], responses=send_push_res)
async def check_users_push_count(access_token: str, db=Depends(data_b.connection)):
    """
    Get users count for pushing messages\n\n
    access_token: users token\n
    """
    res = await check_admin(access_token=access_token, db=db)
    if type(res) != int:
        return res

    users_id = await conn.read_data_without(db=db, table="users", id_name="push_token", id_data="0")

    return JSONResponse(content={'ok': True,
                                 "all_users_count": len(users_id)},
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.post(path='/sending_push', tags=['Admin funcs'], responses=send_push_res)
async def start_sending_push_msg(access_token: str, title: str, short_text: str, content_type: str,
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
    user_id = await check_admin(access_token=access_token, db=db)
    if type(user_id) != int:
        return user_id

    if content_type != 'text' and content_type != 'img':
        return JSONResponse(content={"ok": False,
                                     'description': "bad content_type"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    users_id = await conn.read_data_without(db=db, name="user_id", table="users", id_name="push_token", id_data="0")

    await conn.msg_to_push_logs(db=db, creator_id=user_id, title=title, short_text=short_text, main_text=main_text,
                                img_url=url, content_type=content_type)

    for user in users_id:
        await conn.msg_to_user(db=db, user_id=user[0], title=title, short_text=short_text, main_text=main_text,
                               img_url=url, push_type=content_type, push_msg_id=0)

    return JSONResponse(content={'ok': True, 'desc': 'successfully created'},
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/sending_push', tags=['Admin funcs'], responses=send_push_res)
async def start_sending_push_msg(access_token: str, search: str = 0, page: int = 0, db=Depends(data_b.connection)):
    """
    Use it route for create massive sending message for users with filter\n\n
    access_token: users token\n
    content_type: can be: text for text message and img for img message\n
    title: Tittle of message\n
    short_text: short text of push message\n
    main_text: main text of message for content type 0\n
    url: url to img in internet for content type 0\n
    """
    user_id = await check_admin(access_token=access_token, db=db)
    if type(user_id) != int:
        return user_id

    push_data = await conn.read_all(db=db, table="push_logs", order="id DESC")

    _push_data = []
    for i in push_data:
        if search == "0":
            _push_data.append(i)
            continue
        if search in i[1]:
            _push_data.append(i)
        elif search in i[3]:
            _push_data.append(i)
        elif search in i[4]:
            _push_data.append(i)

    new_push_data = _push_data[page * on_page: (page + 1) * on_page]

    push_log_list = []
    set_users = set()
    for one in new_push_data:

        one_push: PushLogs = PushLogs.parse_obj(one)
        set_users.add(one_push.creator_id)
        push_log_list.append(one_push.dict())

    list_user = []
    if len(set_users) != 0:
        crop_user_list = await conn.get_user_by_set(db=db, set_id=set_users)

        for one in crop_user_list:
            user: User = User.parse_obj(one)
            list_user.append(user.dict())

    return JSONResponse(content={'ok': True,
                                 'push_log': push_log_list,
                                 "users": list_user,
                                 },
                        headers={'content-type': 'application/json; charset=utf-8'})
