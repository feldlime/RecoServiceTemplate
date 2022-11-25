from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


@app.get("/health")
async def root():
    return "36.6"


@app.get("/reco/{model_name}/{user_id}", response_model=RecoResponse)
async def get_reco(model_name: str, user_id: int):
    if model_name == "mmm":
        reco_list = list(range(10))
    else:
        reco_list = list(range(10))[::-1]

    reco = RecoResponse(
        user_id=user_id,
        items=reco_list
    )
    return reco
