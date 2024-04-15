from typing import List, Union, Any
from pydantic import BaseModel, StrictStr


class ChatInputModel(BaseModel):
    message: StrictStr
    # history: List[Any] #List[Union[HumanMessageModel, AIMessageModel]]