from src.models import ChatInputModel
from src.infrastructure.database.connection import get_db
from src.infrastructure.repositories import MessageRepository
from src.utils.load_agents import v2_load_agent
from langchain_core.messages import HumanMessage, AIMessage
from fastapi import APIRouter, Request


V2_APPOINTMENT_ROUTER = APIRouter()


@V2_APPOINTMENT_ROUTER.post("/appointment-setting/{wpp_number}")
async def chat(request: Request, chat_input: ChatInputModel, wpp_number: str):
    #template = ChatPromptTemplate.from_template("Translate the following sentence to Portuguese: {item.sentence}")
    '''prompt_val = full_prompt.invoke(
        {
            "input": "my whatsapp number is:" + wpp_number,
            "agent_scratchpad": [],
        }
    )'''
    v2_executor = v2_load_agent()
    async with get_db() as session:
        repo = MessageRepository(session)
        messages = await repo.get_messages(wpp_number)
        chat_history = [
            # *prompt_val.messages,
            *[HumanMessage(content="my whatsapp number is:" + wpp_number)],
            *[HumanMessage(content=message.content) if message.origin == "human" else AIMessage(content=message.content) for message in messages],
            HumanMessage(content=chat_input.message)
        ]
        response = await v2_executor.ainvoke({"input": chat_input.message, "chat_history": chat_history})
    await repo.add_message(wpp_number, origin="human", content=chat_input.message)
    await repo.add_message(wpp_number, origin="ai", content=response["output"])
    response = [*[{"human": message.content} if isinstance(message, HumanMessage) else {"ai": message.content} for message in chat_history], {"ai": response["output"]}]
    return response
