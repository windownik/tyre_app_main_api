import datetime

from fpdf import FPDF, Align

from lib.db_objects import SessionWork


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("lite", "", 10)
        self.cell(0, 10, f"Page: {self.page_no()}", align=Align.R)


def create_file_pdf(data: tuple, invoice_id: int, co_name: str, address: str, ss_w_dict: dict):
    pdf = PDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.image("tyre_app_pro.png", 10, 8, h=15)
    pdf.add_font("Montserrat", '', "Montserrat-Medium.ttf")
    pdf.add_font("lite", '', "Montserrat-Light.ttf")
    pdf.set_font("Montserrat", "", 22)
    pdf.cell(100, 15, f"", ln=True)
    pdf.cell(100, 10, f"Withdrawal invoice #{invoice_id}", ln=True)
    pdf.set_font("lite", "", 12)
    pdf.cell(100, 8, f"Contractor's name: {co_name}", ln=True)
    pdf.cell(195, 8, f"Address: {address}", ln=True)
    worker_id = 0
    session_id = 0
    amount = 0
    for payment in data:

        if session_id != payment["session_id"]:
            session_id = payment["session_id"]
            if amount != 0:
                pdf.set_font("lite", "", 10)
                pdf.cell(150, 5, f"Total Amount:  {payment['currency']} {amount}", ln=True)
                pdf.cell(100, 8, ln=True)
                pdf.cell(195, 0.5, border=1, ln=True)
                pdf.cell(100, 5, ln=True)
            if worker_id != payment["worker_id"]:
                worker_id = payment["worker_id"]
                pdf = write_for_one_user(pdf=pdf, name=payment["worker_name"], )
            pdf = write_session_data(pdf=pdf, data=payment, )
            pdf = write_headers(pdf)

            amount = 0
        amount += payment['amount'] / 100
        pdf = write_body(pdf=pdf, data=payment, ss_w_dict=ss_w_dict)
    pdf.cell(150, 5, f"Total Amount:  GBP {amount}", ln=True)
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
    pdf.cell(150, 5, f"Vehicle reg number:  {data['reg_num']}", ln=True)
    pdf.cell(150, 5, f"Vehicle:  {data['make']} {data['model']}", ln=True)
    pdf.cell(150, 5, f"Vehicle year:  {data['year']}", ln=True)
    pdf.cell(150, 5, f"Tyre size, Front:  {data['front_section_width']}/ {data['front_aspect_ratio']} "
                     f"R{data['front_rim_diameter']},  Rear: {data['rear_section_width']}/ {data['rear_aspect_ratio']} "
                     f"R{data['rear_rim_diameter']}",
             ln=True)
    pdf.cell(150, 5, f"Client:  {data['name']} {data['surname']}, tel. {data['phone']}", ln=True)
    pdf.cell(150, 5, f"Distance between client and customer:  {round(range, 3)} miles", ln=True)
    pdf.cell(150, 5, f"Client:  {data['name']} {data['surname']}, tel. {data['phone']}", ln=True)

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


def write_body(pdf: FPDF, data: dict, ss_w_dict: dict) -> FPDF:
    list_int = str(data["session_work_id"]).split(",")
    dtime = datetime.datetime.utcfromtimestamp(data["pay_date"])
    pdf.set_font("lite", "", 10)
    # pdf.cell(45, 5, data["session_work_id"], border=1, align=Align.C,)
    # pdf.cell(45, 5, str(data["amount"] / 100), border=1, align=Align.C, ln=True)
    for one in list_int:
        ss_w: SessionWork = ss_w_dict[one]

        pdf.cell(10, 5, str(ss_w.sw_id), border=1, align=Align.C)
        pdf.cell(100, 5, ss_w.name_en, border=1, align=Align.L)

        pdf.cell(20, 5, ss_w.currency, border=1, align=Align.C)
        pdf.cell(20, 5, str(ss_w.price / 100), border=1, align=Align.C)
        pdf.cell(45, 5, str(dtime), border=1, align=Align.C, ln=True)
    return pdf
