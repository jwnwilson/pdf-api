from pydantic import BaseModel


class UserData(BaseModel):
    user_id: str