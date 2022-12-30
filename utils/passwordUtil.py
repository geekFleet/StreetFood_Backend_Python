import re
from fastapi import HTTPException


def password_regex(password: str):
    if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,12}$", password):
        raise HTTPException(status_code=400, detail="Please Provide strong Password!")
    return password
