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


async def create_service_session(db: Depends, client_id: int, vehicle_id: int, session_type: str,
                                 session_date: int):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO service_session (client_id, vehicle_id, session_type, session_date, "
                          f"create_date) VALUES ($1, $2, $3, $4, $5) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", client_id, vehicle_id, session_type, session_date,
                          int(time.mktime(create_date.timetuple())))
    return data


async def create_ss_work(db: Depends, session_id: int, work_type_id: int, name_en: str, price: int, currency: str,
                         bolt_key: bool, wheel_fr: bool, wheel_fl: bool, wheel_rr: bool, wheel_rl: bool):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO session_works (session_id, work_type_id, name_en, price, "
                          f"currency, bolt_key, wheel_fr, wheel_fl, wheel_rr, wheel_rl, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", session_id, work_type_id, name_en, price, currency,
                          bolt_key, wheel_fr, wheel_fl, wheel_rr, wheel_rl, int(time.mktime(create_date.timetuple())))
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
