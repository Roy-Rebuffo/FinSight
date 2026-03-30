from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.core.dependencies import get_current_user
from app.core.database import get_postgres_saver, init_langgraph_tables
from app.models.user import User
from app.agent.graph import agent_graph
import json

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    thread_id: str
    # thread_id identifica la conversación. El mismo thread_id
    # permite al agente recordar mensajes anteriores.


class ChatResponse(BaseModel):
    response: str
    thread_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Endpoint principal del agente IA.
    Recibe un mensaje, lo procesa con el grafo LangGraph
    y devuelve la respuesta con memoria de conversación.
    """
    try:
        with get_postgres_saver() as checkpointer:
            # Compilamos el grafo con el checkpointer de PostgreSQL
            # Cada invocación guarda el estado en la DB automáticamente
            compiled_graph = agent_graph.compile(checkpointer=checkpointer)

            # Config identifica esta conversación específica
            config = {
                "configurable": {
                    "thread_id": request.thread_id,
                }
            }

            # Invoca el grafo con el mensaje del usuario
            result = compiled_graph.invoke(
                {
                    "messages": [HumanMessage(content=request.message)],
                    "user_id": current_user.id,
                },
                config=config,
            )

            # El último mensaje es la respuesta final del agente
            last_message = result["messages"][-1]
            response_text = last_message.content

            return ChatResponse(
                response=response_text,
                thread_id=request.thread_id,
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en el agente: {str(e)}"
        )


@router.get("/threads/{thread_id}/history")
def get_conversation_history(
    thread_id: str,
    current_user: User = Depends(get_current_user),
):
    """
    Devuelve el historial de una conversación específica.
    Útil para que el frontend recargue conversaciones anteriores.
    """
    try:
        with get_postgres_saver() as checkpointer:
            compiled_graph = agent_graph.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}
            state = compiled_graph.get_state(config)

            if not state.values:
                return {"messages": [], "thread_id": thread_id}

            messages = []
            for msg in state.values.get("messages", []):
                if hasattr(msg, "content") and msg.content:
                    messages.append({
                        "role": "human" if msg.__class__.__name__ == "HumanMessage" else "assistant",
                        "content": msg.content,
                    })

            return {"messages": messages, "thread_id": thread_id}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )