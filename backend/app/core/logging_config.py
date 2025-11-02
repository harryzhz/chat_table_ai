"""日志配置模块"""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class LoggingConfig:
    """日志配置类"""
    
    # 日志级别映射
    LOG_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    @classmethod
    def setup_logging(
        cls,
        log_level: str = "INFO",
        log_dir: Optional[str] = None,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True
    ) -> None:
        """
        设置日志配置
        
        Args:
            log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_dir: 日志文件目录，如果为 None 则使用默认目录
            max_file_size: 单个日志文件最大大小（字节）
            backup_count: 保留的日志文件数量
            console_output: 是否输出到控制台
        """
        # 设置日志级别
        level = cls.LOG_LEVELS.get(log_level.upper(), logging.INFO)
        
        # 创建根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建日志格式
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # 文件处理器
        if log_dir is None:
            # 默认日志目录
            log_dir = Path(__file__).parent.parent.parent / "logs"
        else:
            log_dir = Path(log_dir)
        
        # 确保日志目录存在
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 应用日志文件（所有日志）
        app_log_file = log_dir / "app.log"
        app_handler = logging.handlers.RotatingFileHandler(
            filename=app_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        app_handler.setLevel(level)
        app_handler.setFormatter(formatter)
        root_logger.addHandler(app_handler)
        
        # 错误日志文件（只记录 WARNING 及以上级别）
        error_log_file = log_dir / "error.log"
        error_handler = logging.handlers.RotatingFileHandler(
            filename=error_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.WARNING)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        # Agent 专用日志文件
        agent_log_file = log_dir / "agent.log"
        agent_handler = logging.handlers.RotatingFileHandler(
            filename=agent_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        agent_handler.setLevel(level)
        agent_handler.setFormatter(formatter)
        
        # 为 agent 相关的日志记录器添加专用处理器
        agent_logger = logging.getLogger('app.agents')
        agent_logger.addHandler(agent_handler)
        
        # API 请求日志文件
        api_log_file = log_dir / "api.log"
        api_handler = logging.handlers.RotatingFileHandler(
            filename=api_log_file,
            maxBytes=max_file_size,
            backupCount=backup_count,
            encoding='utf-8'
        )
        api_handler.setLevel(level)
        api_handler.setFormatter(formatter)
        
        # 为 API 相关的日志记录器添加专用处理器
        api_logger = logging.getLogger('app.api')
        api_logger.addHandler(api_handler)
        
        logging.info(f"日志系统初始化完成 - 级别: {log_level}, 日志目录: {log_dir}")
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        return logging.getLogger(name)


# 便捷函数
def setup_logging(log_level: str = "INFO", **kwargs) -> None:
    """设置日志配置的便捷函数"""
    LoggingConfig.setup_logging(log_level=log_level, **kwargs)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器的便捷函数"""
    return LoggingConfig.get_logger(name)


# 预定义的日志记录器
def get_agent_logger(module_name: str) -> logging.Logger:
    """获取 Agent 模块的日志记录器"""
    return get_logger(f'app.agents.{module_name}')


def get_api_logger(module_name: str) -> logging.Logger:
    """获取 API 模块的日志记录器"""
    return get_logger(f'app.api.{module_name}')


def get_service_logger(module_name: str) -> logging.Logger:
    """获取服务模块的日志记录器"""
    return get_logger(f'app.services.{module_name}')

def get_app_logger(module_name: str) -> logging.Logger:
    """获取应用模块的日志记录器"""
    return get_logger(f'app.{module_name}')