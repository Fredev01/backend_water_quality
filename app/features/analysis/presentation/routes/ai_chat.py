from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.features.analysis.domain.repository import AnalysisResultRepository
from app.features.analysis.presentation.depends import get_analysis_result
from app.share.ai.domain.services import AIChatService
from app.share.ai.presentation.dependencies import get_ai_service
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token


ai_chat_router = APIRouter(prefix="/ai", tags=["AI Chat"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    context: str
    created_at: str


@ai_chat_router.post("/{analysis_id}/session", response_model=SessionResponse)
async def create_chat_session(
    analysis_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
    ai_service: AIChatService = Depends(get_ai_service),
):
    """
    Create a new AI chat session for an analysis.
    The analysis ID will be used as the session ID.
    """
    try:
        # Get the analysis data
        analysis_data = analysis_result.get_analysis_by_id(
            user_id=user.uid, analysis_id=analysis_id
        )

        if not analysis_data:
            raise HTTPException(
                status_code=404, detail="Análisis no encontrado o sin acceso"
            )

        # Check if analysis is ready
        if analysis_data.get("status") != "saved":
            raise HTTPException(
                status_code=400,
                detail=f"El análisis no está listo. Estado: {analysis_data.get('status')}",
            )

        # Prepare context from analysis data
        context = _prepare_analysis_context(analysis_data)

        # Create chat session with analysis_id as session_id
        session_id = f"{analysis_id}-{user.uid}"

        session = await ai_service.create_session(
            session_id=session_id,
            context=context,
            metadata={
                "analysis_id": analysis_id,
                "analysis_type": analysis_data.get("type"),
                "user_id": user.uid,
                "workspace_id": analysis_data.get("workspace_id"),
                "meter_id": analysis_data.get("meter_id"),
            },
        )

        return SessionResponse(
            session_id=session.id,
            context=session.context,
            created_at=session.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Error al crear sesión de chat")


@ai_chat_router.post("/{analysis_id}/chat", response_model=ChatResponse)
async def chat_with_analysis(
    analysis_id: str,
    request: ChatRequest,
    user: UserPayload = Depends(verify_access_token),
    analysis_result: AnalysisResultRepository = Depends(get_analysis_result),
    ai_service: AIChatService = Depends(get_ai_service),
):
    """
    Send a message to the AI chat for a specific analysis.
    If the session doesn't exist, it will be created automatically.
    """
    try:
        # Check if session exists
        session_id = f"{analysis_id}-{user.uid}"

        session = await ai_service.get_session(session_id)

        # If session doesn't exist, create it
        if not session:
            # Get the analysis data
            analysis_data = analysis_result.get_analysis_by_id(
                user_id=user.uid, analysis_id=analysis_id
            )

            if not analysis_data:
                raise HTTPException(
                    status_code=404, detail="Análisis no encontrado o sin acceso"
                )

            # Check if analysis is ready
            if analysis_data.get("status") != "saved":
                raise HTTPException(
                    status_code=400,
                    detail=f"El análisis no está listo. Estado: {analysis_data.get('status')}",
                )

            # Prepare context from analysis data
            context = _prepare_analysis_context(analysis_data)

            # Create chat session
            session = await ai_service.create_session(
                session_id=session_id,
                context=context,
                metadata={
                    "analysis_id": analysis_id,
                    "analysis_type": analysis_data.get("type"),
                    "user_id": user.uid,
                    "workspace_id": analysis_data.get("workspace_id"),
                    "meter_id": analysis_data.get("meter_id"),
                },
            )

        # Send message and get response
        response = await ai_service.chat(session_id=session_id, message=request.message)

        return ChatResponse(response=response, session_id=analysis_id)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar mensaje")


@ai_chat_router.get("/{analysis_id}/session")
async def get_chat_session(
    analysis_id: str,
    user: UserPayload = Depends(verify_access_token),
    ai_service: AIChatService = Depends(get_ai_service),
):
    """
    Get the chat session for a specific analysis including message history.
    """
    try:
        session_id = f"{analysis_id}-{user.uid}"
        session = await ai_service.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Sesión de chat no encontrada")

        # Verify user has access (check metadata)
        if session.metadata.get("user_id") != user.uid:
            raise HTTPException(status_code=403, detail="Acceso denegado")

        return {
            "session_id": session.id,
            "context": session.context,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in session.messages
            ],
            "metadata": session.metadata,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener sesión")


def _prepare_analysis_context(analysis_data: dict) -> str:
    """
    Prepare a context string from analysis data for the AI chat.
    """
    analysis_type = analysis_data.get("type", "unknown")
    parameters = analysis_data.get("parameters", {})
    data = analysis_data.get("data", {})

    context_parts = [
        f"Tipo de análisis: {analysis_type}",
        f"Parámetros del análisis: {parameters}",
    ]

    # Add data summary based on analysis type
    if data:
        if analysis_type == "average":
            context_parts.append(f"Resultados del análisis de promedio: {data}")
        elif analysis_type == "average_period":
            context_parts.append(
                f"Resultados del análisis de promedio por período: {data}"
            )
        elif analysis_type == "prediction":
            context_parts.append(f"Resultados del análisis de predicción: {data}")
        elif analysis_type == "correlation":
            context_parts.append(f"Resultados del análisis de correlación: {data}")
        else:
            context_parts.append(f"Datos del análisis: {data}")

    return "\n\n".join(context_parts)
