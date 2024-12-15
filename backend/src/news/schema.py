from pydantic import BaseModel


class NewsSummaryRequestSchema(BaseModel):
    content: str


class PromptRequest(BaseModel):
    prompt: str
