#fastapi server backemd

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class ChatMsg(BaseModel):
    message: str
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/")
async def root():
    return {"message": "Hello World"}


#create a post endpoint to handle chat messages
@app.post("/chat", response_model=ChatResponse)
async def handle_chat_message(message: ChatMsg):
    # Here you would typically process the message and generate a response
    response_content = f"{message.user_id}: {message.message}"
    info = f"User has sent the following prompt: {message.message}"
    print(info)
    return ChatResponse(response=response_content)
