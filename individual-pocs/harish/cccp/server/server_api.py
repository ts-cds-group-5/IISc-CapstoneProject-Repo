#readme: use below command to run fastapi server backemd
# fastapi dev /Users/achappa/devhak/cccp/server/server_api.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from mspb_model import load_phi_2_model, get_text_generator, generate_text
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
#from langchain_community.llms import huggingface_pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser

#Use LLMChain from langchain to create a chain with the prompt template and the model

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


#define task template for structured output
def task_template(instruction: str) -> str:
    
    task_template = '''You are a friendly chatbot assistant that gives structured output.
    Your role is to arrange the given task in this structure.
    ### instruction:\n{instruction}\n\nOutput:###Response:\n'''

    prompt1 = PromptTemplate.from_template(task_template)

    return prompt1


model, tokenizer = load_phi_2_model()
plmspb = get_text_generator(model, tokenizer) #pipeline object for mspb model
hfpl = HuggingFacePipeline(pipeline=plmspb)


@app.post("/generate")
async def generate_text_phi2(request: Request):
    data = await request.json()

    prompt = data.get("prompt", "")
    formatted_prompt = task_template(prompt)
    print(f"Received prompt: {prompt}")
    print(f"Formatted prompt: {formatted_prompt}")
    if not prompt:
        return {"error": "Prompt is required"}
    
    chain = prompt | hfpl | StrOutputParser()

    result = chain.invoke({"instruction": "Explain the importance of a good prompt."})
    print(f"Chain result: {result}")

    generated_text = generate_text(formatted_prompt, hfpl)
    print(f"Generated text: {generated_text}")


    return {"generated_text": generated_text} #change this to result


#create a post endpoint to handle chat messages
# @app.post("/chat", response_model=ChatResponse)
# async def handle_chat_message(message: ChatMsg):
    
#     # Here you would typically process the message and generate a response
#     gen2 = init_chat_model(model, tokenizer=tokenizer,temperature=0.2)
#     gen2.invoke(generated_text)

#     generator = get_text_generator(model, tokenizer)
#     generated_text = generator(message.message, max_length=256, num_return_sequences=1)
#     response_content = generated_text[0]['generated_text']
    
#     #response_content = f"{message.user_id}: {message.message}"
#     info = f"User has sent the following prompt: {message.message}"
#     print(info)
#     return ChatResponse(response=response_content, status="success")
