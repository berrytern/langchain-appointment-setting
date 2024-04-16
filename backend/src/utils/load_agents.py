from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.messages import HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from src.utils import settings


V1_MODEL = None

def v1_load_agent():
    global V1_MODEL
    if V1_MODEL: return V1_MODEL
    llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model_name="gpt-4-turbo-2024-04-09")

    examples = [
        {"input": "List all appointments.", "query": "SELECT * FROM appointment;"},
        {"input": "Get professional by username.", "query": "SELECT * FROM professional WHERE professional.username = <username>;"},
        {"input": "Get person by wpp_number.", "query": "SELECT * FROM person WHERE person.wpp_number = <wpp_number> LIMIT 1;"},
        {"input": "Update email field with value '<email_value>' of person with wpp_number <wpp_number>.", "query": "UPDATE person email = '<email_value>' WHERE wpp_number = '<wpp_number>';"},
        {"input": "Create an professional with username field with value '<username_value>'.", "query": "INSERT INTO professional (id, username) VALUES (gen_random_uuid(), '<username_value>');"},
        {"input": "Verify if appointment on datetime is with status filled", "query": "SELECT available FROM appointment WHERE appointment.available = false and appointment.start_time = '<start_time>'::timestamp;"},
        {"input": "Verify if appointment on datetime is with status available", "query": "SELECT available FROM appointment WHERE appointment.available = true and appointment.start_time = '<start_time>'::timestamp;"},
        {"input": "List all appointments of professional '<username_value>' on the date '2024-04-15'", "query": "SELECT p.*, a.start_time, a.available FROM professional p INNER JOIN appointment a ON p.id = a.professional_id WHERE p.username = '<username_value>' AND a.start_time >= '2024-04-15 00:00:00' AND a.start_time < '2024-04-16 00:00:00';"},
        {"input": "Create an appointment of professional '<username_value>' on the datetime '2024-04-15 10:30:00' with status available", "query": "INSERT INTO appointment (id, start_time, available, professional_id)  VALUES (gen_random_uuid(), '<start_time>', true, UUID('<professional_id>'));"},
        {"input": "Create an appointment of professional '<username_value>' on the datetime '2024-04-15 10:30:00' with status filled", "query": "INSERT INTO appointment (id, start_time, available, professional_id)  VALUES (gen_random_uuid(), '<start_time>', false, UUID('<professional_id>'));"},
        {"input": "Update the appointment availability by <professional_id> and <start_date> setting status as filled", "query": "UPDATE appointment SET available = false WHERE appointment.professional_id = UUID('<professional_id>') AND appointment.start_time = '<start_time>'::timestamp; "},
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
    When answering to the user about query, table or database, remember that you are an attendant, a real person, and just ask for the user what he need to know to proceed with the appointment setting steps.
    When you need to interact with the database, do it, but you dont need to give details about that to the user.

    Roles:
    - if the information isn't on db, create it;
    - always use the database to retrieve information;
    - cannot schedule an appointment if already it is setted as not available on given date;

    Previous knowlege required:
    - know the email format looks like;
    - an attendant must be proactive and be sure the whole process is persisted on the database;

    number | Step
    1 | agent verify if the person has email filled, if was not provided yet, agent should ask the user to provide email information.
    2 | agent must verify email is valid and just after that should update on db
    3 | user must give the username of professional, agent must create the an professional if not exists 
    4 | user must give an valid date and hour | Could you provide the date and hour of expected appointment date availability?
    5 | agent must check if the professional has free apointments on the given datetime, - if has not created appointments or appointments with available setted to true agent must create the appointment and mark as filled(available = false)
      - else must say the time is already filled and provide options of available times.
    6 | agent must ask for confirmation in case of availability 
    7 | user must confirm the date and agent must update the appointment with available field setted with value False
    8 | agent must say if the appointment setting was successful


    Database interaction:
    - update email field of person with the provided email;
    - create professional if not exists on the database;
    - before create an appointment, get the related professional id;
    - create appointment if not exists on the database;

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

    When receive an email address, remember to update the email field value on table person.
    When receive an professional username, remember to check if professional exists and create it if not, it must be filled with the gen_random_uuid() value.
    When saving a new appointment, remember of the field available, it must be set to false value.

    when setting an appointment you must set available field with value seted to false.
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


    full_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=few_shot_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=False),
            HumanMessage(content="{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )
    db = SQLDatabase.from_uri("postgresql://admin:admin@"+settings.POSTGRES_HOST+"/appointment")
    V1_MODEL = create_sql_agent(llm, db=db, agent_type="openai-tools", prompt=full_prompt,verbose=True)
    return V1_MODEL

