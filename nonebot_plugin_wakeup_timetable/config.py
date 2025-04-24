
from pathlib import Path
from pydantic import BaseModel


class Config(BaseModel):
    # 以图片发送
    timetable_pic: bool = True