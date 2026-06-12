# Richard Feynman Digital Twin

This project is a conversational digital twin of Richard Feynman. It uses a Retrieval-Augmented Generation (RAG) architecture to emulate his teaching style, voice, and reasoning patterns. 

The system relies on a local vector database built from his lectures, books, and personal letters, allowing the agent to cite his actual thoughts when answering questions.

## Core Capabilities

* **Conversational Interface:** A chat-based interface that supports text and audio input.
* **Dynamic Diagrams:** The agent can write and execute Python code to generate and render Feynman diagrams in real-time within the chat.
* **Voice Generation:** Integrates with ElevenLabs to output responses in Feynman's voice if the user speaks to it.
* **Adjustable Complexity:** A depth selector that allows the user to scale explanations from layman terms up to graduate-level physics.
* **The Feynman Technique Mode:** A Socratic mode where the agent stops explaining and instead probes the user's understanding of a concept, forcing them to explain it from first principles.
* **Anecdote Mode:** Prompts the agent to recall and share personal stories or observations relevant to the current conversation.

## Architecture

* **Framework:** Streamlit for the frontend, LangGraph for agent state routing and tool execution.
* **LLM & Embeddings:** Google Gemini models handle the reasoning and HuggingFace sentence transformers handle the embeddings.
* **Knowledge Base:** ChromaDB is used as the local vector store for the RAG pipeline.
* **Memory:** SQLite is used to persist long-term conversation history and user models.

## Setup Instructions

1. **Install Dependencies**
   Install the required packages from the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the root directory with the following keys:
   ```text
   GOOGLE_API_KEY="your-google-gemini-key"
   ELEVENLABS_API_KEY="your-elevenlabs-key"
   ELEVENLABS_VOICE_ID="your-voice-clone-id"
   ```

3. **Run the Application**
   Launch the Streamlit interface:
   ```bash
   streamlit run app.py
   ```

## Note on Voice Generation
If you plan to deploy this application to a cloud provider, be aware that the ElevenLabs Free Tier restricts API calls originating from data center IP addresses. You will either need to run the application locally or use a paid ElevenLabs tier for cloud deployments.
