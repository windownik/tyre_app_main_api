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
    delete_date: str
    create_date: str


class ServiceSession(BaseModel):
    session_id: int
    client_id: int
    worker_id: int
    contractor_id: int
    vehicle_id: int
    wheel_fr: int
    wheel_fl: int
    wheel_rr: int
    wheel_rl: int
    description: str
    status: str
    session_type: str
    session_date: int
    create_date: int

    async def to_json(self, db: Depends):
        res = self.dict()
        review_data = await conn.read_review(db=db, session_id=self.session_id)
        review_list = []
        services_list = []
        for one in review_data:
            review = Review.parse_obj(one)
            review_list.append(review)

        res['reviews'] = review_list
        res['services_session_list'] = services_list
        return res
