import datetime
import os
import time

from fastapi_asyncpg import configure_asyncpg
from lib.app_init import app
from fastapi import Depends


password = os.environ.get("DATABASE_PASS")
host = os.environ.get("DATABASE_HOST")
port = os.environ.get("DATABASE_PORT")
db_name = os.environ.get("DATABASE_NAME")
secret = os.environ.get("SECRET")

password = 102015 if password is None else password
host = '127.0.0.1' if host is None else host
port = 5432 if port is None else port
db_name = 'tyre_app' if db_name is None else db_name
secret = 'secret12345' if secret is None else secret

# Создаем новую таблицу
data_b = configure_asyncpg(app, f'postgres://postgres:{password}@{host}:{port}/{db_name}')


async def create_user_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS users (
 user_id BIGINT PRIMARY KEY,
 name VARCHAR(100) DEFAULT '0',
 surname VARCHAR(100) DEFAULT '0',
 phone BIGINT UNIQUE,
 email VARCHAR(100) DEFAULT '0',
 user_type VARCHAR(20) DEFAULT 'client',
 status VARCHAR(20) DEFAULT 'active',
 lat DOUBLE PRECISION DEFAULT 0,
 long DOUBLE PRECISION DEFAULT 0,
 last_active BIGINT DEFAULT 0,
 createdate BIGINT
 )''')


async def create_vehicle_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS vehicle (
 vehicle_id SERIAL PRIMARY KEY,
 reg_num VARCHAR(100) DEFAULT 0,
 owner_id BIGINT DEFAULT 0,
 make VARCHAR(100) DEFAULT '0',
 model VARCHAR(100) DEFAULT '0',
 year INT DEFAULT 0,
 front_rim_diameter INT DEFAULT 0,
 front_aspect_ratio INT DEFAULT 0,
 front_section_width INT DEFAULT 0,
 rear_rim_diameter INT DEFAULT 0,
 rear_aspect_ratio INT DEFAULT 0,
 rear_section_width INT DEFAULT 0,
 status VARCHAR(20) DEFAULT 'active',
 bolt_key BOOL DEFAULT false,
 createdate BIGINT
 )''')


async def create_contractor_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS contractor (
 contractor_id SERIAL PRIMARY KEY,
 owner_id BIGINT DEFAULT 0,
 co_name VARCHAR(100) DEFAULT '0',
 acc_num TEXT DEFAULT '0',
 sort_code BIGINT DEFAULT 0,
 contact_name TEXT DEFAULT '0',
 address TEXT DEFAULT '0',
 postcode BIGINT DEFAULT 0,
 lat DOUBLE PRECISION DEFAULT 0,
 long DOUBLE PRECISION DEFAULT 0,
 money BIGINT DEFAULT 0,
 currency VARCHAR(20) DEFAULT 'GBP',
 status VARCHAR(20) DEFAULT 'active',
 createdate BIGINT
 )''')


async def create_user_in_contractor_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS user_in_contractor (
 id SERIAL PRIMARY KEY,
 contractor_id BIGINT DEFAULT 0,
 user_id BIGINT DEFAULT 0,
 status VARCHAR(20) DEFAULT 'active',
 delete_date BIGINT DEFAULT 0,
 createdate BIGINT DEFAULT 0
 )''')


async def create_service_session_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS service_session (
 session_id SERIAL PRIMARY KEY,
 client_id BIGINT DEFAULT 0,
 worker_id BIGINT DEFAULT 0,
 contractor_id BIGINT DEFAULT 0,
 vehicle_id BIGINT DEFAULT 0,
 wheel_fr INT DEFAULT 0,
 wheel_fl INT DEFAULT 0,
 wheel_rr INT DEFAULT 0,
 wheel_rl INT DEFAULT 0,
 description TEXT DEFAULT '0',
 status VARCHAR(20) DEFAULT 'active',
 createdate BIGINT DEFAULT 0
 )''')


# Создаем новый токен
async def save_user(db: Depends, user_id: int, name: str, surname: str, phone: int):
    create_date = datetime.datetime.now()
    token = await db.fetch(f"INSERT INTO users (user_id, name, surname, phone, createdate) "
                           f"VALUES ($1, $2, $3, $4, $5) "
                           f"ON CONFLICT DO NOTHING RETURNING *;", user_id, name, surname, phone,
                           int(time.mktime(create_date.timetuple())))
    return token


# Создаем новый токен
async def create_vehicle(db: Depends, reg_num: str, owner_id: int, make: str, model: str, year: int,
                         front_rim_diameter: int, front_aspect_ratio: int, front_section_width: int,
                         rear_rim_diameter: int, rear_aspect_ratio: int, rear_section_width: int, bolt_key: bool):
    create_date = datetime.datetime.now()
    token = await db.fetch(f"INSERT INTO vehicle (reg_num, owner_id, make, model, year, front_rim_diameter, "
                           f"front_aspect_ratio, front_section_width, rear_rim_diameter, rear_aspect_ratio, "
                           f"rear_section_width, bolt_key, createdate) "
                           f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13) "
                           f"ON CONFLICT DO NOTHING RETURNING *;", reg_num, owner_id, make, model, year,
                           front_rim_diameter, front_aspect_ratio, front_section_width, rear_rim_diameter,
                           rear_aspect_ratio, rear_section_width, bolt_key, int(time.mktime(create_date.timetuple())))
    return token


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


# Обновляем информацию
async def update_user_active(db: Depends, user_id: int):
    now = datetime.datetime.now()
    await db.fetch(f"UPDATE all_users SET last_active=$1 WHERE user_id=$2;",
                   int(time.mktime(now.timetuple())), user_id)


async def read_data(db: Depends, table: str, id_name: str, id_data, order: str = '', name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM {table} WHERE {id_name} = $1{order};", id_data)
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