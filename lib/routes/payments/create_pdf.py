from fpdf import FPDF, Align


def create_file_pdf(data: tuple):
    pdf = FPDF("L", "mm", "A4")
    pdf.add_page()
    pdf.add_font("Montserrat", '', "Montserrat-Medium.ttf")
    pdf.set_font("Montserrat", "", 22)
    pdf.cell(100, 30, "Withdrawal invoice", ln=True)
    pdf = write_headers(pdf)
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

    pdf.output("invoice.pdf")


def write_for_one_user(pdf: FPDF, name: str) -> FPDF:
    pdf.set_font("Montserrat", "", 18)
    pdf.cell(100, 20, name, ln=True)
    pdf.cell(1000, 2, border=1,)
    return pdf


def write_session_data(pdf: FPDF, data: dict) -> FPDF:
    pdf.set_font("Montserrat", "", 14)
    pdf.cell(150, 10, f"Session ID #{data['session_id']}", ln=True)
    pdf.cell(150, 10, f"Vehicle reg number: {data['reg_num']}", ln=True)
    pdf.cell(150, 10, f"Vehicle: {data['make']} {data['model']}", ln=True)
    pdf.cell(150, 10, f"Vehicle year: {data['year']}", ln=True)
    pdf.cell(150, 10, f"Tyre size, Front: {data['front_section_width']}/ {data['front_aspect_ratio']} "
                      f"R{data['front_rim_diameter']}, Rear: {data['rear_section_width']}/ {data['rear_aspect_ratio']} "
                      f"R{data['rear_rim_diameter']}",
             ln=True)
    pdf.cell(150, 10, f"Client: {data['name']} {data['surname']}, tel. {data['phone']}", ln=True)
    pdf.cell(100, 10, )
    return pdf


def write_headers(pdf: FPDF) -> FPDF:
    pdf.set_font("Montserrat", "", 12)
    pdf.cell(15, 10, "ID", border=1, align=Align.C)
    pdf.cell(100, 10, "Work description", border=1, align=Align.C)
    pdf.cell(30, 10, "Currency", border=1, align=Align.C)
    pdf.cell(30, 10, "Amount", border=1, align=Align.C)
    pdf.cell(30, 10, "Pay date", border=1, align=Align.C)
    return pdf


def write_body(pdf: FPDF, data: dict) -> FPDF:
    pdf.set_font("Montserrat", "", 12)
    pdf.cell(15, 10, data["pay_id"], border=1, align=Align.C)
    pdf.cell(100, 10, "Work description", border=1, align=Align.C)
    pdf.cell(30, 10, data["currency"], border=1, align=Align.C)
    pdf.cell(30, 10, data["amount"], border=1, align=Align.C)
    pdf.cell(30, 10, data["pay_date"], border=1, align=Align.C)
    return pdf


