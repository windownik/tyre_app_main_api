from starlette.responses import HTMLResponse

from lib import sql_create_tables as conn
from lib.sql_create_tables import data_b, app


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")
    await conn.create_user_table(db=connect)
    await conn.create_photo_table(db=connect)
    await conn.create_worker_table(db=connect)
    await conn.create_review_table(db=connect)
    await conn.create_vehicle_table(db=connect)
    await conn.create_payments_table(db=connect)
    await conn.create_push_logs_table(db=connect)
    await conn.create_withdrawal_table(db=connect)
    await conn.create_contractor_table(db=connect)
    await conn.create_work_types_table(db=connect)
    await conn.create_session_works_table(db=connect)
    await conn.create_service_session_table(db=connect)
    # await conn.create_user_in_contractor_table(db=connect)
    print('Create all tables')


def generate_html_response():
    html_content = """
    <html>
        <head>
            <title>Start page</title>
        </head>
        <body>
            <h2>Documentation for Tyre App main API</h2>
            <p><a href="/docs">Documentation Swager</a></p>
            <p><a href="/redoc">Documentation from reDoc</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get('/', response_class=HTMLResponse, tags=['Auth'])
async def main_page():
    """main page"""
    return generate_html_response()

