from pydantic import BaseModel


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
