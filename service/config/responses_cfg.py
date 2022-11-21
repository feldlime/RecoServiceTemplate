example_responses = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "Default reco": {
                        "summary": "Success recommendation",
                        "value": {
                            "user_id": 777,
                            "items": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                        }
                    },
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "examples": {
                    "User not found": {
                        "summary": "User_id not found",
                        "value": {
                            "error_key": "user_not_found",
                            "error_message": "User 100000000001 not found",
                            "error_loc": None
                        }
                    },
                    "Model not found": {
                        "summary": "Model name not found",
                        "value": {
                            "error_key": "model_not_found",
                            "error_message": "Model name 'model_-1' not found",
                            "error_loc": None
                        }
                    },
                }
            }
        }
    },
}
