import uuid

sessions: dict[str, dict] = {}


def create_session(
    document_text: str,
    chunks: list[str],
) -> str:
    """Create and store a new session, returning its ID."""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "document_text": document_text,
        "chunks": chunks,
        "chunk_embeddings": [],
        "chat_history": [],
        "status": "embedding",
        "progress": 0,
    }
    return session_id


def get_session(session_id: str) -> dict:
    """Retrieve a session by ID."""
    if session_id not in sessions:
        raise KeyError("Session not found")
    return sessions[session_id]


def append_message(session_id: str, role: str, content: str) -> None:
    """Append a chat message to the session history."""
    session = get_session(session_id)
    session["chat_history"].append({"role": role, "content": content})


def get_recent_history(session_id: str, max_turns: int = 10) -> list[dict]:
    """Return recent conversation turns formatted for Ollama."""
    session = get_session(session_id)
    history = session["chat_history"]
    return history[-(max_turns * 2) :]


def delete_session(session_id: str) -> None:
    """Delete a session if it exists."""
    sessions.pop(session_id, None)
