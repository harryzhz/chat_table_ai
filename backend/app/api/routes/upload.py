from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import UploadResponse, ErrorResponse
from app.services.file_service import FileService
from app.services.session_service import SessionService

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    上传文件接口
    
    支持的文件格式：
    - Excel (.xlsx, .xls)
    - CSV (.csv)
    
    返回：
    - 会话ID
    - 文件信息
    - 预览数据
    """
    try:
        # 验证文件
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名不能为空")
        
        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)
        
        # 验证文件格式和大小
        if not FileService.validate_file(file.filename, file_size):
            raise HTTPException(
                status_code=400, 
                detail="不支持的文件格式或文件过大。支持的格式：.xlsx, .xls, .csv，最大50MB"
            )
        
        # 保存并处理文件
        file_info, preview_data = await FileService.save_and_process_file(
            file_content, file.filename
        )
        
        # 创建会话
        session = SessionService.create_session(file_info)
        
        return UploadResponse(
            success=True,
            session_id=session.id,
            file_info=file_info,
            preview_data=preview_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件处理失败：{str(e)}")

@router.get("/upload/status/{session_id}")
async def get_upload_status(session_id: str):
    """获取上传状态"""
    session = SessionService.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    return {
        "session_id": session.id,
        "status": session.status,
        "file_info": session.file_info
    }