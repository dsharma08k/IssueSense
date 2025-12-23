"""Export/Import API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any
from app.services.export_service import ExportService
from app.database import get_db, db
from app.utils.auth import get_current_user, get_access_token
from supabase import Client
import json
from io import BytesIO

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/json")
async def export_json(
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Export all issues to JSON format"""
    user_db = db.get_user_client(access_token)
    service = ExportService(user_db)
    data = await service.export_to_json(current_user['id'])
    
    # Return as downloadable JSON file
    json_str = json.dumps(data, indent=2)
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=issuesense_export.json"}
    )


@router.get("/csv")
async def export_csv(
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Export issues to CSV format"""
    user_db = db.get_user_client(access_token)
    service = ExportService(user_db)
    csv_content = await service.export_to_csv(current_user['id'])
    
    if not csv_content:
        raise HTTPException(status_code=404, detail="No issues to export")
    
    # Return as downloadable CSV file
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=issuesense_export.csv"}
    )


@router.post("/import")
async def import_json(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    access_token: str = Depends(get_access_token)
):
    """Import issues from JSON file"""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON files are supported")
    
    try:
        # Read and parse JSON
        content = await file.read()
        json_data = json.loads(content)
        
        # Import
        user_db = db.get_user_client(access_token)
        service = ExportService(user_db)
        result = await service.import_from_json(current_user['id'], json_data)
        
        return {
            "success": True,
            "message": f"Imported {result['imported']} issues, skipped {result['skipped']}",
            **result
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
