from fastapi import Depends
from pydantic import BaseModel
from lib import sql_connect as conn


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
    acc_num: str
    sort_code: int
    contact_name: str
    address: str
    postcode: int
    lat: float
    long: float
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
