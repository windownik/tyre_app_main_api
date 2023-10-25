import os
from starlette.responses import HTMLResponse

from lib import sql_connect as conn
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")
    await conn.create_user_table(db=connect)
    await conn.create_photo_table(db=connect)
    await conn.create_review_table(db=connect)
    await conn.create_vehicle_table(db=connect)
    await conn.create_contractor_table(db=connect)
    await conn.create_work_types_table(db=connect)
    await conn.create_session_works_table(db=connect)
    await conn.create_service_session_table(db=connect)
    await conn.create_user_in_contractor_table(db=connect)
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

