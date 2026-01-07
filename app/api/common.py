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



# STATIC_FILE_PATH = Path("app.static") 

# @router.get("/static/download", tags=["static"])
# def download_static_files():
#     """
#     Download application static file.
#     """
#     if not STATIC_FILE_PATH.exists():
#         raise HTTPException(status_code=404, detail="Log file not found")

#     return FileResponse(
#         path=STATIC_FILE_PATH,
#         media_type="text/plain",
#         filename="app.log"
#     )


STATIC_DIR = Path("static")  

@router.get("/static/files", tags=["static"])
def list_static_files():
    if not STATIC_DIR.exists():
        raise HTTPException(status_code=404, detail="Static directory not found")

    files = [
        str(path.relative_to(STATIC_DIR))
        for path in STATIC_DIR.rglob("*")
        if path.is_file()
    ]

    return {
        "base": "static",
        "total_files": len(files),
        "files": files
    }