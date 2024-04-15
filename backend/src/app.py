from src.models import ChatInputModel
from src.infrastructure.database.connection import init_models, get_db
from src.infrastructure.repositories import MessageRepository
from src.utils import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model_name="gpt-4-turbo-2024-04-09")

from langchain_community.agent_toolkits import create_sql_agent

write_query = None
agent_executor = None


examples = [
    {"input": "List all appointments.", "query": "SELECT * FROM appointment;"},
    {"input": "List all professionals.", "query": "SELECT * FROM professional;"},
    {"input": "List all messages.", "query": "SELECT * FROM message;"},
    {"input": "List all people.", "query": "SELECT * FROM person;"},
    {"input": "Update email field with value '<email_value>' of person with wpp_number <wpp_number>.", "query": "UPDATE person email = '<email_value>' WHERE wpp_number = '<wpp_number>';"},
    {"input": "Create an professional with username field with value '<username_value>'.", "query": "INSERT INTO professional (username) VALUES ('<username_value>');"},
    {"input": "List all appointments of professional '<username_value>' on the date '2024-04-15'", "query": "SELECT p.*, a.start_time, a.available FROM professional p INNER JOIN appointment a ON p.id = a.professional_id WHERE p.username = '<username_value>' AND a.start_time >= '2024-04-15 00:00:00' AND a.start_time < '2024-04-16 00:00:00';"},
    {"input": "Create an appointment of professional '<username_value>' on the datetime '2024-04-15 10:30:00' with status available", "query": "SELECT p.*, a.start_time, a.available FROM professional p INNER JOIN appointment a ON p.id = a.professional_id WHERE p.username = '<username_value>' AND a.start_time >= '2024-04-15 00:00:00' AND a.start_time < '2024-04-16 00:00:00';"},
]

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    FAISS,
    k=5,
    input_keys=["input"],
)

system_prefix = """You are an agent designed to interact with a SQL database and help people on appointment setting.
Given an input, agent must verify step by steps if the user do not provided the necessary information you ask him, agent cannot jump over steps that requires user input. You should avoid ask the user about informations already gived.
The agent must hide to user that he interacts with database, so, the user must think on agent as an real attendant and the agent will do it best to user finish the appointment setting.
when answering about query, table or database, remember that you are an attendant, a real person, and just ask for the user what he need to know to proceed with the appointment setting steps.

before go into this steps the agent must know the usual format of an email

number | Step
1 | agent verify if the person has email filled, if was not provided yet, agent should ask the user to provide email information.
2 | agent must verify email is valid and just after that should proceed to next step.
3 | user must give the username of professional, agent must create the an professional if not exists 
4 | user must give some valid date and hour | Could you provide the date and hour of expected appointment date availability?
5 | agent must check if the professional has free apointments on the given date, if not, create appointments with available setted as True with 30 minutes of distance between start_time, feed the 9am to 9pm with these informations.  
6 | agent must provide the available of professional on the given period and ask for confirmation in case of availability 
7 | user must confirm the date and agent must update the appointment with available setted as False
8 | agent must say if the appointment setting was successful 

Agent must priorize more ask for filling of fields than share the status of step, try to proceed to next step when check pass successfully.
Try always check the information needed from nexts steps and ask for the user to give the information.

When the step need agent action, try to interact with the tool to create registers on database.

create a syntactically correct PostgreSQL query to achieve the steps, only do queries when needed, do not delete any information in any kind of situation, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 30 results.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools know about database elements.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
Just query tables that already exist on the database.


"""

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=PromptTemplate.from_template(
        "User input: {input}\nSQL query: {query}"
    ),
    input_variables=["input"],
    prefix=system_prefix,
    suffix="",
)
agent_executor = None



full_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate(prompt=few_shot_prompt),
        MessagesPlaceholder(variable_name="chat_history", optional=False),
        MessagesPlaceholder("agent_scratchpad"),
    ]
)


@app.on_event("startup")
async def startup_event():
    global agent_executor
    await init_models()
    db = SQLDatabase.from_uri("postgresql://admin:admin@localhost/appointment")
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", prompt=full_prompt,verbose=True)
    

@app.post("/appointment-setting/{wpp_number}")
async def chat(chat_input: ChatInputModel, wpp_number: str):
    #template = ChatPromptTemplate.from_template("Translate the following sentence to Portuguese: {item.sentence}")
    '''prompt_val = full_prompt.invoke(
        {
            "input": "my whatsapp number is:" + wpp_number,
            "agent_scratchpad": [],
        }
    )'''
    async with get_db() as session:
        repo = MessageRepository(session)
        messages = await repo.get_messages(wpp_number)
        chat_history = [
            # *prompt_val.messages,
            *[HumanMessage(content="my whatsapp number is:" + wpp_number)],
            *[HumanMessage(content=message.content) if message.origin == "human" else AIMessage(content=message.content) for message in messages]
        ]
        print(chat_history)
        #print(input_messages)
        await repo.add_message(wpp_number, origin="human", content=chat_input.message)
        response = agent_executor.invoke({"input": chat_input.message, "chat_history": chat_history})
        await repo.add_message(wpp_number, origin="ai", content=response["output"])
    return response["output"]   
