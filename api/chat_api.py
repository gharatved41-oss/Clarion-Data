from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from services.gemini_chat_service import GeminiChatService
from services.file_ops_service import FileOpsService

router = APIRouter(prefix="/chat", tags=["AI Assistant & Chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="Natural language user query or command")
    dataset_id: Optional[str] = Field(None, description="Active dataset ID context")
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list, description="Recent conversation turns")

class ApplyEditRequest(BaseModel):
    proposal_id: str = Field(..., description="Unique ID of the file edit proposal to apply")

class CancelEditRequest(BaseModel):
    proposal_id: str = Field(..., description="Unique ID of the file edit proposal to cancel")

@router.post("/message")
def chat_message(req: ChatRequest):
    """Processes natural language user requests for data analysis, charting, and code modification."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        response = GeminiChatService.process_chat(
            user_message=req.message,
            dataset_id=req.dataset_id,
            history=req.history
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/apply-edit")
def apply_file_edit(req: ApplyEditRequest):
    """Applies a user-approved file modification with automated backup and syntax checks."""
    result = FileOpsService.apply_edit(req.proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/cancel-edit")
def cancel_file_edit(req: CancelEditRequest):
    """Cancels a pending file modification proposal."""
    result = FileOpsService.cancel_edit(req.proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/project-files")
def get_project_files():
    """Lists accessible project files for the assistant workspace."""
    files = FileOpsService.list_files()
    return {"total_files": len(files), "files": files}

@router.get("/changelog")
def get_ai_changelog():
    """Returns the audit log of applied AI file modifications."""
    return {"changelog": FileOpsService.get_changelog()}
