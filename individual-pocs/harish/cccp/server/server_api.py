#readme: use below command to run fastapi server backemd
# fastapi dev /Users/achappa/devhak/cccp/server/server_api.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from mspb_model import load_phi_2_model, get_text_generator, generate_text
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains.llm import LLMChain
from langchain_community.llms import HuggingFacePipeline
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser,PydanticToolsParser
from langchain_core.tools import tool
import re
import sys
import os

# Add parent directory to path to import logging_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import setup_logging, get_logger

# Setup logging
logger = get_logger("server_api")
setup_logging()


#Use LLMChain from langchain to create a chain with the prompt template and the model

app = FastAPI()

class ChatMsg(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
#+++++++++++++++++++
@app.get("/")
async def root():
    return {"message": "Hello World"}
#+++++++++++++++++++

#+++++++++++++++++++
#define task template for structured output
def task_template(instruction: str) :
    logger.info(f"Creating task template for instruction: {instruction}")
    task_template = '''You are a friendly chatbot assistant that gives structured output.
    Your role is to arrange the given task in this structure.
    ### instruction:\n{instruction}\n\nOutput:###Response:\n'''    
    return task_template.format(instruction=instruction)
#+++++++++++++++++++
OLLAMA_LLAMA3 = "/Users/achappa/.ollama/models/llama3.2:latest"
inp_model_name = "microsoft/phi-2"

#load the model and tokenizer, set up a pipeline and HuggingFacePipeline
model, tokenizer = load_phi_2_model(inp_model_name)
plmspb = get_text_generator(model, tokenizer) #pipeline object for mspb model
hfpl = HuggingFacePipeline(pipeline=plmspb)

#+++++++++++++++++++
#tool function to multiply two numbers
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two numbers and returns the result."""
    logger.debug(f"Inside multiply tool with a: {a}, b: {b} and types {type(a)}, {type(b)}")
    try:
        logger.info(f"Multiplying {a} and {b}")
        z = a / b
    except Exception as e:
        logger.error(f"Error multiplying numbers: {e}")
        raise ValueError(f"Error multiplying numbers: {e}")
    logger.info(f"Result of multiplying {a} and {b} is {z}")
    #use the task template to format the output and return the result

    return z
#+++++++++++++++++++

#+++++++++++++++++++
@app.post("/generate")
async def generate_text_phi2(request: Request):
    data = await request.json()

    prompt = data.get("prompt", "")
    formatted_prompt = task_template(prompt)
    logger.info(f"Received prompt: {prompt}")
    logger.debug(f"Formatted prompt: {formatted_prompt}")

    multiply_pattern = re.compile(
        r"multiply\s+(\d+)\s*(?:and|by|with)?\s*(\d+)", re.IGNORECASE
    )
    logger.debug(f"Regex pattern: {multiply_pattern}")
    match = multiply_pattern.search(formatted_prompt)
    logger.debug(f"Regex match: {match}")
    
    if match:
        a, b = int(match.group(1)), int(match.group(2))
        logger.debug(f"Extracted numbers - type(a): {type(a)}, type(b): {type(b)}, a: {a}, b: {b}")
        #call the multiply tool and format using task template
        result = multiply.invoke({"a":a, "b":b})

        #format response using task template
        response = f"The result of multiplying {a} and {b} is {result}"
        return {"response": response, "tool_used": "multiply", "result": result}
        #return task_template.format(instruction=result)
    else:
        prompt = ChatPromptTemplate.from_template(formatted_prompt)
    
        if not formatted_prompt:
            return {"error": "Prompt is required"}
        
    #call the model using HuggingFace pipeline, LLMChain and StrOutputParser
        chain =  hfpl | StrOutputParser()
        result = chain.invoke(formatted_prompt)
        logger.info(f"Chain result: {result}")

    #    generated_text = generate_text(formatted_prompt, hfpl)
    #    logger.debug(f"Generated text: {generated_text}")

    return {"generated_text": result} #change this to result
#+++++++++++++++++++

# Example: Add multiply_tool to a tools list for your chain/model
tools = [multiply]

# You can now use this tools list with LangGraph chains or agents as needed.
# For example, if you use an agent or chain that accepts tools:
#define a langraph agent

@app.post("/tools/multiply")
async def execute_multiply(request: Request):
    data = await request.json()
    a = data.get("a",0)
    b = data.get("b",0)
    
    try:
        a = int(a)
        b = int(b)
        logger.info(f"Executing multiply tool with a={a}, b={b}")
        result = multiply(a,b)
        logger.info(f"Multiply tool result: {result}")
        return {"result": result, "status": "success"}
    except ValueError as e:
        logger.error(f"ValueError in multiply tool: {e}")
        return {"error": "Invalid input. Please provide integers for a and b.", "status": "error"}
    except Exception as e:
        logger.error(f"Exception in multiply tool: {e}")
        return {"error": str(e), "status": "error"}



#tools = [multiply]



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
