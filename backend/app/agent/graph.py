from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph.message import add_messages
from app.core.config import settings
from app.agent.tools import TOOLS


# ── Estado del grafo ──────────────────────────────────────────────────
class AgentState(TypedDict):
    """
    El estado es lo que se pasa entre nodos del grafo.
    'messages' acumula toda la conversación.
    'user_id' identifica al usuario para que las tools
    puedan consultar su portfolio específico.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    user_id: str


# ── LLM con tools ─────────────────────────────────────────────────────
def get_llm():
    """Crea el LLM de Groq con las tools vinculadas."""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.GROQ_API_KEY,
        temperature=0,
        # temperature=0 para respuestas más deterministas y precisas
        # en análisis financiero
    )
    return llm.bind_tools(TOOLS)


# ── Nodos del grafo ───────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres FinSight, un analista financiero IA experto.

IMPORTANTE: El user_id del usuario actual es: {user_id}
Siempre usa este user_id cuando llames a las herramientas.

Tienes acceso a las siguientes herramientas:
- portfolio_tool: consulta el portfolio del usuario. Llámala con user_id='{user_id}'
- market_data_tool: obtiene precios y datos de mercado en tiempo real
- quant_tool: calcula métricas cuantitativas. Llámala con user_id='{user_id}'

INSTRUCCIONES:
- Cuando el usuario pregunte sobre su portfolio, posiciones o inversiones,
  USA SIEMPRE portfolio_tool antes de responder.
- Cuando pregunte por precios o datos de mercado, usa market_data_tool.
- Cuando pregunte por riesgo, Sharpe o métricas, usa quant_tool.
- Responde siempre en el idioma del usuario.
- Sé preciso con los números financieros."""


def agent_node(state: AgentState) -> AgentState:
    """Nodo principal del agente."""
    llm = get_llm()

    # Inyectamos el user_id en el system prompt
    system_content = SYSTEM_PROMPT.format(user_id=state["user_id"])

    messages_with_system = [
        SystemMessage(content=system_content)
    ] + state["messages"]

    response = llm.invoke(messages_with_system)
    # Debug temporal
    print(f"DEBUG user_id: {state['user_id']}")
    print(f"DEBUG tool_calls: {getattr(response, 'tool_calls', 'ninguna')}")
    print(f"DEBUG response content: {response.content[:100]}")
    
    return {"messages": [response], "user_id": state["user_id"]}


def should_continue(state: AgentState) -> str:
    """
    Función de routing: decide si continuar con herramientas o terminar.
    Si el último mensaje del LLM tiene tool_calls, va al nodo de tools.
    Si no, la conversación termina y se devuelve la respuesta al usuario.
    """
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ── Construcción del grafo ─────────────────────────────────────────────
def build_agent_graph():
    """
    Construye y compila el grafo del agente.
    El grafo se compila una vez y se reutiliza para todas las conversaciones.
    """
    graph = StateGraph(AgentState)

    # Añadir nodos
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    # Punto de entrada
    graph.set_entry_point("agent")

    # Edges condicionales: después del agente decide si usar tools o terminar
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        }
    )

    # Después de ejecutar tools, vuelve al agente para procesar resultados
    graph.add_edge("tools", "agent")

    return graph


# Instancia del grafo sin compilar (se compila con el checkpointer en el router)
agent_graph = build_agent_graph()