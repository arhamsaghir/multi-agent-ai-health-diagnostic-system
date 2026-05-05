"""Vision page — X-ray/MRI image analysis with AI-powered detection."""

import sys
from pathlib import Path as StdPath
sys.path.insert(0, str(StdPath(__file__).resolve().parents[1]))

import streamlit as st
import requests
import json
import time
from datetime import datetime
from PIL import Image
import numpy as np

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from config import settings

API_BASE = "http://localhost:8000"

# Disease classes matching the vision model training
DISEASE_CLASSES = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass",
    "Nodule", "Pneumonia", "Pneumothorax", "Consolidation", "Edema",
    "Emphysema", "Fibrosis", "Pleural Thickening", "Hernia", "Normal"
]

# Severity mapping for findings
FINDING_SEVERITY = {
    "Pneumonia": ("High", "⚠️", "#fd7e14", "Seek medical evaluation"),
    "Pneumothorax": ("Critical", "🚨", "#dc3545", "Emergency — seek immediate care"),
    "Effusion": ("High", "⚠️", "#fd7e14", "Requires medical attention"),
    "Mass": ("High", "⚠️", "#fd7e14", "Further investigation needed"),
    "Nodule": ("Moderate", "🔍", "#ffc107", "Monitor and follow up"),
    "Cardiomegaly": ("Moderate", "🔍", "#ffc107", "Cardiac evaluation recommended"),
    "Infiltration": ("Moderate", "🔍", "#ffc107", "Clinical correlation needed"),
    "Consolidation": ("High", "⚠️", "#fd7e14", "May indicate infection"),
    "Edema": ("High", "⚠️", "#fd7e14", "Seek medical evaluation"),
    "Emphysema": ("Moderate", "🔍", "#ffc107", "Pulmonary evaluation needed"),
    "Fibrosis": ("Moderate", "🔍", "#ffc107", "Specialist referral recommended"),
    "Atelectasis": ("Moderate", "🔍", "#ffc107", "May resolve with treatment"),
    "Pleural Thickening": ("Low", "ℹ️", "#28a745", "Usually benign — monitor"),
    "Hernia": ("Moderate", "🔍", "#ffc107", "Surgical consultation may be needed"),
    "Normal": ("Low", "✅", "#28a745", "No significant abnormalities"),
}

# Demo results for offline presentation
DEMO_RESULTS = {
    "Pneumonia Case": {
        "predictions": [
            {"disease": "Pneumonia", "confidence": 0.89},
            {"disease": "Consolidation", "confidence": 0.62},
            {"disease": "Infiltration", "confidence": 0.45},
        ],
        "primary_finding": "Pneumonia",
        "severity": "High",
        "recommendation": "Chest X-ray shows findings consistent with pneumonia. Clinical correlation with symptoms (fever, cough, difficulty breathing) is recommended. Seek medical evaluation for appropriate treatment.",
    },
    "Normal Chest X-ray": {
        "predictions": [
            {"disease": "Normal", "confidence": 0.92},
            {"disease": "Atelectasis", "confidence": 0.05},
            {"disease": "Effusion", "confidence": 0.02},
        ],
        "primary_finding": "Normal",
        "severity": "Low",
        "recommendation": "No significant abnormalities detected. All findings within normal limits.",
    },
    "Cardiomegaly Case": {
        "predictions": [
            {"disease": "Cardiomegaly", "confidence": 0.78},
            {"disease": "Effusion", "confidence": 0.34},
            {"disease": "Edema", "confidence": 0.22},
        ],
        "primary_finding": "Cardiomegaly",
        "severity": "Moderate",
        "recommendation": "Enlarged cardiac silhouette detected. Cardiac evaluation recommended including echocardiography and clinical assessment for heart failure symptoms.",
    },
    "Pneumothorax Case": {
        "predictions": [
            {"disease": "Pneumothorax", "confidence": 0.85},
            {"disease": "Emphysema", "confidence": 0.28},
            {"disease": "Atelectasis", "confidence": 0.15},
        ],
        "primary_finding": "Pneumothorax",
        "severity": "Critical",
        "recommendation": "Pneumothorax (collapsed lung) detected — this is a medical emergency. Seek immediate emergency care. Do not delay treatment.",
    },
}


def call_vision_api(image_file) -> dict:
    """Send image to API for analysis."""
    try:
        response = requests.post(
            f"{API_BASE}/api/diagnosis/analyze-with-image",
            files={"file": (image_file.name, image_file.getvalue(), "image/png")},
            timeout=60,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}", "detail": response.text}
    except requests.ConnectionError:
        return {"error": "API server not running", "detail": "Start the API server with: uvicorn src.api.main:app"}
    except requests.Timeout:
        return {"error": "Request timed out", "detail": "The analysis took too long. Try again or use demo mode."}
    except Exception as e:
        return {"error": str(e), "detail": ""}


def run_local_vision(image_bytes) -> dict:
    """Run vision analysis locally using the VisionAgent directly."""
    try:
        import tempfile
        import os
        from src.agents.vision.agent import VisionAgent
        from PIL import Image
        
        # Save image to temp file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(image_bytes)
            temp_path = f.name
        
        try:
            vision_agent = VisionAgent()
            import asyncio
            result = asyncio.run(vision_agent.run({"image_path": temp_path}))
            return result
        finally:
            os.unlink(temp_path)
            
    except Exception as e:
        return {"error": f"Local analysis failed: {e}", "detail": ""}


def display_finding_card(disease: str, confidence: float):
    """Display a finding card with severity coloring."""
    severity_info = FINDING_SEVERITY.get(disease, ("Unknown", "❓", "#6c757d", "Consult physician"))
    sev_label, sev_icon, sev_color, sev_action = severity_info
    
    bar_color = sev_color
    st.markdown(
        f"""
        <div style="padding: 1rem; background: {sev_color}11; border-left: 4px solid {sev_color}; border-radius: 8px; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 1.1rem;">{sev_icon} {disease}</strong>
                </div>
                <div style="font-size: 1.2rem; font-weight: bold; color: {sev_color};">
                    {confidence*100:.0f}%
                </div>
            </div>
            <div style="color: {sev_color}; font-size: 0.85rem; margin-top: 4px;">
                Severity: {sev_label} | {sev_action}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_vision_page():
    st.title("🔬 Medical Image Analysis")
    st.caption("Upload X-ray, MRI, or CT images for AI-powered anomaly detection")
    
    # Sidebar: mode toggle
    with st.sidebar:
        st.subheader("Analysis Mode")
        use_demo = st.toggle("Use Demo Mode", value=False, help="Show pre-computed results without running AI")
        
        st.divider()
        st.subheader("Supported Conditions")
        st.caption("15 chest X-ray conditions: Pneumonia, Pneumothorax, Cardiomegaly, Effusion, Mass, Nodule, and more")
        
        st.divider()
        st.info("📸 Upload a chest X-ray image (PNG, JPG, DICOM)")
    
    # Upload section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Medical Image",
            type=["png", "jpg", "jpeg", "tiff"],
            help="Upload a chest X-ray image for AI analysis. Supported formats: PNG, JPG, JPEG, TIFF.",
        )
    
    with col2:
        st.subheader("Demo Scenarios")
        demo_scenario = st.selectbox(
            "Choose a demo case",
            list(DEMO_RESULTS.keys()),
            index=0,
            help="Select a pre-built case for demonstration",
        )
        if st.button("Load Demo Case", type="primary", use_container_width=True):
            st.session_state["demo_result"] = DEMO_RESULTS[demo_scenario]
            st.session_state["demo_scenario_name"] = demo_scenario
            st.rerun()
    
    # Display uploaded image
    if uploaded_file:
        st.subheader("Uploaded Image")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption=f"Image: {uploaded_file.name} ({image.size[0]}x{image.size[1]})")
    
    # Analyze button
    if uploaded_file and not use_demo:
        if st.button("Analyze Image", type="primary", use_container_width=True):
            with st.spinner("Running AI vision analysis..."):
                # Try API first, fall back to local
                uploaded_file.seek(0)
                result = call_vision_api(uploaded_file)
                
                if result.get("error") and "API" in result.get("error", ""):
                    st.warning(f"API unavailable ({result['error']}). Running local analysis...")
                    uploaded_file.seek(0)
                    result = run_local_vision(uploaded_file.getvalue())
                
                if result.get("error"):
                    st.error(f"Analysis failed: {result['error']}")
                    if result.get("detail"):
                        st.caption(result["detail"])
                else:
                    st.session_state["analysis_result"] = result
                    st.session_state["analysis_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.success("Analysis complete!")
                    st.rerun()
    
    # Display demo result
    if st.session_state.get("demo_result"):
        st.subheader(f"Demo Results: {st.session_state.get('demo_scenario_name', '')}")
        display_results(st.session_state["demo_result"])
    
    # Display analysis result
    if st.session_state.get("analysis_result"):
        st.subheader(f"Analysis Results ({st.session_state.get('analysis_timestamp', '')})")
        display_results(st.session_state["analysis_result"])


def display_results(result: dict):
    """Display analysis results with cards and charts."""
    # Primary finding
    primary = result.get("primary_finding", result.get("prediction", "Unknown"))
    if isinstance(primary, dict):
        primary = primary.get("disease", primary.get("condition", "Unknown"))
    
    predictions = result.get("predictions", result.get("diagnoses", []))
    if isinstance(predictions, dict):
        predictions = [predictions]
    
    severity_info = FINDING_SEVERITY.get(primary, ("Unknown", "❓", "#6c757d", "Consult physician"))
    sev_label, sev_icon, sev_color, sev_action = severity_info
    
    # Severity card
    st.markdown(
        f"""
        <div style="padding: 1.5rem; background: {sev_color}15; border-left: 5px solid {sev_color}; border-radius: 8px; margin-bottom: 1rem;">
            <div style="font-size: 1.3rem; font-weight: bold; color: {sev_color};">
                {sev_icon} {primary} — Severity: {sev_label.upper()}
            </div>
            <div style="color: {sev_color}; font-size: 0.95rem; margin-top: 6px;">
                {sev_action}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Findings cards
    if predictions:
        st.subheader("All Findings")
        for pred in predictions:
            disease = pred.get("disease", pred.get("condition", "Unknown"))
            conf = pred.get("confidence", 0)
            if isinstance(conf, str):
                try:
                    conf = float(conf)
                except:
                    conf = 0
            display_finding_card(disease, conf)
    
    # Confidence chart
    if predictions:
        st.subheader("Confidence Distribution")
        
        # Sort by confidence
        sorted_preds = sorted(predictions, key=lambda x: x.get("confidence", 0), reverse=True)
        
        # Bar chart
        import plotly.graph_objects as go
        
        diseases = [p.get("disease", p.get("condition", "Unknown")) for p in sorted_preds]
        confidences = [p.get("confidence", 0) for p in sorted_preds]
        
        colors = []
        for d in diseases:
            sev_info = FINDING_SEVERITY.get(d, ("Unknown", "❓", "#6c757d", ""))
            colors.append(sev_info[2])
        
        fig = go.Figure(
            data=[
                go.Bar(
                    x=diseases,
                    y=[c * 100 for c in confidences],
                    marker_color=colors,
                    text=[f"{c*100:.0f}%" for c in confidences],
                    textposition="auto",
                )
            ]
        )
        fig.update_layout(
            xaxis_title="Condition",
            yaxis_title="Confidence (%)",
            height=400,
            margin=dict(l=40, r=20, t=20, b=40),
            xaxis_tickangle=-30,
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendation
    recommendation = result.get("recommendation", result.get("explanation", ""))
    if recommendation:
        st.subheader("AI Recommendation")
        if sev_label in ["Critical", "High"]:
            st.error(recommendation)
        elif sev_label == "Moderate":
            st.warning(recommendation)
        else:
            st.success(recommendation)
    
    # Save to history
    if st.button("Save to History", key="save_vision_to_history"):
        history = st.session_state.get("diagnosis_history", [])
        history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "vision",
            "primary_finding": primary,
            "severity": sev_label,
            "confidence": confidences[0] if confidences else 0,
            "result": result,
        })
        st.session_state["diagnosis_history"] = history
        st.success("Saved to history!")
    
    # Disclaimer
    st.divider()
    st.caption("⚠️ This AI analysis is for research purposes only and does not replace professional medical diagnosis. Always consult a qualified radiologist or healthcare provider for medical imaging interpretation.")
