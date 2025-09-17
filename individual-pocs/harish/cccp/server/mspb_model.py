import torch
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
import sys
import os

# Add parent directory to path to import logging_config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logging_config import get_logger

# Setup logger for this module
logger = get_logger("mspb_model")


OLLAMA_LLAMA3 = "/Users/achappa/.ollama/models/llama3.2:latest"

#load model
def load_phi_2_model(inp_model_name):
    model_name = inp_model_name
    logger.info(f"Loading model: {model_name}")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    logger.info("Tokenizer loaded successfully")
    
    model = AutoModelForCausalLM.from_pretrained(model_name,
                                                      trust_remote_code=True,
                                                      dtype = torch.float32,
                                                      device_map='cpu',
                                                      local_files_only=True)
    logger.info("Model loaded successfully")
    return model, tokenizer

# Create a text generation pipeline using the model and tokenizer
#use prompt template to load the model

def get_text_generator(model, tokenizer):
    logger.info("Creating text generation pipeline")
    
    pl = pipeline (
        "text-generation",
        model= model,
        tokenizer=tokenizer,
        pad_token_id=tokenizer.eos_token_id,
        device_map="cpu", # Automatically use GPU if available,
        max_length=256,    # Limit token length to 256
        truncation=True,  # Enable truncation
        temperature=0.2,   # Adjust temperature for sampling
        repetition_penalty=1.2, # Penalize repetition
        do_sample=True # Enable sampling for varied text
    )
    logger.info("Text generation pipeline created successfully")
    return pl

def generate_text(prompt,generator):
    # Generate text using the pipeline
    logger.info(f"Generating text for prompt: {prompt}")
    outputs = generator(prompt, max_length=256, num_return_sequences=1)
    logger.debug(f"Generated {len(outputs)} output sequences")
    return outputs[0]['generated_text']

#create a joblib to export the model and tokenizer
# import joblib
# joblib.dump((model, tokenizer), 'phi2_model_tokenizer.joblib')

#get model and tokenizer in variables
#add exception handlgin when calling load_model
# model, tokenizer = load_phi_2_model()

# model.save_pretrained("./phi2_model")
# tokenizer.save_pretrained("./phi2_model")

#load the model and tokenizer from joblib
# model, tokenizer = joblib.load('phi2_model_tokenizer.joblib')


# def generate_text(prompt):
#     # Generate text using the pipeline
#     outputs = generator(prompt, max_length=256, num_return_sequences=1)
#     return outputs[0]['generated_text']

# Example usage
#call load_model function
# model, tokenizer = load_phi_2_model()
# #call get_text_generator with model and tokenizer
# generator = get_text_generator(model, tokenizer)
# prompt = "How should I load microsoft/phi-2 model using transformers library in local macos machine with python?"
# generated_text = generate_text(prompt)
# print(generated_text)

# Example usage
# if __name__ == "__main__":
#     model, tokenizer = load_model()
#     generator = get_generator(model, tokenizer)
#     prompt = "How should I load microsoft/phi-2 model using transformers library in local macos machine with python?"
#     print(generate_text(prompt, generator))