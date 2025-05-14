from pydantic import BaseModel, Field

class AnswerType(BaseModel):
    conclusion: str = Field(description="結論")
    detail: str = Field(description="詳細説明")

    def insert_dict(self):
        return {"conclusion": self.conclusion, "detail": self.detail}
