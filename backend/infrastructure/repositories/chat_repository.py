from domain.models.chat.chat_conversation import ChatConversation
from domain.models.chat.chat_message import ChatMessage


class ChatRepository:
    def __init__(self, logger, db):
        self.db = db

    def list_conversations(self):
        return self.db.query(ChatConversation).order_by(ChatConversation.updated_at.desc(), ChatConversation.id.desc()).all()

    def get_conversation(self, id):
        return self.db.get(ChatConversation, id)

    def messages_for(self, conversation_id):
        return (self.db.query(ChatMessage)
                .filter(ChatMessage.conversation_id == conversation_id)
                .order_by(ChatMessage.id).all())

    def get_message(self, id):
        return self.db.get(ChatMessage, id)

    def replace_from(self, conversation_id, first_removed_id, *items):
        """Delete messages from first_removed_id onwards and save items in one transaction."""
        try:
            if first_removed_id is not None:
                (self.db.query(ChatMessage)
                 .filter(ChatMessage.conversation_id == conversation_id, ChatMessage.id >= first_removed_id)
                 .delete(synchronize_session="fetch"))
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

    def delete_message(self, message):
        try:
            self.db.delete(message)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def save(self, *items):
        try:
            self.db.add_all(items)
            self.db.commit()
            for item in items:
                self.db.refresh(item)
            return items
        except Exception:
            self.db.rollback()
            raise

    def delete_conversation(self, conversation):
        try:
            self.db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation.id).delete()
            self.db.delete(conversation)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
