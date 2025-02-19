import os

from dotenv import load_dotenv

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.prompt import PromptTemplate

load_dotenv()

_PROMPT_TEMPLATE = """You are subject matter expert specializing in computer science, programming and machine learning technologies.
You are to classify whether the following text:
{text}
Is likely to relate to computer science, programming or machine learning or not. Please provide one of two answers: tech, not_tech.
"""

prompt = PromptTemplate(input_variables=["text"], template=_PROMPT_TEMPLATE)
llm = OpenAI(
    model_name="text-davinci-003",
    temperature=0,
    openai_api_key=os.environ["OPEN_API_KEY"],
)
chain = LLMChain(llm=llm, prompt=prompt)
