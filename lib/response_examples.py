access_token_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'access_token': 'fFsok0mod3y5mgoe203odk3f',
                                  'refresh_token': 'e45wfknwfooii3n43948unf3n932k'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'bad refresh token or device_id, please login'}
                    },
                }
            }
        }
    },
}

get_login_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'access_token': 'fFsok0mod3y5mgoe203odk3f',
                                  'refresh_token': 'e45wfknwfooii3n43948unf3n932k'}
                    },
                }
            }
        }
    },
    400: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'SMS code is too old'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'No user with this phone number, device_id or bad sms_cod'}
                    },
                }
            }
        }
    },
}

post_create_account_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'access_token': 'fFsok0mod3y5mgoe203odk3f',
                                  'refresh_token': 'e45wfknwfooii3n43948unf3n932k'}
                    },
                }
            }
        }
    },
    400: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'Reason'}
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'No user with this phone number, device_id or bad sms_cod'}
                    },
                }
            }
        }
    },
}

get_user_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user': {
                                      "user_id": 1,
                                      "name": "Mikita",
                                      "surname": "Mislivets",
                                      "phone": 123,
                                      "email": "0",
                                      "user_type": "client",
                                      "status": "active",
                                      "lat": 0,
                                      "long": 0,
                                      "last_active": 1697447161,
                                      "createdate": 1697019389
                                  },
                                  }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': "bad access token or device_id, please login"}
                    },
                }
            }
        }
    },
}

get_user_id_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            'user_id': 1
                        }
                    },
                }
            }
        }
    },
}

get_logout_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'description': 'You successful logout'
                                  }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': "bad refresh token or device_id, please login"}
                    },
                }
            }
        }
    },
}

get_create_code_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'description': 'Check your phone number', }
                    },
                }
            }
        }
    },
    400: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'Cant create, write to the admin.', }
                    },
                }
            }
        }
    },
}

delete_user_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'description': 'User account is deleted', }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'You have bad refresh token or device_id, please login', }
                    },
                }
            }
        }
    },
}

get_vehicle_from_api_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            "vehicle": {
                                "reg_num": "1M14 111",
                                "make": "BMW",
                                "model": "520D M SPORT AUTO",
                                "year": "2014",
                                "tyre_variants": [
                                    {
                                        "name_front": "245/50R18",
                                        "name_rear": "245/50R18",
                                        "front_rim_diameter": 18,
                                        "front_aspect_ratio": 50,
                                        "front_section_width": 245,
                                        "rear_rim_diameter": 18,
                                        "rear_aspect_ratio": 50,
                                        "rear_section_width": 245
                                    },
                                    {
                                        "name_front": "245/45R19",
                                        "name_rear": "275/40R19",
                                        "front_rim_diameter": 19,
                                        "front_aspect_ratio": 45,
                                        "front_section_width": 245,
                                        "rear_rim_diameter": 19,
                                        "rear_aspect_ratio": 40,
                                        "rear_section_width": 275
                                    },
                                    {
                                        "name_front": "245/40R20",
                                        "name_rear": "275/35R20",
                                        "front_rim_diameter": 20,
                                        "front_aspect_ratio": 40,
                                        "front_section_width": 245,
                                        "rear_rim_diameter": 20,
                                        "rear_aspect_ratio": 35,
                                        "rear_section_width": 275
                                    },
                                    {
                                        "name_front": "245/35R21",
                                        "name_rear": "275/30R21",
                                        "front_rim_diameter": 21,
                                        "front_aspect_ratio": 35,
                                        "front_section_width": 245,
                                        "rear_rim_diameter": 21,
                                        "rear_aspect_ratio": 30,
                                        "rear_section_width": 275
                                    }
                                ]
                            }
                        }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'You have bad access token or device_id, please login', }
                    },
                }
            }
        }
    },
}

send_push_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {'ok': True, 'desc': 'successful send push'}
                    },
                }
            }
        }
    },
}

create_payment_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {'ok': True, "payment": {
                            "pay_id": 1,
                            "user_id": 3,
                            "session_id": 2,
                            "session_work_id": 2,
                            "worker_id": 0,
                            "contractor_id": 0,
                            "status": "create",
                            "intent": "wofn383c93ucn3ucniwuen",
                            "pay_date": 0,
                            "create_date": 1701154844
                        }}
                    },
                }
            }
        }
    },
}

get_ss_img_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            "session_img": {
                                "session_id": 35,
                                "photo_before": [
                                    {
                                        "file_id": 2,
                                        "file_name": "1.jpeg",
                                        "file_type": "image",
                                        "creator_id": 1,
                                        "images": [
                                            {
                                                "file_size": 1105764,
                                                "url": "http://167.235.253.89:10090/download?file_id=2"
                                            },
                                            {
                                                "file_size": 33306,
                                                "url": "http://167.235.253.89:10090/download?file_id=3"
                                            },
                                            {
                                                "file_size": 4411,
                                                "url": "http://167.235.253.89:10090/download?file_id=4"
                                            }
                                        ]
                                    }
                                ],
                                "photo_after": [
                                    {
                                        "file_id": 3,
                                        "file_name": "2.jpeg",
                                        "file_type": "image",
                                        "creator_id": 1,
                                        "images": [
                                            {
                                                "file_size": 1105764,
                                                "url": "http://167.235.253.89:10090/download?file_id=5"
                                            },
                                            {
                                                "file_size": 33306,
                                                "url": "http://167.235.253.89:10090/download?file_id=6"
                                            },
                                            {
                                                "file_size": 4411,
                                                "url": "http://167.235.253.89:10090/download?file_id=7"
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    },
                }
            }
        }
    },
}
