#!/usr/bin/env python3
"""测试 LLM 接口重构后的功能"""

import os
import sys
# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))

from app.agents.config import AgentConfig
from app.agents.llm import LLMFactory, LLMMessage, MessageRole
from app.agents.nodes import IntentClassificationNode, TableAnalysisNode, ResponseGenerationNode, DirectResponseNode


def test_llm_factory():
    """测试 LLM 工厂"""
    print("=== 测试 LLM 工厂 ===")
    
    # 测试获取可用提供商
    providers = LLMFactory.get_available_providers()
    print(f"可用提供商: {providers}")
    
    # 测试创建不同提供商
    try:
        # 测试 OpenAI 提供商（应该降级到 mock）
        llm = LLMFactory.create_llm(provider="openai", fallback_to_mock=True)
        print(f"OpenAI 提供商创建成功: {type(llm).__name__}")
        
        # 测试模拟提供商
        mock_llm = LLMFactory.create_llm(provider="mock")
        print(f"Mock 提供商创建成功: {type(mock_llm).__name__}")
        
        # 测试消息调用
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content="你是一个测试助手"),
            LLMMessage(role=MessageRole.USER, content="这是一个测试消息")
        ]
        
        response = mock_llm.invoke(messages)
        print(f"Mock 提供商响应: {response.content[:100]}...")
        
    except Exception as e:
        print(f"LLM 工厂测试失败: {str(e)}")


def test_node_classes():
    """测试节点类"""
    print("\n=== 测试节点类 ===")
    
    try:
        # 测试意图分类节点
        intent_node = IntentClassificationNode()
        print(f"意图分类节点创建成功: {type(intent_node.llm).__name__ if intent_node.llm else 'None'}")
        
        # 测试表格分析节点
        analysis_node = TableAnalysisNode()
        print(f"表格分析节点创建成功: {type(analysis_node.llm).__name__ if analysis_node.llm else 'None'}")
        
        # 测试响应生成节点
        response_node = ResponseGenerationNode()
        print(f"响应生成节点创建成功: {type(response_node.llm).__name__ if response_node.llm else 'None'}")
        
        # 测试直接响应节点
        direct_node = DirectResponseNode()
        print(f"直接响应节点创建成功: {type(direct_node.llm).__name__ if direct_node.llm else 'None'}")
        
    except Exception as e:
        print(f"节点类测试失败: {str(e)}")


def test_config():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    print(f"LLM 提供商: {AgentConfig.LLM_PROVIDER}")
    print(f"LLM 模型: {AgentConfig.LLM_MODEL}")
    print(f"LLM 温度: {AgentConfig.LLM_TEMPERATURE}")
    print(f"降级到模拟: {AgentConfig.LLM_FALLBACK_TO_MOCK}")
    print(f"OpenAI API Key: {'已配置' if AgentConfig.OPENAI_API_KEY else '未配置'}")
    
    # 测试配置验证
    is_valid = AgentConfig.validate_config()
    print(f"配置验证结果: {is_valid}")
    
    # 测试获取 LLM 配置
    llm_config = AgentConfig.get_llm_config()
    print(f"LLM 配置: {llm_config}")


def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n=== 测试向后兼容性 ===")
    
    # 测试使用旧的 OPENAI_MODEL 配置
    old_model = AgentConfig.OPENAI_MODEL
    print(f"旧的 OpenAI 模型配置: {old_model}")
    
    # 测试从配置创建 LLM
    try:
        llm = LLMFactory.create_from_config(AgentConfig)
        print(f"从配置创建 LLM 成功: {type(llm).__name__}")
        print(f"LLM 模型名称: {llm.get_model_name()}")
    except Exception as e:
        print(f"从配置创建 LLM 失败: {str(e)}")


if __name__ == "__main__":
    print("开始测试 LLM 接口重构...")
    
    test_config()
    test_llm_factory()
    test_node_classes()
    test_backward_compatibility()
    
    print("\n测试完成！")