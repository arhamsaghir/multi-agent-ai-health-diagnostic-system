"""Ingest medical knowledge documents into the FAISS vector store.

Embeds clinical guidelines using sentence-transformers and stores them
in FAISS for fast semantic retrieval by the RAG Agent.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loguru import logger
from config import settings
from src.data.embedding import EmbeddingModel
from src.agents.rag.agent import RAGAgent


MEDICAL_KNOWLEDGE = [
    {
        "text": (
            "Upper respiratory infections (URI) are among the most common illnesses worldwide. "
            "Symptoms include cough, sore throat, runny nose, nasal congestion, and sometimes fever. "
            "Most URIs are viral and self-limiting, resolving within 7-10 days. "
            "Common causative agents include rhinovirus, coronavirus, adenovirus, and respiratory syncytial virus. "
            "Treatment is primarily supportive: rest, hydration, and symptomatic relief with analgesics."
        ),
        "source": "CDC Guidelines — Upper Respiratory Infections",
        "metadata": {"category": "respiratory", "type": "guideline"},
    },
    {
        "text": (
            "Tension-type headache is the most common primary headache disorder. "
            "It presents as bilateral, pressing, or tightening pain of mild to moderate intensity. "
            "It is not aggravated by routine physical activity and is not associated with nausea. "
            "Migraine, in contrast, is typically unilateral, pulsating, moderate to severe, "
            "and associated with nausea, photophobia, and phonophobia."
        ),
        "source": "International Classification of Headache Disorders (ICHD-3)",
        "metadata": {"category": "neurological", "type": "classification"},
    },
    {
        "text": (
            "Community-acquired pneumonia (CAP) is an acute infection of the pulmonary parenchyma. "
            "Common symptoms include cough (often productive), fever, chills, dyspnea, and pleuritic chest pain. "
            "Diagnosis is confirmed by chest radiograph showing infiltrates. "
            "Streptococcus pneumoniae is the most common bacterial cause. "
            "Treatment depends on severity and may include macrolides, doxycycline, or respiratory fluoroquinolones."
        ),
        "source": "IDSA/ATS Guidelines — Community-Acquired Pneumonia",
        "metadata": {"category": "respiratory", "type": "guideline"},
    },
    {
        "text": (
            "Acute gastroenteritis presents with diarrhea, nausea, vomiting, abdominal pain, and sometimes fever. "
            "Viral causes (norovirus, rotavirus) are most common. Bacterial causes include Salmonella, "
            "Campylobacter, and E. coli. Treatment focuses on oral rehydration therapy. "
            "Antibiotics are reserved for specific bacterial pathogens and severe cases."
        ),
        "source": "WHO Guidelines — Acute Gastroenteritis",
        "metadata": {"category": "gastrointestinal", "type": "guideline"},
    },
    {
        "text": (
            "Type 2 diabetes mellitus is characterized by insulin resistance and relative insulin deficiency. "
            "Risk factors include obesity, family history, sedentary lifestyle, and age >45. "
            "Symptoms may include polyuria, polydipsia, fatigue, blurred vision, and slow wound healing. "
            "Diagnosis is by fasting glucose >=126 mg/dL, HbA1c >=6.5%, or random glucose >=200 mg/dL with symptoms. "
            "Management includes lifestyle modification, metformin as first-line, and additional agents as needed."
        ),
        "source": "American Diabetes Association — Standards of Care",
        "metadata": {"category": "endocrine", "type": "guideline"},
    },
    {
        "text": (
            "Acute coronary syndrome (ACS) encompasses unstable angina, NSTEMI, and STEMI. "
            "Presentation includes chest pain (pressure, squeezing, heaviness), radiation to arm or jaw, "
            "diaphoresis, nausea, and dyspnea. Risk factors: hypertension, diabetes, smoking, dyslipidemia, "
            "family history, obesity. Immediate evaluation with ECG and cardiac biomarkers (troponin) is essential. "
            "Time to reperfusion is critical in STEMI."
        ),
        "source": "ACC/AHA Guidelines — Acute Coronary Syndrome",
        "metadata": {"category": "cardiovascular", "type": "guideline"},
    },
    {
        "text": (
            "Urinary tract infections (UTI) are common, especially in women. "
            "Symptoms include dysuria, frequency, urgency, suprapubic pain, and sometimes hematuria. "
            "Upper UTI (pyelonephritis) presents with fever, flank pain, and nausea. "
            "Most common pathogen is Escherichia coli. "
            "Uncomplicated cystitis is treated with nitrofurantoin, trimethoprim-sulfamethoxazole, or fosfomycin."
        ),
        "source": "IDSA Guidelines — Uncomplicated Urinary Tract Infections",
        "metadata": {"category": "urological", "type": "guideline"},
    },
    {
        "text": (
            "Major depressive disorder (MDD) is characterized by depressed mood or anhedonia for >=2 weeks, "
            "plus symptoms including sleep disturbance, appetite changes, fatigue, feelings of worthlessness, "
            "difficulty concentrating, and suicidal ideation. "
            "Screening tools include PHQ-9. First-line treatment includes SSRIs (sertraline, escitalopram) "
            "and cognitive behavioral therapy. Severe cases may require hospitalization."
        ),
        "source": "APA Guidelines — Major Depressive Disorder",
        "metadata": {"category": "psychiatric", "type": "guideline"},
    },
    {
        "text": (
            "Asthma is a chronic inflammatory disorder of the airways characterized by reversible airflow obstruction. "
            "Symptoms include wheezing, shortness of breath, chest tightness, and cough (often worse at night). "
            "Triggers include allergens, exercise, cold air, and respiratory infections. "
            "Management includes inhaled corticosteroids (controller) and short-acting beta-agonists (rescue). "
            "Peak flow monitoring helps assess control."
        ),
        "source": "GINA Guidelines — Asthma Management",
        "metadata": {"category": "respiratory", "type": "guideline"},
    },
    {
        "text": (
            "Hypertension is defined as systolic BP >=130 mmHg or diastolic BP >=80 mmHg. "
            "Often asymptomatic, it is called the 'silent killer.' "
            "Complications include stroke, myocardial infarction, heart failure, kidney disease, and retinopathy. "
            "Risk factors: age, family history, obesity, high sodium intake, sedentary lifestyle, alcohol. "
            "Treatment: lifestyle modification (DASH diet, exercise, weight loss) plus antihypertensives "
            "(ACE inhibitors, ARBs, calcium channel blockers, thiazide diuretics)."
        ),
        "source": "ACC/AHA Guidelines — Hypertension",
        "metadata": {"category": "cardiovascular", "type": "guideline"},
    },
]


def load_curated_corpus() -> list[dict]:
    """Load the provenance-bearing Phase 2 corpus when available."""
    corpus_path = Path(__file__).resolve().parents[1] / "data/knowledge/guidelines/corpus.json"
    if not corpus_path.exists():
        return MEDICAL_KNOWLEDGE

    records = json.loads(corpus_path.read_text())
    documents = []
    for record in records:
        if not record.get("content") or not record.get("source") or not record.get("source_url"):
            raise ValueError(f"Corpus record missing provenance: {record.get('id', '<unknown>')}")
        documents.append({
            "text": record["content"],
            "source": record["source"],
            "metadata": {
                "source": record["source"],
                "source_url": record["source_url"],
                "category": record.get("category", "general"),
                "last_reviewed": record.get("last_reviewed", ""),
                "provenance": record.get("provenance", ""),
            },
        })
    return documents


def ingest_medical_knowledge():
    """Embed and store the curated medical knowledge corpus in FAISS."""
    logger.info("Starting medical knowledge ingestion...")

    documents = load_curated_corpus()
    rag = RAGAgent()
    # A single replaceable corpus avoids duplicate accumulation on reruns.
    rag.faiss_index = None
    rag.documents = []
    rag.metadata = []
    batch_size = 64
    for start in range(0, len(documents), batch_size):
        rag.ingest_documents(documents[start:start + batch_size])

    logger.info(f"Ingested {len(documents)} medical knowledge documents")
    logger.info(f"Vector store location: {settings.vector_store_dir}")

    # Verify by doing a test retrieval
    import asyncio
    async def verify():
        result = await rag.run({"query": "headache and nausea for 3 days"})
        logger.info(f"Test retrieval: {result['num_sources']} results for 'headache and nausea'")

    asyncio.run(verify())


if __name__ == "__main__":
    ingest_medical_knowledge()
