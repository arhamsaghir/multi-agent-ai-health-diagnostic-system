"""About page — project information and architecture."""

import streamlit as st


def show_about_page():
    """Render the about page."""
    st.title("About This System")
    st.caption("Multi-Agent AI Health Diagnostic System — B.Tech Final Year Project")

    st.markdown("""
### Architecture

This system uses a **multi-agent AI architecture** where specialist agents collaborate
under an orchestrator to provide comprehensive health diagnostics.

```
User Input → Orchestrator Agent → Specialist Agents → GenAI Synthesis → Output
               (LangGraph)         (Vision/NLP/RAG/     (Gemini 1.5       (Report/
                                   Prediction)           Flash)            Chatbot)
```

### Specialist Agents

| Agent | Technology | Purpose |
|---|---|---|
| **Orchestrator** | LangGraph, GPT-4o-mini | Task planning, routing, memory management |
| **Vision** | ResNet-50, PyTorch | Medical image analysis (X-ray, MRI) |
| **NLP** | BioBERT, spaCy | Symptom extraction, NER, intent classification |
| **RAG** | LlamaIndex, FAISS, Nemotron 3 | Medical knowledge retrieval |
| **Prediction** | XGBoost, LSTM | Disease risk scoring |
| **Voice** | Whisper | Speech-to-text transcription |

### Multi-LLM Strategy

Different LLMs are used for different tasks to maximize quality while staying within free tiers:

- **GPT-4o-mini** (OpenAI): Orchestrator reasoning, patient chatbot
- **Gemini 1.5 Flash** (Google): Report synthesis, plain language explanations
- **Nemotron 3** (NVIDIA): RAG retrieval and knowledge synthesis
- **BioBERT** (HuggingFace): Domain-specific medical NLP (local, free)

### Disclaimer

⚠️ **This is a research project, not a medical device.** Always consult a qualified
healthcare professional for medical advice, diagnosis, and treatment.
    """)

    # Tech stack
    st.divider()
    st.subheader("Tech Stack")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Backend**\n- FastAPI\n- LangChain / LangGraph\n- PyTorch / TensorFlow\n- XGBoost")
    with col2:
        st.markdown("**Frontend**\n- Streamlit\n- Plotly (visualizations)\n\n**Infrastructure**\n- Docker\n- FAISS (vector DB)\n- SQLite")
