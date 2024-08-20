import streamlit as st
import streamlit.components.v1 as components
import base64
import sqlite3
import os
import re
import uuid
import json

from agents_content import agent_content_ideas, agent_content_creator

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)


# Function to convert image to base64
def img_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


# Function to initialize the database schema
def initialize_db():
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            nombre_negocio text,
            descripcion text,
            tono text,
            metas text,
            reporte text
        )"""
    )
    conn.commit()
    conn.close()


# Function to save user data
def save_user_data(
    nombre_negocio,
    descripcion,
    tono,
    metas,
    reporte,
):
    conn = sqlite3.connect("data/user_data.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO users (nombre_negocio, descripcion, tono, metas, reporte) VALUES (?, ?, ?, ?, ?)",
        (
            nombre_negocio,
            descripcion,
            tono,
            metas,
            reporte,
        ),
    )
    conn.commit()
    conn.close()


def main():
    st.set_page_config(
        page_title="Generador de Estrategia IA para tu Negocio - AutoFlujo",
        page_icon="images/favicon.ico",  # Make sure you have the favicon.ico in the same directory or provide the correct path
    )

    if "config" not in st.session_state:
        thread_id_number = str(uuid.uuid4())
        st.session_state.config = {"configurable": {"thread_id": thread_id_number}}

    # Initialize the database schema
    initialize_db()

    # Cache the API key in the session state
    if "groq_api_key" not in st.session_state:
        st.session_state.groq_api_key = ""

    # Sidebar content
    img_path = "images/image.jpg"
    img_base64 = img_to_base64(img_path)
    st.sidebar.markdown(
        f"""
        <style>
        .cover-glow {{
            width: 100%;  /* Adjust the width as needed */
            height: auto; /* Maintain the aspect ratio */
            padding: 3px;
            box-shadow: 1px 2px 23px 0px rgba(188,150,255,0.75);
            border-radius: 30px;
        }}
        </style>
        <img src="data:image/png;base64,{img_base64}" class="cover-glow">
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.title("Te ayudamos a implementar IA en tu negocio")
    st.sidebar.markdown(
        "En AutoFlujo te ayudamos a aumentar tus ventas, reducir costos operativos y llegar más rápido a tus metas con:<br><br>- 🤖 Chatbots<br>- ⚙️ Automatizaciones<br>- 🤝 Captación de Leads<br>- 📈 Reportes automatizados<br><br>Y más herramientas con Inteligencia Artificial al servicio de tus metas. <a href='https://autoflujo.com/agenda-tu-cita-flow-1/' target='_blank'>Contáctanos aquí.</a>",
        unsafe_allow_html=True,
    )

    # Main content
    # Title
    st.title("💡 Creador de Contenidos para Redes Sociales")
    st.subheader("Llena los datos de tu negocio y crea contenidos virales.")

    # Form to collect business information and API key
    with st.form("user_form"):
        nombre_negocio = st.text_input("Nombre de tu negocio")
        descripcion = st.text_area("Breve descripción de tu negocio.")
        tono = st.selectbox(
            "¿Qué tono prefieres para la comunicación de tu negocio?",
            ["Formal", "Informal", "Creativo", "Profesional"],
        )
        metas = st.text_area("Metas que deseas cumplir con tu negocio")

        # Add Groq API key input field
        st.session_state.groq_api_key = st.text_input(
            "Llave API de Groq",
            value=st.session_state.groq_api_key,
            placeholder="gsk_...",
        )

        create_ideas = st.form_submit_button("Generar Contenidos")

    st.markdown(
        "<div style='text-align: center; color: #a491ff;'>Creado por AutoFlujo ♾️. Todos los derechos reservados</div>",
        unsafe_allow_html=True,
    )

    if create_ideas:
        if not (nombre_negocio and descripcion and tono and metas):
            st.warning("Por favor, completa todos los campos obligatorios.")
        elif not st.session_state.groq_api_key:
            st.warning("Por favor, ingresa tu llave API de Groq.")
        else:
            with st.spinner("Procesando..."):
                # Generate 5 Ideas: Content Planner
                if "dict_ideas" not in st.session_state:
                    dict_ideas = agent_content_ideas(
                        nombre_negocio,
                        descripcion,
                        tono,
                        metas,
                        rejected_ideas="",
                        api_key=st.session_state.groq_api_key,
                    )
                    st.session_state.dict_ideas = dict_ideas
                else:
                    rejected = st.session_state.dict_ideas
                    new_dict_ideas = agent_content_ideas(
                        nombre_negocio,
                        descripcion,
                        tono,
                        metas,
                        rejected_ideas=rejected,
                        api_key=st.session_state.groq_api_key,
                    )
                    st.session_state.dict_ideas = new_dict_ideas

    # Display and select ideas if they exist in session_state
    if "dict_ideas" in st.session_state:
        st.title("Selecciona una Idea")

        # Create a list of options for the radio button
        options = [
            f"**Idea {idea['id']}:** {idea['idea']}"
            for idea in st.session_state.dict_ideas["content_ideas"]
        ]

        # Use radio button to select an idea
        selected_option = st.radio("Elige una idea:", options)

        # Find the selected idea
        selected_idea = next(
            (
                idea
                for idea in st.session_state.dict_ideas["content_ideas"]
                if f"Idea {idea['id']}" in selected_option
            ),
            None,
        )

        if selected_idea:
            st.session_state.selected_idea = selected_idea

        # Proceed to the next step or generate new ideas
        col1, col2 = st.columns(2)

        with col1:
            continue_button = st.button("Continuar con la idea seleccionada")

        with col2:
            generate_new_ideas_button = st.button("Generar 5 nuevas ideas")

        # Logic when the "Continuar con la idea seleccionada" button is clicked
        if continue_button:
            # Custom logic when the user selects "Continuar con la idea seleccionada"
            save_user_data(
                nombre_negocio,
                descripcion,
                tono,
                metas,
                selected_idea["idea"],
            )

            st.write("Creando contenido con la idea seleccionada...")

            # Display the result across the full width of the page
            agent_content_response = agent_content_creator(
                nombre_negocio,
                descripcion,
                tono,
                metas,
                selected_idea["idea"],
                api_key=st.session_state.groq_api_key,
            )
            st.markdown(agent_content_response.content, unsafe_allow_html=True)

        # Logic for generating 5 new ideas
        if generate_new_ideas_button:
            with st.spinner("Generando nuevas ideas..."):
                rejected = st.session_state.dict_ideas
                new_dict_ideas = agent_content_ideas(
                    nombre_negocio,
                    descripcion,
                    tono,
                    metas,
                    rejected_ideas=rejected,
                    api_key=st.session_state.groq_api_key,
                )
                st.session_state.dict_ideas = new_dict_ideas
                st.rerun()  # Rerun to update the UI with new ideas


if __name__ == "__main__":
    main()
