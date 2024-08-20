import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from typing import List


# Environment setup
load_dotenv(override=True)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "Asistente de Contenidos"

llama3_1 = "llama-3.1-70b-versatile"


class ContentIdea(BaseModel):
    id: int = Field(description="Unique identifier for the content idea")
    idea: str = Field(description="Content idea for social media")


class ContentIdeas(BaseModel):
    content_ideas: List[ContentIdea] = Field(description="List of content ideas")


def agent_content_ideas(
    name: str,
    description: str,
    tone: str,
    goals: str,
    rejected_ideas: str,
    api_key: str,
) -> str:
    parser = JsonOutputParser(pydantic_object=ContentIdeas)
    format_instructions = parser.get_format_instructions()
    prompt = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        
        Crea 5 ideas de contenidos para promocionar un negocio con la siguiente info:
        NOMBRE DE NEGOCIO: {name}.
        
        DESCRIPCIÓN: {description}.
        
        METAS: {goals}.
        
        TONO DE COMUNICACIÓN: {tone}.
        
        IDEAS RECHAZADAS (optativamente): {rejected_ideas}.
        
        Destaca los aspectos únicos de su DESCRIPCIÓN para lograr las METAS requerids con un enfoque según su TONO DE COMUNICACIÓN. 
        Usa un lenguaje que se ajuste a su TONO DE COMUNICACIÓN para crear publicaciones atractivas para el negocio con la DESCRIPCIÓN, impulsando sus METAS. 
        Si recibes IDEAS RECHAZADAS, procura que tus 5 ideas no estén relacionadas a las IDEAS RECHAZADAS y en su lugar ofrece ideas diferentes pero que sigan cumpliendo las METAS del negocio con la DESCRIPCIÓN y TONO DE COMUNICACIÓN establecido.
        IMPORTANTE: Tus ideas deben ser eso, ideas, no desarrolles el contenido aún, eso lo haremos en otro paso.
        IMPORTANTE: Usa el siguiente formato JSON: {format_instructions}<|eot_id|>
        <|start_header_id|>user<|end_header_id|>
         
        Adelante con tus 5 ideas:<|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
    )

    llm = ChatGroq(model=llama3_1, api_key=api_key, temperature=0.7)

    chain = prompt | llm | parser

    try:
        # Get the extracted data from the chain
        json_ideas = chain.invoke(
            {
                "name": name,
                "description": description,
                "goals": goals,
                "tone": tone,
                "rejected_ideas": rejected_ideas,
                "format_instructions": format_instructions,
            }
        )

        # Debug: Print the extracted data before validation
        # print(f"Json Ideas: {json_ideas}")

        # Create a ContentIdea instance to invoke the validation
        content_ideas = ContentIdeas(**json_ideas)

        # Debug: Print the person instance to check the validation result
        # print(f"Validated IDEAS: {content.dict()}")

        return content_ideas.dict()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Develop single content
def agent_content_creator(
    name_bizz, description_bizz, tone_bizz, goals_bizz, content_choosen, api_key
):
    prompt_extract = PromptTemplate(
        template="""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
        
        Asume tu papel como experto en Marketing Digital y ventas.
        
        Desarrolla el contenido para la siguiente idea de promoción en redes sociales:
        
        Concepto del contenido: {content_choosen}.
        
        Toma en cuenta esta información del negocio para el cual le harás su contenido.

        Nombre del negocio: {name_bizz}

        Descripción del negocio: {description_bizz}

        Tono de comunicación: {tone_bizz}

        Metas del negocio: {goals_bizz}


        Requerimientos:
        
        1. CONCEPTO: Explica al usuario a detalle el concepto del contenido en términos generales. Esto no se publicará pero servirá al usuario para entender qué es lo que tiene que comunicar en su publicación.
        
        2. REDES SOCIALES EN QUE SE PUBLICARÁ: FB, IG, TikTok, YouTube o LinkedIn, dependiendo la información que reicbas.

        3. PROMPT DE IMAGEN: Proporciona un prompt muy descriptivo para generar una imagen que acompañe el contenido. Debe capturar la esencia del concepto y ser visualmente muy atractiva en las plataformas mencionadas. No menciones uses logotipos ni conceptos que sean difíciles de entender para una AI creadora de imágenes.
        
        4. COPY OUT: Redacta un copy out que irá en el espacio de texto de la plataforma. Debe profundizar en el mensaje, alineado con el tono de comunicación del negocio, y que lleve a los usuarios a interactuar o realizar la acción deseada.
        
        5. COPY IN: Desarrolla el copy principal que irá en la imagen del contenido. Debe llamar la atención rápidamente cuando la visualice el usuario, ideal para captar la atención de los usuarios en las plataformas seleccionadas.

        6. CONCEPTO PARA VIDEO: Si seleccionas TikTok en las redes sociales a publicar, describe una idea atractiva de video que se pueda producir para complementar el contenido. Esta idea debe ser fácil de desarrollar y no debe necesitar una producción costosa.
        IMPORTANTE: Responde solamente con lo que se te pide, no agregues saludos, introducción ni conclusiones.<|eot_id|>
        <|start_header_id|>user<|end_header_id|>
         
        Adelante con tu contenido:<|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
        """
    )
    llm = ChatGroq(model=llama3_1, api_key=api_key, temperature=0.7)

    chain = prompt_extract | llm
    try:
        agent_response = chain.invoke(
            {
                "name_bizz": name_bizz,
                "description_bizz": description_bizz,
                "tone_bizz": tone_bizz,
                "goals_bizz": goals_bizz,
                "content_choosen": content_choosen,
            }
        )
        return agent_response
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
