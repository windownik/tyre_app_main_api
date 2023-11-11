import datetime
import time

from fastapi import Depends


async def save_user(db: Depends, user_id: int, name: str, surname: str, phone: int):
    """Save main users information"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO users (user_id, name, surname, phone, last_active, createdate) "
                          f"VALUES ($1, $2, $3, $4, $5, $6) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, name, surname, phone,
                          int(time.mktime(create_date.timetuple())), int(time.mktime(create_date.timetuple())))
    return data


async def create_vehicle(db: Depends, reg_num: str, owner_id: int, make: str, model: str, year: int,
                         front_rim_diameter: int, front_aspect_ratio: int, front_section_width: int,
                         rear_rim_diameter: int, rear_aspect_ratio: int, rear_section_width: int, bolt_key: bool):
    """We are create a new vehicle"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO vehicle (reg_num, owner_id, make, model, year, front_rim_diameter, "
                          f"front_aspect_ratio, front_section_width, rear_rim_diameter, rear_aspect_ratio, "
                          f"rear_section_width, bolt_key, createdate) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", reg_num, owner_id, make, model, year,
                          front_rim_diameter, front_aspect_ratio, front_section_width, rear_rim_diameter,
                          rear_aspect_ratio, rear_section_width, bolt_key, int(time.mktime(create_date.timetuple())))
    return data


async def create_service_session(db: Depends, client_id: int, vehicle_id: int, session_type: str, bolt_key: bool,
                                 session_date: int):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO service_session (client_id, vehicle_id, session_type, session_date, bolt_key, "
                          f"create_date) VALUES ($1, $2, $3, $4, $5, $6) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", client_id, vehicle_id, session_type, session_date,
                          bolt_key, int(time.mktime(create_date.timetuple())))
    return data


async def create_ss_work(db: Depends, session_id: int, work_type_id: int, name_en: str, price: int, currency: str,
                         wheel_fr: bool, wheel_fl: bool, wheel_rr: bool, wheel_rl: bool):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO session_works (session_id, work_type_id, name_en, price, "
                          f"currency, wheel_fr, wheel_fl, wheel_rr, wheel_rl, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", session_id, work_type_id, name_en, price, currency,
                          wheel_fr, wheel_fl, wheel_rr, wheel_rl, int(time.mktime(create_date.timetuple())))
    return data


async def create_review(db: Depends, session_id: int, client_id: int, text: str, score: int):
    """We are create a new review for service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO review (session_id, client_id, text, score, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", session_id, client_id, text, score,
                          int(time.mktime(create_date.timetuple())))
    return data


async def create_work_type(db: Depends, name_en: str, price: int, currency: str):
    """We are create a new Work type for services sessions"""
    data = await db.fetch(f"INSERT INTO work_types (name_en, price, currency) "
                          f"VALUES ($1, $2, $3) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", name_en, price, currency)
    return data


async def msg_to_user(db: Depends, user_id: int, title: str, short_text: str, main_text: str, img_url: str,
                      push_type: str, push_msg_id: int):
    """We are create a new Work type for services sessions"""
    data = await db.fetch(f"INSERT INTO sending "
                          f"(user_id, title, short_text, main_text, img_url, push_type, push_msg_id) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, title, short_text, main_text, img_url,
                          push_type, push_msg_id)
    return data


async def msg_to_push_logs(db: Depends, creator_id: int, title: str, short_text: str, main_text: str, img_url: str,
                           content_type: str):
    """We are create a new Work type for services sessions"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO push_logs "
                          f"(creator_id, title, short_text, main_text, img_url, content_type, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", creator_id, title, short_text, main_text, img_url,
                          content_type, int(time.mktime(create_date.timetuple())))
    return data


async def get_user_id(db: Depends, token_type: str, token: str, device_id: str):
    """Get user_id by token and device id"""
    now = datetime.datetime.now()
    data = await db.fetch(f"SELECT user_id, death_date FROM token "
                          f"WHERE token_type = $1 "
                          f"AND device_id = $2 "
                          f"AND token = $3 "
                          f"AND death_date > $4;",
                          token_type, device_id, token, now)
    return data


async def get_user_by_set(db: Depends, set_id: set, ):
    """Get user_id by token and device id"""
    sql_id = ""
    for i in set_id:
        sql_id = f"{sql_id} user_id={i} OR"
    sql_id = sql_id[0: -3]
    data = await db.fetch(f"SELECT * FROM users "
                          f"WHERE{sql_id};")
    return data


async def get_user_id_by_token(db: Depends, token_type: str, token: str):
    """Get user_id by token and device id"""
    now = datetime.datetime.now()
    data = await db.fetch(f"SELECT user_id, death_date FROM token "
                          f"WHERE token_type = $1 "
                          f"AND token = $2 "
                          f"AND death_date > $3;",
                          token_type, token, now)
    return data


async def update_vehicle(db: Depends, vehicle_id: int,
                         front_rim_diameter: int, front_aspect_ratio: int, front_section_width: int,
                         rear_rim_diameter: int, rear_aspect_ratio: int, rear_section_width: int):
    """We are update wheels params of vehicle with vehicle_id"""
    data = await db.fetch(f"UPDATE vehicle SET front_rim_diameter=$1, front_aspect_ratio=$2, front_section_width=$3, "
                          f"rear_rim_diameter=$4, rear_aspect_ratio=$5, rear_section_width=$6 "
                          f"WHERE vehicle_id=$7;", front_rim_diameter, front_aspect_ratio,
                          front_section_width, rear_rim_diameter, rear_aspect_ratio, rear_section_width, vehicle_id)
    return data


# Обновляем информацию
async def update_inform(db: Depends, name: str, data, table: str, id_name: str, id_data):
    await db.fetch(f"UPDATE {table} SET {name}=$1 WHERE {id_name}=$2;",
                   data, id_data)


# Обновляем информацию
async def update_user(db: Depends, name: str, surname: str, email: str, get_push: bool, get_email: bool, user_id: int):
    now = datetime.datetime.now()
    await db.fetch(f"UPDATE users SET name=$1, surname=$2, email=$3, get_push=$4, get_email=$5, last_active=$6 "
                   f"WHERE user_id=$7;",
                   name, surname, email, get_push, get_email, int(time.mktime(now.timetuple())), user_id)


# Обновляем информацию
async def update_user_active(db: Depends, user_id: int):
    now = datetime.datetime.now()
    await db.fetch(f"UPDATE all_users SET last_active=$1 WHERE user_id=$2;",
                   int(time.mktime(now.timetuple())), user_id)


async def read_data(db: Depends, table: str, id_name: str, id_data, order: str = '', name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name} = $1{order};", id_data)
    return data


async def read_data_without(db: Depends, table: str, id_name: str, id_data, order: str = '', name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name} != $1{order};", id_data)
    return data


async def read_users(db: Depends, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM users ORDER BY user_id;", )
    return data


async def read_admin_vehicles(db: Depends):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM vehicle ORDER BY vehicle_id;", )
    return data


async def read_admin_ss(db: Depends):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM service_session ORDER BY session_id DESC;", )
    return data


async def read_review(db: Depends, session_id: int, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM review WHERE session_id = $1 AND status = 'active' ORDER BY session_id;",
                          session_id)
    return data


async def read_service_session(db: Depends, client_id: int, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM service_session WHERE client_id = $1 AND status = 'active' "
                          f"ORDER BY session_id;",
                          client_id)
    return data


async def read_vehicles(db: Depends, user_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM vehicle WHERE owner_id = $1 AND status = 'active' ORDER BY vehicle_id;",
                          user_id)
    return data


async def read_all(db: Depends, table: str, order: str):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM {table} ORDER BY {order};", )
    return data


# Удаляем токены
async def delete_old_tokens(db: Depends):
    now = datetime.datetime.now()
    await db.execute(f"DELETE FROM token WHERE death_date < $1", now)


# Удаляем токены
async def delete_all_tokens_with_device_id(db: Depends, device_id: str):
    await db.execute(f"DELETE FROM token WHERE device_id = $1", device_id)


# Удаляем все записи из таблицы по ключу
async def delete_where(db: Depends, table: str, id_name: str, data):
    await db.execute(f"DELETE FROM {table} WHERE {id_name} = $1", data)


# Удаляем все записи из таблицы
async def delete_from_table(db: Depends, table: str):
    await db.execute(f"DELETE FROM {table};")
