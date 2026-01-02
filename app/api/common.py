from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

LOG_FILE_PATH = Path("app.log")  # adjust if needed


@router.get("/logs/download", tags=["Logs"])
def download_logs():
    """
    Download application log file.
    """
    if not LOG_FILE_PATH.exists():
        raise HTTPException(status_code=404, detail="Log file not found")

    return FileResponse(
        path=LOG_FILE_PATH,
        media_type="text/plain",
        filename="app.log"
    )
