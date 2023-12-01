import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Contractor, WithdrawalInvoice
from lib.response_examples import *
from lib.routes.admins.admin_routes import check_con_owner_or_admin
from lib.sql_create_tables import data_b, app
import stripe

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server

ip_auth_server = os.environ.get("IP_AUTH_SERVER")
ip_auth_port = os.environ.get("PORT_AUTH_SERVER")

auth_url = f"http://{ip_auth_server}:{ip_auth_port}"

str_secret = os.environ.get("STRIPE_SECRET")

stripe.api_key = str_secret


@app.post(path='/withdrawal', tags=['Payment'], responses=create_payment_res)
async def create_new_payment(access_token: str, contractor_id: int, db=Depends(data_b.connection)):
    """Create new withdrawal for contractor"""

    user_id = await check_con_owner_or_admin(access_token=access_token, co_id=contractor_id, db=db)
    if type(user_id) != int:
        return user_id
    payments_data = await conn.read_payments_for_withdrawal(db=db, contractor_id=contractor_id)
    if not payments_data:
        return JSONResponse(content={"ok": False, "description": "Haven't payments for withdrawal", }, status_code=400)

    co_data = await conn.read_data(db=db, table="contractor", name="owner_id", id_name="contractor_id",
                                   id_data=contractor_id)
    co: Contractor = Contractor.parse_obj(co_data[0])

    wi_data = await conn.create_withdrawal_invoice(db=db, contractor_id=contractor_id, user_id=user_id,
                                                   acc_num=co.acc_num, vat_number=co.vat_number, sort_code=co.sort_code,
                                                   post_code=co.post_code, beneficiary_name=co.beneficiary_name)

    wi_invoice: WithdrawalInvoice = WithdrawalInvoice.parse_obj(wi_data[0])
    for one in payments_data:
        _wi_data = await conn.create_withdrawal(db=db, wi_id=wi_invoice.wi_id, amount=one["amount"],
                                                currency=one["currency"], contractor_id=contractor_id,
                                                pay_id=one["pay_id"])
        await conn.update_inform(db=db, table="payments", id_name="pay_id", id_data=one["pay_id"], name="withdrawal_id",
                                 data=_wi_data[0][0])

    return JSONResponse(content={"ok": True,
                                 "wi_invoice": await wi_invoice.to_json(db=db, ),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
