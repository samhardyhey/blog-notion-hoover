import os

from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.prompt import PromptTemplate

load_dotenv()

_PROMPT_TEMPLATE = """You are an expert professor specialized in emerging machine learning technologies.
You are to classify whether the following text:
{text}
Is likely to relate to machine learning or not. Please provide one of two answers: is_ml_related, is_not_ml_related.
"""

prompt = PromptTemplate(input_variables=["text"], template=_PROMPT_TEMPLATE)
llm = OpenAI(
    model_name="text-davinci-003",
    temperature=0,
    openai_api_key=os.environ["OPEN_API_KEY"],
)
chain = LLMChain(llm=llm, prompt=prompt)
