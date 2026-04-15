from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select, func
from models.conversation import Conversation, Message, ConversationSummary
from core.exceptions import ConversationNotFoundException, UnauthorizedConversationAccessException
from fastapi import status


class ConversationService:
    def __init__(self, session: Session):
        self.session = session

    def create_conversation(
        self, user_id: int, title: str, metadata: Optional[dict] = None
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id, title=title, metadata=metadata or {}
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: int, user_id: int) -> Conversation:
        conversation = self.session.get(Conversation, conversation_id)
        if not conversation:
            raise ConversationNotFoundException

        if conversation.user_id != user_id:
            raise UnauthorizedConversationAccessException

        return conversation

    def list_conversations(
        self, user_id: int, limit: int = 50, offset: int = 0
    ) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.exec(statement).all())

    def add_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        model_used: Optional[str] = None,
        provider_used: Optional[str] = None,
        token_usage: Optional[dict] = None,
        metadata: Optional[dict] = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            model_used=model_used,
            provider_used=provider_used,
            token_usage=token_usage,
            metadata=metadata or {},
        )
        self.session.add(message)

        conversation = self.session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(message)
        return message

    def get_messages(
        self, conversation_id: int, limit: Optional[int] = None, offset: int = 0
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
        )
        if limit:
            statement = statement.limit(limit)

        return list(self.session.exec(statement).all())

    def count_messages(self, conversation_id: int) -> int:
        statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        return self.session.exec(statement).one()

    def get_latest_summary(
        self, conversation_id: int
    ) -> Optional[ConversationSummary]:
        statement = (
            select(ConversationSummary)
            .where(ConversationSummary.conversation_id == conversation_id)
            .order_by(ConversationSummary.created_at.desc())
            .limit(1)
        )
        return self.session.exec(statement).first()

    def create_summary(
        self,
        conversation_id: int,
        summary_content: str,
        messages_summarized: int,
        model_used: Optional[str] = None,
    ) -> ConversationSummary:
        summary = ConversationSummary(
            conversation_id=conversation_id,
            summary_content=summary_content,
            messages_summarized=messages_summarized,
            model_used=model_used,
        )
        self.session.add(summary)
        self.session.commit()
        self.session.refresh(summary)
        return summary

    def delete_conversation(self, conversation_id: int, user_id: int) -> None:
        conversation = self.get_conversation(conversation_id, user_id)
        self.session.delete(conversation)
        self.session.commit()
