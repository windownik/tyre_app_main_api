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

get_devices_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'user_id': 12,
                                  'devices': [
                                      {
                                          'name': 'IPhone 12',
                                          'device_id': 'dkm1omo1m34o23m2',
                                          'last_date': '2023-09-25 13:24:05.996'
                                      },
                                      {
                                          'name': 'IPhone 15',
                                          'device_id': 'a8fvds8ve8c8',
                                          'last_date': '2023-09-24 11:23:02.1'
                                      },

                                  ]
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

check_phone_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  'description': 'This phone is not in database', }
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
                                  'description': 'This phone is in database', }
                    },
                }
            }
        }
    },
}
