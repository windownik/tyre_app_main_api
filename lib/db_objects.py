import os

import requests
from fastapi import Depends
from pydantic import BaseModel
from lib import sql_connect as conn

ip_file_server = os.environ.get("IP_FILE_SERVER")
ip_file_port = os.environ.get("PORT_FILE_SERVER")

file_url = f"http://{ip_file_server}:{ip_file_port}"




class User(BaseModel):
    user_id: int
    name: str
    surname: str
    phone: int
    email: str
    user_type: str
    status: str
    lat: float
    long: float
    get_push: bool
    get_email: bool
    last_active: int
    createdate: int


class Worker(BaseModel):
    user_id: int
    contractor_id: int
    co_name: str
    login: str
    worker_name: str
    user_type: str
    status: str
    lat: float
    long: float
    get_push: bool
    last_active: int
    createdate: int


class Vehicle(BaseModel):
    vehicle_id: int
    reg_num: str
    owner_id: int
    make: str
    model: str
    year: int
    front_rim_diameter: int
    front_aspect_ratio: int
    front_section_width: int
    rear_rim_diameter: int
    rear_aspect_ratio: int
    rear_section_width: int
    status: str
    bolt_key: bool
    createdate: int


class VehicleTyreApi:
    name_front: str
    name_rear: str
    front_rim_diameter: int
    front_aspect_ratio: int
    front_section_width: int
    rear_rim_diameter: int
    rear_aspect_ratio: int
    rear_section_width: int

    def __init__(self, data: dict):
        self.name_front = data["Front"]["Tyre"]["Size"]
        self.name_rear = data["Rear"]["Tyre"]["Size"]
        self.front_rim_diameter = data["Front"]["Tyre"]["RimDiameter"]
        self.front_aspect_ratio = data["Front"]["Tyre"]["AspectRatio"]
        self.front_section_width = data["Front"]["Tyre"]["SectionWidth"]

        self.rear_rim_diameter = data["Rear"]["Tyre"]["RimDiameter"]
        self.rear_aspect_ratio = data["Rear"]["Tyre"]["AspectRatio"]
        self.rear_section_width = data["Rear"]["Tyre"]["SectionWidth"]

    def to_json(self) -> dict:
        return {
            "name_front": self.name_front,
            "name_rear": self.name_rear,
            "front_rim_diameter": self.front_rim_diameter,
            "front_aspect_ratio": self.front_aspect_ratio,
            "front_section_width": self.front_section_width,
            "rear_rim_diameter": self.rear_rim_diameter,
            "rear_aspect_ratio": self.rear_aspect_ratio,
            "rear_section_width": self.rear_section_width,
        }


class VehicleApi:
    reg_num: str
    make: str
    model: str
    year: int
    tyre_variants: list[VehicleTyreApi]

    def __init__(self, data: dict, reg_num: str):
        vehicle = data['Response']['DataItems']["VehicleDetails"]
        self.reg_num = reg_num
        self.make = vehicle['Make']
        self.model = vehicle['Model']
        self.year = vehicle['BuildYear']
        tyres = data['Response']["DataItems"]["TyreDetails"]["RecordList"]
        list_tyres = []
        for one in tyres:
            tyre_api = VehicleTyreApi(one)
            list_tyres.append(tyre_api)
        self.tyre_variants = list_tyres

    def to_json(self) -> dict:
        list_tyre_types = []
        for one in self.tyre_variants:
            list_tyre_types.append(one.to_json())
        return {
            "reg_num": self.reg_num,
            "make": self.make,
            "model": self.model,
            "year": int(self.year),
            "tyre_variants": list_tyre_types
        }


class Contractor(BaseModel):
    contractor_id: int
    owner_id: int
    co_name: str
    co_email: str
    address: str
    acc_num: str
    vat_number: str
    sort_code: str
    post_code: str
    beneficiary_name: str
    money: int
    currency: str
    status: str
    create_date: int


class Review(BaseModel):
    client_id: int
    text: str
    score: str
    status: str
    delete_date: int
    create_date: int


class WorkType(BaseModel):
    work_id: int
    name_en: str
    price: int
    currency: str
    status: str


class SessionWork(BaseModel):
    sw_id: int
    work_type_id: int
    name_en: str
    price: int
    currency: str
    wheel_fr: bool
    wheel_fl: bool
    wheel_rr: bool
    wheel_rl: bool


class PushLogs(BaseModel):
    push_id: int
    creator_id: int
    tittle: str
    short_text: str
    content_type: str
    main_text: str
    img_url: str
    users_ids: str
    create_date: int


class ServiceSession(BaseModel):
    session_id: int
    client_id: int
    worker_id: int
    contractor_id: int
    vehicle_id: int
    description: str
    status: str
    session_type: str
    session_date: int
    lat: float
    long: float
    address: str
    bolt_key: bool
    create_date: int

    async def to_json(self, db: Depends, session_work_list: list):
        res: dict = self.dict()
        review_data = await conn.read_review(db=db, session_id=self.session_id)
        if review_data:
            review: Review = Review.parse_obj(review_data[0])
            res['review'] = review.dict()
        if len(session_work_list) != 0:
            session_works_dict = []
            for one in session_work_list:
                session_works_dict.append(one.dict())
            res['session_works'] = session_works_dict
        else:
            ss_work_data = await conn.read_data(db=db, table="session_works", id_name='session_id',
                                                id_data=self.session_id)
            session_work_list = []
            for one in ss_work_data:
                session_work: SessionWork = SessionWork.parse_obj(one)
                session_work_list.append(session_work.dict())

            res['session_works'] = session_work_list
        return res


class Payment(BaseModel):
    pay_id: int
    user_id: int
    session_id: int
    session_work_id: str
    worker_id: int
    contractor_id: int
    amount: int
    currency: str
    status: str
    client_secret: str
    stripe_id: str
    withdrawal_id: int
    pay_date: int
    create_date: int


class Withdrawal(BaseModel):
    withdrawal_id: int
    pay_id: int
    wi_id: int
    contractor_id: int
    admin_user_id: int
    amount: int
    currency: str
    confirm_date: int
    create_date: int


class WithdrawalInvoice(BaseModel):
    wi_id: int
    user_id: int
    contractor_id: int
    admin_user_id: int
    acc_num: str
    vat_number: str
    sort_code: str
    post_code: str
    beneficiary_name: str
    confirm_date: int
    create_date: int

    async def to_json(self, db: Depends, ) -> dict:
        total_amount_data = await conn.read_data_sum(db=db, id_name="wi_id", id_data=self.wi_id, table="withdrawal",
                                                     sum_name='amount')
        total_amount = 0
        if total_amount_data:
            total_amount = int(total_amount_data[0][0])
        currency = "GBP"
        res = self.dict()
        res["amount"] = total_amount
        res["currency"] = currency
        return res

    async def to_json_with_withdrawals(self, db: Depends, ) -> dict and list:
        wi_data = await conn.read_data(db=db, id_name="wi_id", id_data=self.wi_id, table="withdrawal")
        total_amount = 0
        currency = "GBP"
        wi_list = []
        for one in wi_data:
            withdrawal: Withdrawal = Withdrawal.parse_obj(one)
            wi_list.append(withdrawal.dict())
            total_amount += withdrawal.amount
            currency = one["currency"]

        res = self.dict()
        res["amount"] = total_amount
        res["currency"] = currency
        return res, wi_list


class InetImage(BaseModel):
    fileSize: int
    url: str


class SPhoto:
    session_id: int
    photo_before_1: int = 0
    photo_before_2: int = 0
    photo_before_3: int = 0
    photo_before_4: int = 0
    photo_after_1: int = 0
    photo_after_2: int = 0
    photo_after_3: int = 0
    photo_after_4: int = 0

    def __init__(self, data=None, session_id: int = 0, ):
        if data is None:
            data = {}
        if session_id != 0:
            self.session_id = session_id
        else:
            self.session_id = data["session_id"]
            self.photo_before_1 = data["photo_before_1"]
            self.photo_before_2 = data["photo_before_2"]
            self.photo_before_3 = data["photo_before_3"]
            self.photo_before_4 = data["photo_before_4"]
            self.photo_after_1 = data["photo_after_1"]
            self.photo_after_2 = data["photo_after_2"]
            self.photo_after_3 = data["photo_after_3"]
            self.photo_after_4 = data["photo_after_4"]

    def dict(self) -> dict:
        photo_index_before = [self.photo_before_1, self.photo_before_2, self.photo_before_3, self.photo_before_4]
        photo_index_after = [self.photo_after_1, self.photo_after_2, self.photo_after_3, self.photo_after_4]

        photo_before = self.create_list_img(index_list=photo_index_before)
        photo_after = self.create_list_img(index_list=photo_index_after)
        res = {
            "session_id": self.session_id,
            "photo_before": photo_before,
            "photo_after": photo_after,
        }
        return {
            "ok": True,
            "session_img": res
        }

    def create_list_img(self, index_list: list[int]) -> list:
        list_images = []
        for i in index_list:
            if i == 0:
                continue
            res = requests.get(f'{file_url}/file', params={"file_id": i})
            if res.status_code == 200:
                body: dict = res.json()
                body.pop("ok")
                list_images.append(body)
        return list_images
