from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from database.db import get_session
from schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationHistoryResponse,
)
from services.conversation_service import ConversationService
from services.context_manager import ContextManager
from services.chat_service import build_chat_service
from schemas.chat import ChatRequest

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def get_conversation_service(session: Session = Depends(get_session)) -> ConversationService:
    return ConversationService(session)


def get_context_manager(session: Session = Depends(get_session)) -> ContextManager:
    return ContextManager(session)


@router.post(
    "/",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
)
def create_conversation(
    request: ConversationCreate,
    user_id: int = 1,  # TODO: Replace with actual auth
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    """
    Create a new conversation thread for a user.
    """
    conversation = service.create_conversation(
        user_id=user_id, title=request.title, metadata=request.metadata
    )
    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        title=conversation.title,
        metadata=conversation.metadata,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        message_count=0,
    )


@router.get(
    "/",
    response_model=list[ConversationResponse],
    summary="List all conversations for a user",
)
def list_conversations(
    user_id: int = 1,  # TODO: Replace with actual auth
    limit: int = 50,
    offset: int = 0,
    service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationResponse]:
    """
    Retrieve all conversations for the authenticated user.
    """
    conversations = service.list_conversations(user_id, limit, offset)
    return [
        ConversationResponse(
            id=conv.id,
            user_id=conv.user_id,
            title=conv.title,
            metadata=conv.metadata,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=service.count_messages(conv.id),
        )
        for conv in conversations
    ]


@router.get(
    "/{conversation_id}",
    response_model=ConversationHistoryResponse,
    summary="Get conversation history",
)
def get_conversation_history(
    conversation_id: int,
    user_id: int = 1,  # TODO: Replace with actual auth
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationHistoryResponse:
    """
    Retrieve full conversation history including all messages.
    """
    conversation = service.get_conversation(conversation_id, user_id)
    messages = service.get_messages(conversation_id)
    summary = service.get_latest_summary(conversation_id)

    return ConversationHistoryResponse(
        conversation=ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            metadata=conversation.metadata,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            message_count=len(messages),
        ),
        messages=[
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                model_used=msg.model_used,
                provider_used=msg.provider_used,
                token_usage=msg.token_usage,
                created_at=msg.created_at,
            )
            for msg in messages
        ],
        has_summary=summary is not None,
        total_messages=len(messages),
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message in a conversation",
)
async def send_message(
    conversation_id: int,
    request: MessageCreate,
    user_id: int = 1,  # TODO: Replace with actual auth
    service: ConversationService = Depends(get_conversation_service),
    context_mgr: ContextManager = Depends(get_context_manager),
) -> MessageResponse:
    """
    Send a message in an existing conversation and get LLM response.

    This endpoint:
    1. Stores the user's message
    2. Builds context using sliding window + summarization
    3. Gets LLM response
    4. Stores the assistant's response
    5. Auto-summarizes if threshold is reached
    """
    service.get_conversation(conversation_id, user_id)

    user_message = service.add_message(
        conversation_id=conversation_id, role="user", content=request.content
    )

    context = context_mgr.build_context(conversation_id)

    chat_service = build_chat_service(
        provider=request.provider,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )

    chat_request = ChatRequest(messages=context)
    response = await chat_service.acomplete(chat_request)

    assistant_message = service.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response.message.content,
        model_used=response.model,
        provider_used=response.provider,
        token_usage=response.usage.dict() if response.usage else None,
    )

    if context_mgr.should_summarize(conversation_id):
        await context_mgr.create_summary(conversation_id, model=request.model)

    return MessageResponse(
        id=assistant_message.id,
        conversation_id=assistant_message.conversation_id,
        role=assistant_message.role,
        content=assistant_message.content,
        model_used=assistant_message.model_used,
        provider_used=assistant_message.provider_used,
        token_usage=assistant_message.token_usage,
        created_at=assistant_message.created_at,
    )


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a conversation",
)
def delete_conversation(
    conversation_id: int,
    user_id: int = 1,  # TODO: Replace with actual auth
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    """
    Delete a conversation and all its messages.
    """
    service.delete_conversation(conversation_id, user_id)
