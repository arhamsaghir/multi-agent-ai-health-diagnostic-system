"""History page — view past diagnosis sessions with search, filter, and export."""

import streamlit as st
import json
import csv
import io
from datetime import datetime


def load_history_from_db():
    """Load diagnosis history from SQLite database."""
    try:
        from src.data.database.repository import DiagnosisRepository
        repo = DiagnosisRepository()
        sessions = repo.list_sessions(limit=100)
        history = []
        for s in sessions:
            entry = {
                "timestamp": s.get("created_at", "Unknown"),
                "type": "vision" if s.get("image_path") else "text",
                "primary_finding": s.get("user_input", "Unknown")[:50],
                "severity": "unknown",
                "confidence": 0.0,
                "symptom_input": s.get("user_input", ""),
                "conditions": s.get("symptoms", []),
                "recommendations": [],
                "session_id": s.get("id", ""),
            }
            # Try to get diagnosis details
            diagnoses = s.get("diagnoses", [])
            if diagnoses:
                top_diag = diagnoses[0]
                entry["primary_finding"] = top_diag.get("condition_name", entry["primary_finding"])
                entry["confidence"] = top_diag.get("confidence", 0.0)
                entry["severity"] = top_diag.get("severity", "unknown")
                entry["conditions"] = diagnoses
            history.append(entry)
        return history
    except Exception:
        return []


def save_history_to_session(entry: dict):
    """Save a single history entry to session state (immediate display)."""
    if "diagnosis_history" not in st.session_state:
        st.session_state["diagnosis_history"] = []
    # Avoid duplicates by session_id
    if entry.get("session_id"):
        existing_ids = [h.get("session_id") for h in st.session_state["diagnosis_history"]]
        if entry["session_id"] in existing_ids:
            return
    st.session_state["diagnosis_history"].insert(0, entry)


def show_history_page():
    st.title("📋 Diagnosis History")
    st.caption("Review your past diagnostic assessments and image analyses")
    
    # Load history from database if session state is empty
    if "diagnosis_history" not in st.session_state or not st.session_state["diagnosis_history"]:
        db_history = load_history_from_db()
        if db_history:
            st.session_state["diagnosis_history"] = db_history
        else:
            st.session_state["diagnosis_history"] = []
    
    history = st.session_state["diagnosis_history"]
    
    # Sidebar: filters
    with st.sidebar:
        st.subheader("Filters")
        
        # Type filter
        all_types = list(set(h.get("type", "text") for h in history)) if history else []
        type_filter = st.multiselect(
            "Type",
            options=["text", "vision"] if history else [],
            default=["text", "vision"] if history else [],
            format_func=lambda x: "Text Diagnosis" if x == "text" else "Image Analysis",
        )
        
        # Severity filter
        all_severities = list(set(h.get("severity", "unknown") for h in history)) if history else []
        severity_filter = st.multiselect(
            "Severity",
            options=all_severities,
            default=all_severities,
        )
        
        # Refresh button
        if st.button("🔄 Refresh from Database", use_container_width=True):
            st.session_state["diagnosis_history"] = load_history_from_db()
            st.rerun()
        
        # Date range
        if history:
            st.divider()
            st.subheader("Actions")
            
            if st.button("Clear All History", type="secondary", use_container_width=True):
                st.session_state["diagnosis_history"] = []
                st.rerun()
    
    # Apply filters
    filtered = history
    if type_filter:
        filtered = [h for h in filtered if h.get("type", "text") in type_filter]
    if severity_filter:
        filtered = [h for h in filtered if h.get("severity", "unknown") in severity_filter]
    
    # Summary stats
    if history:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(history))
        with col2:
            text_count = len([h for h in history if h.get("type") == "text"])
            st.metric("Text Diagnoses", text_count)
        with col3:
            vision_count = len([h for h in history if h.get("type") == "vision"])
            st.metric("Image Analyses", vision_count)
        with col4:
            high_severity = len([h for h in history if h.get("severity") in ["high", "critical", "High", "Critical"]])
            st.metric("High/Critical", high_severity)
        
        st.divider()
    
    # Export buttons
    if filtered:
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            csv_data = generate_history_csv(filtered)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📊 Export as CSV",
                data=csv_data,
                file_name=f"diagnosis_history_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with col_export2:
            json_data = json.dumps(filtered, indent=2, default=str)
            st.download_button(
                label="📄 Export as JSON",
                data=json_data,
                file_name=f"diagnosis_history_{timestamp}.json",
                mime="application/json",
                use_container_width=True,
            )
    
    # History entries
    if not history:
        st.info("No diagnosis records yet. Run a diagnosis or analyze an image to start building your history.")
        
        # Show how-to
        st.subheader("How to Save Records")
        st.write("""
        1. **Text Diagnosis**: Go to the Diagnosis page, enter symptoms, and click "Run Diagnosis". Results are automatically saved.
        2. **Image Analysis**: Go to the Vision page, upload an X-ray, and click "Analyze Image". Results are automatically saved.
        """)
        return
    
    if not filtered:
        st.warning("No records match your current filters. Try adjusting the filters above.")
        return
    
    # Sort by timestamp (newest first)
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Display entries
    for i, entry in enumerate(filtered):
        timestamp = entry.get("timestamp", "Unknown")
        entry_type = entry.get("type", "text")
        severity = entry.get("severity", "unknown")
        primary = entry.get("primary_finding", entry.get("primary_condition", "Unknown"))
        confidence = entry.get("confidence", 0)
        
        # Severity color
        sev_colors = {
            "critical": ("#dc3545", "🚨", "CRITICAL"),
            "high": ("#fd7e14", "⚠️", "HIGH"),
            "severe": ("#fd7e14", "⚠️", "HIGH"),
            "moderate": ("#ffc107", "🔍", "MODERATE"),
            "low": ("#28a745", "✅", "LOW"),
            "mild": ("#28a745", "✅", "LOW"),
            "Critical": ("#dc3545", "🚨", "CRITICAL"),
            "High": ("#fd7e14", "⚠️", "HIGH"),
            "Moderate": ("#ffc107", "🔍", "MODERATE"),
            "Low": ("#28a745", "✅", "LOW"),
        }
        sev_color, sev_icon, sev_label = sev_colors.get(severity, ("#6c757d", "❓", severity.upper()))
        
        type_icon = "🔬" if entry_type == "vision" else "📝"
        type_label = "Image Analysis" if entry_type == "vision" else "Text Diagnosis"
        
        with st.expander(
            f"{sev_icon} **{primary}** — {timestamp} ({type_icon} {type_label})",
            expanded=(i == 0),
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Severity:** <span style='color:{sev_color};font-weight:bold;'>{sev_label}</span>", unsafe_allow_html=True)
            with col2:
                st.metric("Confidence", f"{confidence * 100:.0f}%")
            with col3:
                st.write(f"**Type:** {type_label}")
            
            # Show symptoms or image info
            if entry_type == "text":
                symptoms = entry.get("symptom_input", entry.get("symptoms", []))
                if isinstance(symptoms, list):
                    symptoms = ", ".join(str(s) for s in symptoms)
                if symptoms:
                    st.write(f"**Input:** {symptoms}")
            elif entry_type == "vision":
                st.write(f"**Primary Finding:** {primary}")
            
            # Conditions found
            conditions = entry.get("conditions", entry.get("diagnosis", []))
            if conditions:
                st.write("**Conditions Identified:**")
                for c in conditions[:5]:
                    if isinstance(c, dict):
                        cond_name = c.get("condition", c.get("disease", c.get("condition_name", "Unknown")))
                        cond_conf = c.get("confidence", 0)
                        st.write(f"  • {cond_name} ({cond_conf * 100:.0f}%)")
                    else:
                        st.write(f"  • {c}")
            
            # Recommendations
            recommendations = entry.get("recommendations", [])
            if recommendations:
                st.write("**Recommendations:**")
                for j, rec in enumerate(recommendations, 1):
                    st.write(f"  {j}. {rec}")
            
            # View full result
            if st.button(f"View Full Details #{i+1}", key=f"view_full_{i}"):
                with st.expander("Full Result Data", expanded=True):
                    st.json(entry.get("result", entry))
            
            # Delete button
            if st.button(f"Delete", key=f"delete_{i}", type="secondary"):
                history.remove(entry)
                st.session_state["diagnosis_history"] = history
                st.rerun()


def generate_history_csv(history: list) -> bytes:
    """Generate CSV export of history records."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        "Timestamp", "Type", "Primary Finding/Condition",
        "Severity", "Confidence", "Symptoms/Input",
        "Conditions", "Recommendations",
    ])
    
    for entry in history:
        conditions = entry.get("conditions", entry.get("diagnosis", []))
        if isinstance(conditions, list):
            conditions_str = "; ".join(
                f"{c.get('condition', c.get('disease', 'Unknown'))} ({c.get('confidence', 0)*100:.0f}%)"
                if isinstance(c, dict) else str(c)
                for c in conditions
            )
        else:
            conditions_str = str(conditions)
        
        recommendations = "; ".join(entry.get("recommendations", []))
        symptoms = entry.get("symptom_input", entry.get("primary_finding", ""))
        if isinstance(symptoms, list):
            symptoms = ", ".join(str(s) for s in symptoms)
        
        writer.writerow([
            entry.get("timestamp", ""),
            entry.get("type", "text"),
            entry.get("primary_finding", entry.get("primary_condition", "")),
            entry.get("severity", ""),
            f"{entry.get('confidence', 0) * 100:.0f}%",
            symptoms,
            conditions_str,
            recommendations,
        ])
    
    return output.getvalue().encode("utf-8")
