import logging
import uuid
from app.db import conversations as db_conversations
from app.db import messages as db_messages
from app.llm import provider as llm_provider

logger = logging.getLogger(__name__)

TITLER_PROMPT = "Provide a concise, 3-6 word title for the chat conversation based on the opening exchange, using title case conventions. Respond with only the title: no quotes, no trailing punctuation, no explanation."
MAX_TITLER_CONTENT_CHARS = 1729

def _attachment_hint(msg: dict) -> str:
    """
    Builds a short pure-text indicator of the files a message carries.
    The titler only ever sees text; attachments are summarized as filename + type.
    The mime type comes from upload-time magic-number detection, so it reflects
    the file's real type even when the filename extension lies.
    """
    attachments = msg.get("attachments") or []
    if not attachments:
        return ""
    names = [f"{att['filename']} ({att['mime_type']})" for att in attachments]
    return f" [attachments: {', '.join(names)}]"

async def generate_title(conversation_id: uuid.UUID, force: bool = False) -> str | None:
    """
    Generates and saves a title for a conversation.
    If force=False, only generates if current title is NULL.
    Returns the new title string, or None if skipped/failed.
    """
    conv = await db_conversations.fetch_conversation(conversation_id)
    if not conv:
        return None
        
    if not force and conv['title'] is not None:
        logger.info("Titler: Conversation %s already has title, skipping.", conversation_id)
        return conv['title']
        
    active_leaf_id = conv.get('active_leaf_id')
    if not active_leaf_id:
        logger.warning("Titler: Conversation %s has no active_leaf_id, cannot fetch history.", conversation_id)
        return None
        
    history = await db_messages.fetch_message_history(active_leaf_id)
    
    # Extract first user and assistant messages
    first_user_msg = next((m for m in history if m['role'] == 'user'), None)
    first_assistant_msg = next((m for m in history if m['role'] == 'assistant'), None)
    
    user_content = ""
    if first_user_msg:
        raw_content = first_user_msg['content'] or ""
        user_content = raw_content[:MAX_TITLER_CONTENT_CHARS] + _attachment_hint(first_user_msg)
    assistant_content = first_assistant_msg['content'][:MAX_TITLER_CONTENT_CHARS] if first_assistant_msg and first_assistant_msg['content'] else ""
    
    # Refuse if both are missing/empty
    if not user_content and not assistant_content:
        logger.info("Titler: No user or assistant content found for conversation %s, skipping.", conversation_id)
        return None
        
    combined_content = f"User: {user_content}\nAssistant: {assistant_content}".strip()
    
    messages_payload = [
        {"role": "developer", "content": TITLER_PROMPT},
        {"role": "user", "content": combined_content}
    ]
    
    logger.info("Titler: Requesting generation for conversation %s", conversation_id)
    result = await llm_provider.generate_completion(messages_payload)
    
    if result.get("error") or not result.get("content"):
        logger.error("Titler: LLM call failed or returned empty for conversation %s", conversation_id)
        return None
        
    title = result["content"].strip()
    
    # Normalize: strip surrounding quotes, trailing periods
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    if title.endswith('.'):
        title = title[:-1]
        
    # Cap length to match schema validation
    if len(title) > 137:
        title = title[:137]
        
    # Save to DB
    await db_conversations.update_conversation(conversation_id, title=title)
    logger.info("Titler: Saved new title '%s' for conversation %s", title, conversation_id)
    
    return title