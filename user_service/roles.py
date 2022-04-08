from asyncio.log import logger
from fastapi import Depends, HTTPException
import schemas
from hashing import Hash
from routers.oauth2 import get_current_user
from typing import List


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self,
                 user: schemas.User = Depends(get_current_user)):
        role = user['role']
        if role not in self.allowed_roles:
            logger.debug(
                f"User with role {role} not in {self.allowed_roles}")
            raise HTTPException(
                status_code=403, detail="Operation not permitted")


allow_create_resource = RoleChecker(["Admin"])
