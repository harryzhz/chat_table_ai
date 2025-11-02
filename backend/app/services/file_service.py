import pandas as pd
import os
import uuid
from typing import Dict, List, Any, Tuple
from datetime import datetime
from app.core.config import settings
from app.models.schemas import FileInfo


class FileService:
    """文件处理服务"""

    @staticmethod
    def validate_file(filename: str, file_size: int) -> bool:
        """验证文件格式和大小"""
        # 检查文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in settings.allowed_extensions:
            return False

        # 检查文件大小
        if file_size > settings.max_file_size:
            return False

        return True

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"

        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.1f}{size_names[i]}"

    @staticmethod
    async def save_and_process_file(
        file_content: bytes, filename: str
    ) -> Tuple[FileInfo, List[Dict[str, Any]]]:
        """保存并处理文件"""
        # 生成唯一文件名
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(settings.upload_dir, unique_filename)

        # 保存文件
        with open(filepath, "wb") as f:
            f.write(file_content)

        try:
            # 读取文件数据
            if file_ext.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(filepath)
            elif file_ext.lower() == ".csv":
                # 尝试不同的编码
                try:
                    df = pd.read_csv(filepath, encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(filepath, encoding="gbk")
                    except UnicodeDecodeError:
                        df = pd.read_csv(filepath, encoding="latin-1")
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")

            # 处理 NaN 值
            df = df.fillna("")

            # 创建文件信息
            file_info = FileInfo(
                filename=filename,
                filepath=filepath,
                rows=len(df),
                columns=len(df.columns),
                size=FileService.format_file_size(len(file_content)),
                uploaded_at=datetime.now().isoformat(),
            )

            # 生成预览数据（前200行）
            preview_df = df.head(200)
            preview_data = preview_df.to_dict("records")

            return file_info, preview_data

        except Exception as e:
            # 如果处理失败，删除已保存的文件
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e

    @staticmethod
    def get_dataframe(filepath: str) -> pd.DataFrame:
        """获取文件的 DataFrame"""
        file_ext = os.path.splitext(filepath)[1].lower()

        if file_ext in [".xlsx", ".xls"]:
            return pd.read_excel(filepath)
        elif file_ext == ".csv":
            # 尝试不同的编码
            try:
                return pd.read_csv(filepath, encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    return pd.read_csv(filepath, encoding="gbk")
                except UnicodeDecodeError:
                    return pd.read_csv(filepath, encoding="latin-1")
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    @staticmethod
    def cleanup_file(filepath: str) -> bool:
        """清理文件"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
