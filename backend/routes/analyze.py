import json
from flask import Blueprint, request, jsonify
from routes.upload import get_document_text, document_store
from services.analysis_service import (
    perform_master_analysis,
    analyze_document_core,
    detect_hidden_traps,
    explain_like_friend,
    calculate_risk_score,
    detect_suspicious_clauses,
    calculate_trust_score,
    calculate_reality_cost,
)

analyze_bp = Blueprint('analyze', __name__)

# Cache for analysis results
analysis_cache = {}


@analyze_bp.route('/api/analyze/<doc_id>', methods=['POST'])
def full_analysis(doc_id):
    """Run full AI analysis on uploaded document. All 12 features."""
    # Check cache
    if doc_id in analysis_cache:
        return jsonify({"success": True, "cached": True, **analysis_cache[doc_id]})

    try:
        doc_text = get_document_text(doc_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

    if not doc_text or len(doc_text.strip()) < 50:
        return jsonify({"error": "Document text is too short or empty. Please upload a readable PDF."}), 400

    try:
        # Run unified master AI analysis
        master_data = perform_master_analysis(doc_text)
        
        core_info = master_data.get("core_info", {})
        traps = master_data.get("hidden_traps", [])
        explanations = master_data.get("friendly_explanations", [])
        risk_score = master_data.get("risk_score", {})
        suspicious = master_data.get("suspicious_clauses", {})
        trust_score = master_data.get("trust_score", {})
        reality_cost = calculate_reality_cost(core_info)

        result = {
            "doc_id": doc_id,
            "filename": document_store.get(doc_id, {}).get("filename", ""),
            "document_text": doc_text,
            "core_info": core_info,
            "hidden_traps": traps,
            "friendly_explanations": explanations,
            "risk_score": risk_score,
            "suspicious_clauses": suspicious,
            "trust_score": trust_score,
            "reality_cost": reality_cost,
        }

        analysis_cache[doc_id] = result
        return jsonify({"success": True, "cached": False, **result})

    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@analyze_bp.route('/api/analyze/<doc_id>/traps', methods=['GET'])
def get_traps_only(doc_id):
    """Get only hidden traps for a document."""
    if doc_id in analysis_cache:
        return jsonify({"traps": analysis_cache[doc_id].get("hidden_traps", [])})
    try:
        doc_text = get_document_text(doc_id)
        traps = detect_hidden_traps(doc_text)
        return jsonify({"traps": traps})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@analyze_bp.route('/api/analyze/<doc_id>/risk', methods=['GET'])
def get_risk_only(doc_id):
    """Get only risk score for a document."""
    if doc_id in analysis_cache:
        return jsonify(analysis_cache[doc_id].get("risk_score", {}))
    try:
        doc_text = get_document_text(doc_id)
        traps = detect_hidden_traps(doc_text)
        risk = calculate_risk_score(doc_text, traps)
        return jsonify(risk)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
