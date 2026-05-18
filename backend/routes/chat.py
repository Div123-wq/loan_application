import json
from flask import Blueprint, request, jsonify
from routes.upload import get_document_text
from services.github_ai_service import chat

chat_bp = Blueprint('chat', __name__)

# Per-session conversation history
chat_histories = {}

CHAT_SYSTEM = """You are LoanLens AI — a friendly, knowledgeable financial advisor specializing in loan documents.
You speak like a trusted friend who happens to be a financial expert.
You have access to the user's loan document and answer questions about it clearly and honestly.
Keep responses concise (2-4 sentences), warm, and actionable.
Never use legal jargon without immediately explaining it.
Always prioritize the borrower's interests."""

LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
}


@chat_bp.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Feature 9: Voice Conversation AI — chat about the loan document."""
    data = request.get_json()
    doc_id = data.get('doc_id', '')
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    language = data.get('language', 'en')

    if not message:
        return jsonify({"error": "Message is required."}), 400

    # Get document context
    doc_context = ""
    if doc_id:
        try:
            doc_context = get_document_text(doc_id)[:4000]
        except:
            pass

    # Build conversation history
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # Build context-aware system prompt
    lang_name = LANGUAGES.get(language, "English")
    system_with_context = CHAT_SYSTEM
    if doc_context:
        system_with_context += f"\n\nLOAN DOCUMENT CONTEXT:\n{doc_context}"
    if language != 'en':
        system_with_context += f"\n\nIMPORTANT: Respond in {lang_name} language only."

    # Build history string for context
    history = chat_histories[session_id][-6:]  # Last 6 exchanges
    history_text = ""
    for h in history:
        history_text += f"User: {h['user']}\nAssistant: {h['assistant']}\n\n"

    full_user_prompt = f"{history_text}User: {message}"

    try:
        response = chat(system_with_context, full_user_prompt, temperature=0.5)

        # Store in history
        chat_histories[session_id].append({
            "user": message,
            "assistant": response
        })

        return jsonify({
            "success": True,
            "response": response,
            "language": language,
            "session_id": session_id
        })

    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@chat_bp.route('/api/chat/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages."""
    return jsonify({
        "languages": [
            {"code": code, "name": name}
            for code, name in LANGUAGES.items()
        ]
    })


@chat_bp.route('/api/chat/negotiate', methods=['POST'])
def negotiation_assistant():
    """Advanced: AI Negotiation Assistant — what to ask the bank."""
    data = request.get_json()
    doc_id = data.get('doc_id', '')

    doc_text = ""
    if doc_id:
        try:
            doc_text = get_document_text(doc_id)
        except:
            pass

    from services.github_ai_service import chat_json
    prompt = f"""Analyze this loan document and suggest negotiation strategies for the borrower.

LOAN DOCUMENT:
{doc_text[:4000] if doc_text else "Standard home loan with typical terms"}

Return JSON:
{{
  "negotiable_terms": [
    {{
      "term": "Processing Fee",
      "current": "₹10,000 (2%)",
      "negotiable_to": "₹2,500 - ₹5,000",
      "success_probability": "High",
      "how_to_ask": "Exact script to say to the bank"
    }}
  ],
  "questions_for_bank": [
    "Is the foreclosure penalty waivable after 3 years?",
    "Can the processing fee be reduced given my credit score?"
  ],
  "best_time_to_negotiate": "Before signing — never after",
  "leverage_points": [
    "Your good credit score gives you bargaining power",
    "Competition from other lenders you can mention"
  ],
  "red_lines": [
    "Do NOT accept variable rate without rate cap clause"
  ],
  "negotiation_script": "A 3-4 sentence script to open negotiation with the bank"
}}"""

    from services.github_ai_service import chat_json
    result = chat_json(CHAT_SYSTEM, prompt)
    return jsonify({"success": True, **json.loads(result)})


@chat_bp.route('/api/chat/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    """Clear chat history for a session."""
    chat_histories.pop(session_id, None)
    return jsonify({"success": True, "message": "Chat history cleared."})
