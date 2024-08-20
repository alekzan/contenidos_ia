from typing_extensions import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage

from agents_content import agent_content_ideas, agent_content_creator
import json


# State
class State(TypedDict):
    query: str  # User's query
    nombre_negocio: str  # Business name
    descripcion: str  # The description of the business
    tono: str  # The comunciation tone selected for the business for their ads
    metas: str  # Business goals
    contenidos_json: (
        str  # Content topics for social media of the business in JSON format
    )
    contenidos_rechazados: str  # Content topics rejected by the user
    contenido_elegido: str  # Content topic selected by the user
    contenido_final: str  # Content to upload in Social Media


# Edges
def router_query(state: State):
    print("ENRUTANDO LA CONSULTA DEL USUARIO")
    user_query = state["query"]
    return user_query  # create_ideas, create_content


# Nodes
def generate_ideas(state: State):
    print("CREANDO 5 IDEAS DE CONTENIDO")

    # Safely retrieve or initialize contenidos_json and contenidos_rechazados
    current_content_json = state.get("contenidos_json", "")
    current_rejected_ideas = state.get("contenidos_rechazados", "")

    # Move the existing content to 'contenidos_rechazados' if there is any
    if current_content_json:
        current_rejected_ideas += "\n" + current_content_json

    # Generate new content ideas
    name_bizz = state["nombre_negocio"]
    description_bizz = state["descripcion"]
    tone_bizz = state["tono"]
    goals_bizz = state["metas"]

    content_ideas_dict = agent_content_ideas(
        name_bizz, description_bizz, tone_bizz, goals_bizz, current_rejected_ideas
    )

    # Convert the content ideas dictionary to a JSON string
    content_ideas_json = json.dumps(content_ideas_dict, ensure_ascii=False)

    # Return the updated state with new content ideas and updated contenidos_rechazados
    return {
        "contenidos_json": content_ideas_json,
        "contenidos_rechazados": current_rejected_ideas,
    }


def generate_content(state: State):
    print("DESARROLLANDO CONTENIDO")
    name_bizz = state["nombre_negocio"]
    description_bizz = state["descripcion"]
    tone_bizz = state["tono"]
    goals_bizz = state["metas"]
    content_choosen = state["contenido_elegido"]

    final_content = agent_content_creator(
        name_bizz, description_bizz, tone_bizz, goals_bizz, content_choosen
    )

    return {"contenido_final": final_content}


graph_builder = StateGraph(State)

graph_builder.add_node("generate_ideas", generate_ideas)
graph_builder.add_node("generate_content", generate_content)

graph_builder.set_conditional_entry_point(
    router_query,
    {
        "create_ideas": "generate_ideas",
        "create_content": "generate_content",
    },
)

graph_builder.add_edge("generate_ideas", END)
graph_builder.add_edge("generate_content", END)
