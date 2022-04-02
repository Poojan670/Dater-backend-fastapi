from enum import Enum
import database
import schemas
from random import choice
import string


class OTPType(str, Enum):
    phone = "Phone"
    email = "Email"


def random(digits: int):
    chars = string.digits
    return "".join(choice(chars) for _ in range(digits))
