import os

from fastapi_asyncpg import configure_asyncpg
from lib.app_init import app

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


# Create new connection with database
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
 get_push BOOL DEFAULT true,
 get_email BOOL DEFAULT false,
 push_token TEXT DEFAULT '0',
 last_active BIGINT DEFAULT 0,
 createdate BIGINT
 )''')


async def create_worker_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS workers (
 user_id BIGINT PRIMARY KEY,
 contractor_id BIGINT DEFAULT 0,
 login VARCHAR(100) DEFAULT '0',
 worker_name VARCHAR(100) DEFAULT '0',
 user_type VARCHAR(20) DEFAULT 'worker',
 status VARCHAR(20) DEFAULT 'active',
 lat DOUBLE PRECISION DEFAULT 0,
 long DOUBLE PRECISION DEFAULT 0,
 get_push BOOL DEFAULT true,
 push_token TEXT DEFAULT '0',
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
 co_email VARCHAR(100) DEFAULT '0',
 address TEXT DEFAULT '0',
 acc_num TEXT DEFAULT '0',
 vat_number TEXT DEFAULT '0',
 sort_code TEXT DEFAULT '0',
 post_code TEXT DEFAULT '0',
 beneficiary_name TEXT DEFAULT '0',
 money BIGINT DEFAULT 0,
 currency VARCHAR(20) DEFAULT 'GBP',
 status VARCHAR(20) DEFAULT 'active',
 create_date BIGINT
 )''')


async def create_user_in_contractor_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS user_in_contractor (
 id SERIAL PRIMARY KEY,
 contractor_id BIGINT DEFAULT 0,
 user_id BIGINT DEFAULT 0,
 status VARCHAR(20) DEFAULT 'active',
 delete_date BIGINT DEFAULT 0,
 create_date BIGINT DEFAULT 0
 )''')


async def create_service_session_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS service_session (
 session_id SERIAL PRIMARY KEY,
 client_id BIGINT DEFAULT 0,
 worker_id BIGINT DEFAULT 0,
 contractor_id BIGINT DEFAULT 0,
 vehicle_id BIGINT DEFAULT 0,
 description TEXT DEFAULT '0',
 status VARCHAR(20) DEFAULT 'active',
 session_type VARCHAR(20) DEFAULT 'now',
 session_date BIGINT DEFAULT 0,
 bolt_key BOOL DEFAULT false,
 lat DOUBLE PRECISION DEFAULT 0,
 long DOUBLE PRECISION DEFAULT 0,
 address TEXT DEFAULT '0',
 create_date BIGINT DEFAULT 0
 )''')


async def create_review_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS review (
 session_id BIGINT PRIMARY KEY,
 client_id BIGINT DEFAULT 0,
 text TEXT DEFAULT '0',
 score INTEGER DEFAULT 5,
 status VARCHAR(20) DEFAULT 'active',
 delete_date BIGINT DEFAULT 0,
 create_date BIGINT DEFAULT 0
 )''')


async def create_photo_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS photo (
 session_id BIGINT PRIMARY KEY,
 photo_before_1 BIGINT DEFAULT 0,
 photo_before_2 BIGINT DEFAULT 0,
 photo_before_3 BIGINT DEFAULT 0,
 photo_before_4 BIGINT DEFAULT 0,
 photo_after_1 BIGINT DEFAULT 0,
 photo_after_2 BIGINT DEFAULT 0,
 photo_after_3 BIGINT DEFAULT 0,
 photo_after_4 BIGINT DEFAULT 0
 )''')


async def create_work_types_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS work_types (
 work_id SERIAL PRIMARY KEY,
 name_en TEXT DEFAULT '0',
 price BIGINT DEFAULT 0,
 currency VARCHAR(20) DEFAULT 'GBP',
 status VARCHAR(20) DEFAULT 'active'
 )''')


async def create_session_works_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS session_works (
 id SERIAL PRIMARY KEY,
 session_id BIGINT DEFAULT 0,
 work_type_id BIGINT DEFAULT 0,
 name_en TEXT DEFAULT '0',
 price BIGINT DEFAULT 0,
 currency VARCHAR(20) DEFAULT 'GBP',
 wheel_fr BOOL DEFAULT false,
 wheel_fl BOOL DEFAULT false,
 wheel_rr BOOL DEFAULT false,
 wheel_rl BOOL DEFAULT false,
 create_date BIGINT DEFAULT 0
 )''')


async def create_push_logs_table(db):
    await db.execute(f'''CREATE TABLE IF NOT EXISTS push_logs (
 push_id SERIAL PRIMARY KEY,
 creator_id BIGINT DEFAULT 0,
 tittle TEXT DEFAULT '0',
 short_text TEXT DEFAULT '0',
 content_type TEXT DEFAULT '0',
 main_text TEXT DEFAULT '0',
 img_url TEXT DEFAULT '0',
 users_ids TEXT DEFAULT 'for_all',
 create_date BIGINT DEFAULT 0
 )''')
