import datetime

from fpdf import FPDF, Align


def create_file_pdf(data: tuple, invoice_id: int, co_name: str, address: str):
    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.add_font("Montserrat", '', "Montserrat-Medium.ttf")
    pdf.add_font("lite", '', "Montserrat-Light.ttf")
    pdf.set_font("Montserrat", "", 22)
    pdf.cell(100, 10, f"Withdrawal invoice #{invoice_id}", ln=True)
    pdf.set_font("lite", "", 12)
    pdf.cell(100, 8, f"Contractor's name: {co_name}", ln=True)
    pdf.cell(195, 8, f"Address: {address}", ln=True)
    worker_id = 0
    session_id = 0
    for payment in data:
        if worker_id != payment["worker_id"]:
            worker_id = payment["worker_id"]
            pdf = write_for_one_user(pdf=pdf, name=payment["worker_name"], )
        if session_id != payment["session_id"]:
            session_id = payment["session_id"]
            pdf = write_session_data(pdf=pdf, data=payment, )
        pdf = write_headers(pdf)
        pdf = write_body(pdf=pdf, data=payment)
        pdf.cell(100, 8, ln=True)
        pdf.cell(195, 0.5, border=1, ln=True)
        pdf.cell(100, 5, ln=True)

    pdf.output("invoice.pdf")


def write_for_one_user(pdf: FPDF, name: str) -> FPDF:
    pdf.set_font("Montserrat", "", 16)
    pdf.cell(120, 20, f"Driver's name:  {name}", ln=True)
    pdf.cell(195, 0.5, border=1, ln=True)
    return pdf


def write_session_data(pdf: FPDF, data: dict) -> FPDF:
    range = data['distant'] / 1609.34

    pdf.set_font("Montserrat", "", 12)
    pdf.cell(150, 8, f"Session ID # {data['session_id']}", ln=True)
    pdf.set_font("lite", "", 10)
    pdf.cell(150, 6, f"Vehicle reg number:  {data['reg_num']}", ln=True)
    pdf.cell(150, 6, f"Vehicle:  {data['make']} {data['model']}", ln=True)
    pdf.cell(150, 6, f"Vehicle year:  {data['year']}", ln=True)
    pdf.cell(150, 6, f"Tyre size, Front:  {data['front_section_width']}/ {data['front_aspect_ratio']} "
                     f"R{data['front_rim_diameter']},  Rear: {data['rear_section_width']}/ {data['rear_aspect_ratio']} "
                     f"R{data['rear_rim_diameter']}",
             ln=True)
    pdf.cell(150, 6, f"Client:  {data['name']} {data['surname']}, tel. {data['phone']}", ln=True)
    pdf.cell(150, 6, f"Distance between client and customer:  {round(range, 3)} miles", ln=True)
    pdf.cell(150, 6, f"Client:  {data['name']} {data['surname']}, tel. {data['phone']}", ln=True)
    # pdf.cell(100, 10, ln=True)
    return pdf


def write_headers(pdf: FPDF) -> FPDF:
    pdf.set_font("Montserrat", "", 12)
    pdf.cell(150, 8, "Works in service session", align=Align.L, ln=True)
    pdf.set_font("lite", "", 10)
    pdf.cell(10, 6, "ID", border=1, align=Align.C)
    pdf.cell(100, 6, "Work description", border=1, align=Align.C)
    pdf.cell(20, 6, "Currency", border=1, align=Align.C)
    pdf.cell(20, 6, "Amount", border=1, align=Align.C)
    pdf.cell(45, 6, "Pay date", border=1, align=Align.C, ln=True)
    return pdf


def write_body(pdf: FPDF, data: dict) -> FPDF:
    dtime = datetime.datetime.utcfromtimestamp(data["pay_date"])
    pdf.set_font("lite", "", 10)
    pdf.cell(10, 6, str(data["pay_id"]), border=1, align=Align.C)
    pdf.cell(100, 6, "Work description", border=1, align=Align.C)
    pdf.cell(20, 6, data["currency"], border=1, align=Align.C)
    pdf.cell(20, 6, str(data["amount"] / 100), border=1, align=Align.C)
    pdf.cell(45, 6, str(dtime), border=1, align=Align.C, ln=True)
    return pdf
