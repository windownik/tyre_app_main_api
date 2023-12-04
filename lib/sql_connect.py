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


async def save_worker(db: Depends, user_id: int, login: str, worker_name: str, contractor_id: int):
    """Save main users information"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO workers (user_id, contractor_id, login, worker_name, last_active, createdate) "
                          f"VALUES ($1, $2, $3, $4, $5, $6) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, contractor_id, login, worker_name,
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
                                 session_date: int, lat: float, long: float, address: str, ):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO service_session (client_id, vehicle_id, session_type, session_date, bolt_key, "
                          f"lat, long, address, create_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", client_id, vehicle_id, session_type, session_date,
                          bolt_key, lat, long, address, int(time.mktime(create_date.timetuple())))
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


async def create_contractor(db: Depends, owner_id: int, co_name: str, co_email: str, address: str, acc_num: str,
                            vat_number: str, sort_code: str, post_code: str, beneficiary_name: str, ):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO contractor (owner_id, co_name, co_email, address, "
                          f"acc_num, vat_number, sort_code, post_code, beneficiary_name, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", owner_id, co_name, co_email, address, acc_num,
                          vat_number, sort_code, post_code, beneficiary_name, int(time.mktime(create_date.timetuple())))
    return data


async def save_user_to_contractor(db: Depends, user_id: int, contractor_id: int):
    """We are create a new service session"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO user_in_contractor (contractor_id, user_id, createdate) "
                          f"VALUES ($1, $2, $3) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", contractor_id, user_id,
                          int(time.mktime(create_date.timetuple())))
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
                      push_type: str, push_msg_id: int, app_type: str):
    """We are create a new Work type for services sessions"""
    data = await db.fetch(f"INSERT INTO sending "
                          f"(user_id, title, short_text, main_text, img_url, push_type, push_msg_id, app_type) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, title, short_text, main_text, img_url,
                          push_type, push_msg_id, app_type)
    return data


async def msg_to_push_logs(db: Depends, creator_id: int, title: str, short_text: str, main_text: str, img_url: str,
                           content_type: str, users_ids: str):
    """We are create a new Work type for services sessions"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO push_logs "
                          f"(creator_id, tittle, short_text, main_text, img_url, content_type, users_ids, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", creator_id, title, short_text, main_text, img_url,
                          content_type, users_ids, int(time.mktime(create_date.timetuple())))
    return data


async def create_payment(db: Depends, user_id: int, session_id: int, session_work_id: list, intent: str, amount: int,
                         pay_id: str, currency: str):
    """We create a new payment"""
    create_date = datetime.datetime.now()
    sw_id_list = ""
    for one in session_work_id:
        sw_id_list = f"{sw_id_list},{one}"
    data = await db.fetch(f"INSERT INTO payments (user_id, session_id, session_work_id, amount, currency, "
                          f"client_secret, stripe_id, create_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, session_id, sw_id_list[1:], amount,
                          currency, intent, pay_id, int(time.mktime(create_date.timetuple())))
    return data


async def create_withdrawal_invoice(db: Depends, contractor_id: int, user_id: int, acc_num: str, vat_number: str,
                                    sort_code: str, post_code: str, beneficiary_name: str):
    """We create a new payment"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO withdrawal_invoice (user_id, contractor_id, acc_num, vat_number, sort_code, "
                          f"post_code, beneficiary_name, create_date) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", user_id, contractor_id, acc_num, vat_number,
                          sort_code, post_code, beneficiary_name, int(time.mktime(create_date.timetuple())))
    return data


async def create_withdrawal(db: Depends, wi_id: int, pay_id: int, contractor_id: int, amount: int, currency: str):
    """We create a new payment"""
    create_date = datetime.datetime.now()
    data = await db.fetch(f"INSERT INTO withdrawal (pay_id, wi_id, contractor_id, amount, currency, create_date) "
                          f"VALUES ($1, $2, $3, $4, $5, $6) "
                          f"ON CONFLICT DO NOTHING RETURNING *;", pay_id, wi_id, contractor_id, amount,
                          currency, int(time.mktime(create_date.timetuple())))
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


async def get_contractors_by_user_id(db: Depends, worker_id: int):
    """Get user_id by token and device id"""
    data = await db.fetch(f"SELECT contractor.contractor_id, contractor.owner_id, "
                          f"contractor.co_name, contractor.co_email, "
                          f"contractor.address, contractor.acc_num, "
                          f"contractor.vat_number, contractor.sort_code, "
                          f"contractor.post_code, contractor.beneficiary_name, "
                          f"contractor.money, contractor.currency, "
                          f"contractor.status, contractor.create_date "
                          f"FROM contractor JOIN user_in_contractor "
                          f"ON contractor.contractor_id = user_in_contractor.contractor_id "
                          f"WHERE user_in_contractor.user_id = $1 "
                          f"AND user_in_contractor.status = $2 "
                          f"AND contractor.status = $3;",
                          worker_id, "active", "active")
    return data


async def update_contractor(db: Depends, contractor_id: int, co_name: str, co_email: str, address: str, acc_num: str,
                            vat_number: str, sort_code: str, post_code: str, beneficiary_name: str, ):
    """We are create a new service session"""
    await db.fetch(f"UPDATE contractor SET co_name=$1, co_email=$2, address=$3, "
                   f"acc_num=$4, vat_number=$5, sort_code=$6, post_code=$7, beneficiary_name=$8 "
                   f"WHERE contractor_id = $9;", co_name, co_email, address, acc_num,
                   vat_number, sort_code, post_code, beneficiary_name, contractor_id)


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


async def read_users_for_push(db: Depends, name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM users WHERE push_token != $1 AND get_push = $2;", "0", True)
    return data


async def read_workers_for_push(db: Depends, name: str = '*'):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT {name} FROM workers WHERE push_token != $1 AND get_push = $2;", "0", True)
    return data


async def owner_read_ss(db: Depends, id_name: str, id_data):
    """Get all active workers sessions with filter """
    data = await db.fetch(f"SELECT * FROM service_session WHERE {id_name} = $1 "
                          f"AND (status = 'delivery' OR status = 'in work') ORDER BY session_id DESC;", id_data)
    return data


async def read_users(db: Depends, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM users "
                          f"WHERE user_type = 'admin' "
                          f"OR user_type = 'user' "
                          f"OR user_type = 'client' "
                          f"ORDER BY user_id;", )
    return data


async def read_payments_for_withdrawal(db: Depends, contractor_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM payments "
                          f"WHERE contractor_id = $1 "
                          f"AND status = 'paid' "
                          f"AND withdrawal_id = 0;", contractor_id)
    return data


async def read_withdrawal_invoice_payments(db: Depends, wi_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT payments.* FROM payments "
                          f"JOIN withdrawal ON withdrawal.pay_id = payments.pay_id "
                          f"WHERE withdrawal.wi_id = $1;", wi_id)
    return data


async def read_worker_withdrawal(db: Depends, worker_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT withdrawal.* FROM withdrawal "
                          f"JOIN payments ON withdrawal.pay_id = payments.pay_id "
                          f"WHERE payments.worker_id = $1;", worker_id)
    return data


async def read_withdrawal_filter(db: Depends, where_data, where_name: str, offset: int, limit: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT withdrawal.* FROM withdrawal "
                          f"JOIN payments ON withdrawal.pay_id = payments.pay_id "
                          f"WHERE payments.{where_name} = $1 ORDER BY withdrawal_id DESC LIMIT $2 OFFSET $3;",
                          where_data, limit, offset)
    return data


async def read_withdrawal_count(db: Depends, where_data, where_name: str):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT withdrawal.* FROM withdrawal "
                          f"JOIN payments ON withdrawal.pay_id = payments.pay_id "
                          f"WHERE payments.{where_name} = $1;",
                          where_data)
    return data


async def read_workers(db: Depends, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT workers.*, contractor.co_name "
                          f"FROM workers JOIN contractor "
                          f"ON workers.contractor_id = contractor.contractor_id "
                          f"ORDER BY workers.user_id;", )
    return data


async def read_contractors_workers(db: Depends, contractor_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT workers.*, contractor.co_name "
                          f"FROM workers JOIN contractor "
                          f"ON workers.contractor_id = contractor.contractor_id "
                          f"WHERE workers.contractor_id = $1 ORDER BY workers.user_id;", contractor_id)
    return data


async def get_workers_by_set(db: Depends, set_id: set, ):
    """Get user_id by token and device id"""
    sql_id = ""
    for i in set_id:
        sql_id = f"{sql_id} workers.user_id={i} OR"
    sql_id = sql_id[0: -3]
    data = await db.fetch(f"SELECT workers.*, contractor.co_name "
                          f"FROM workers JOIN contractor "
                          f"ON workers.contractor_id = contractor.contractor_id "
                          f"WHERE{sql_id};")
    return data


async def get_ss_work_list_by_set(db: Depends, ss_work_id: list, ):
    """Get services_session_works by token and device id"""
    sql_id = ""
    for i in ss_work_id:
        if i.isdigit():
            sql_id = f"{sql_id} sw_id={i} OR"

    sql_id = sql_id[0: -3]
    print(sql_id)
    print(sql_id)
    data = await db.fetch(f"SELECT * FROM session_works WHERE{sql_id};")
    return data


async def read_admin_vehicles(db: Depends):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM vehicle ORDER BY vehicle_id;", )
    return data


async def read_admin_ss(db: Depends):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM service_session ORDER BY session_id DESC;", )
    return data


async def read_workers_ss(db: Depends, worker_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM service_session WHERE worker_id = $1 "
                          f"AND (status = 'delivery' OR status = 'in work') "
                          f"ORDER BY session_id DESC;", worker_id)
    return data


async def read_workers_contractors(db: Depends, worker_id: int):
    """Получаем актуальные события"""
    data = await db.fetch(f"""SELECT contractor.* FROM contractor JOIN user_in_contractor ON 
                            contractor.contractor_id = user_in_contractor.contractor_id 
                            WHERE user_in_contractor.user_id = $1 
                            AND contractor.status = 'active';
                            """, worker_id)
    return data


async def read_review(db: Depends, session_id: int, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM review WHERE session_id = $1 AND status = 'active' ORDER BY session_id;",
                          session_id)
    return data


async def read_service_session(db: Depends, client_id: int, ):
    """Получаем актуальные события"""
    data = await db.fetch(f"SELECT * FROM service_session WHERE client_id = $1 AND (status = 'active' "
                          f"OR status = 'search') "
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


async def read_all_offset(db: Depends, table: str, order: str, limit: int, offset: int, ):
    """Получаем актуальные данные"""
    data = await db.fetch(f"SELECT * FROM {table} ORDER BY {order} LIMIT {limit} OFFSET {offset};", )
    return data


async def read_all_count(db: Depends, table: str,):
    """Получаем актуальные данные"""
    data = await db.fetch(f"SELECT COUNT(*) FROM {table};",)
    return data


async def read_data_offset(db: Depends, table: str, order: str, limit: int, offset: int, id_name: str,
                           id_data: str | int):
    """Получаем актуальные данные"""
    data = await db.fetch(f"SELECT * FROM {table} WHERE {id_name} = $1 ORDER BY {order} "
                          f"LIMIT {limit} OFFSET {offset};", id_data)
    return data


async def read_data_count(db: Depends, table: str, id_name: str, id_data: str | int):
    """Получаем актуальные данные"""
    data = await db.fetch(f"SELECT COUNT(*) FROM {table} WHERE {id_name} = $1;", id_data)
    return data


async def read_worker_payments(db: Depends, worker_id: int, contractor_id: int = 0):
    """Read workers payments with date filter"""
    sql = "worker_id"
    if contractor_id != 0:
        sql = "contractor_id"
        worker_id = contractor_id
    data = await db.fetch(f"SELECT payments.* FROM payments JOIN service_session "
                          f"ON payments.session_id = service_session.session_id "
                          f"WHERE service_session.status = 'success' "
                          f"AND payments.{sql} = $1 AND payments.withdrawal_id = 0"
                          f"ORDER BY payments.pay_id;", worker_id)
    return data


async def read_service_session_archive(db: Depends, contractor_id: int, worker_id: int, offset: int, limit: int, ):
    """Get all sessions with filters"""
    sql = "worker_id"
    if contractor_id != 0:
        sql = "contractor_id"
        worker_id = contractor_id

    data = await db.fetch(f"SELECT * FROM service_session WHERE {sql} = $1 "
                          f"ORDER BY session_id DESC OFFSET $2 LIMIT $3;",
                          worker_id, offset, limit)
    return data


async def count_service_session_archive(db: Depends, contractor_id: int, worker_id: int, ):
    """Get all sessions with filters"""
    sql = "worker_id"
    if contractor_id != 0:
        sql = "contractor_id"
        worker_id = contractor_id

    data = await db.fetch(f"SELECT COUNT(*) FROM service_session WHERE {sql} = $1;",
                          worker_id, )
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
