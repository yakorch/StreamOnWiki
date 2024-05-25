import pydantic


class PageInformation(pydantic.BaseModel):
    page_id: int
    uri: str
    title: str


class ActiveUser(pydantic.BaseModel):
    user_id: int
    user_name: str
    num_created_pages: int
