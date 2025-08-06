import os
import base64
import mimetypes
from anthropic import Anthropic
from openai import OpenAI
import re
import json
import logging
from typing import Dict, Any
from difflib import SequenceMatcher

def get_project_root():
    """Dynamically determine the project root directory."""
    # Start from the current file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Walk up the directory tree to find the project root
    # Look for common indicators of project root
    while current_dir != os.path.dirname(current_dir):  # Stop at filesystem root
        # Check for common project root indicators
        if (os.path.exists(os.path.join(current_dir, "config.yaml")) or
            os.path.exists(os.path.join(current_dir, "README.md")) or
            os.path.exists(os.path.join(current_dir, "requirements.txt")) or
            os.path.exists(os.path.join(current_dir, "setup.py")) or
            os.path.exists(os.path.join(current_dir, "pyproject.toml"))):
            return current_dir
        
        current_dir = os.path.dirname(current_dir)
    
    # If no project root found, return the directory containing this file
    return os.path.dirname(os.path.abspath(__file__))

# Extract the JSON part from the result
def extract_json(text):

    json_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', text)
    for block in json_blocks:
        try:
            return json.loads(block.strip())
        except:
            continue
    
    # If still no valid JSON found, raise an exception
    raise ValueError("No valid JSON found in response")

def encode_image(image_path):
    """
    Encode an image file to base64 and return with correct MIME type.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Tuple of (base64_encoded_image, mime_type)
    """

    # raise error if file does not exist
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    # Determine correct MIME type based on file extension
    file_ext = os.path.splitext(image_path)[1].lower()
    mime_type = mimetypes.guess_type(image_path)[0]
    
    # Fallback if mimetypes doesn't recognize the extension
    if not mime_type:
        if file_ext == ".png":
            mime_type = "image/png"
        elif file_ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif file_ext == ".gif":
            mime_type = "image/gif"
        elif file_ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"  # Default fallback
    
    # Read and encode the image
    # try:
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
    return base64_image, mime_type


def chat_text(prompt, system=None, model="gpt-4o", client=None, max_tokens=10000, temperature=0.2):
    # For OpenAI, system message should be included in messages array
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=messages
    )
    result_text = response.choices[0].message.content
    
    return result_text

    
    
def read_security_policy_categories(file_path):
    """
    读取包含安全策略类别的JSON文件并解析为Python对象
    
    参数:
        file_path (str): JSON文件的路径
        
    返回:
        list: 包含所有安全策略类别的列表，每个类别是一个字典
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"错误：文件 '{file_path}' 不存在")
    except json.JSONDecodeError:
        raise ValueError(f"错误：文件 '{file_path}' 不是有效的JSON格式")
    
    
def is_similar(text1, text2, threshold=0.85):
    return SequenceMatcher(None, text1.strip(), text2.strip()).ratio() >= threshold

def get_reference_limit(policy):
    # 支持 future 扩展：根据标签决定引用上限
    tags = policy.get("risk_level", [])
    if "High" in tags:
        return 10
    if "low" in tags:
        return 5
    return 7


def _format_policy_list(policy_list):
    formatted_text = "SECURITY POLICIES SUMMARY\n" + "="*30 + "\n\n"
        
    for policy in policy_list:
        policy_id = policy.get("policy_id", "Unknown")
        formatted_text += f"Policy ID: {policy_id}\n"
            
        if definitions := policy.get("definitions", []):
            formatted_text += "Definitions:\n"
            formatted_text += ''.join(f"  • {d}\n" for d in definitions) + "\n"
            
        if scope := policy.get("scope"):
            formatted_text += f"Scope:\n  {scope}\n\n"
            
        if description := policy.get("policy_description"):
            formatted_text += f"Description:\n  {description}\n\n"
                
        if risk_level := policy.get("risk_level"):
            formatted_text += f"Risk Level:\n  {risk_level}\n\n"
            
        references = policy.get("reference", [])
        formatted_text += "References:\n"
        formatted_text += ''.join(f"  - {r}\n" for r in references) if references else "  (none)\n"
        formatted_text += "\n" + "="*50 + "\n\n"

        return formatted_text

def pretty_print_alignment(result: dict, last_step_message: str):
            # 创建logger
            logger = logging.getLogger('Alignment_Evaluation')
            # Get logging level from config
            from utility.config_loader import get_default_loader
            config_loader = get_default_loader()
            logging_config = config_loader.get_logging_config()
            log_level = getattr(logging, logging_config.get('level', 'INFO'))
            logger.setLevel(log_level)
            
            # 确保logger不会传播到根logger
            logger.propagate = False
            
            # 如果logger没有handler，添加一个
            if not logger.handlers:
                handler = logging.StreamHandler()
                # Get logging format from config
                from utility.config_loader import get_default_loader
                config_loader = get_default_loader()
                logging_config = config_loader.get_logging_config()
                log_format = logging_config.get('format', '%(asctime)s - %(levelname)s - %(message)s')
                formatter = logging.Formatter(log_format)
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            
            divider = "-" * 70
            logger.info(divider)
            logger.info("🔍 [Alignment Evaluation]")
            logger.info(f"{'Threat Risk':25}: {result['threat_risk']}")
            logger.info(f"{'Task Alignment':25}: {result['task_alignment']}")
            logger.info(f"{'Last Step Message':25}:")
            for line in last_step_message.strip().split('\n'):
                logger.info(f">>> {line}")
            logger.info(f"{'Threat Risk Explanation':25}: {result['threat_risk_explanation']}")
            logger.info(f"{'Policy IDs':25}: {result['policy_ids']}")
            logger.info(f"{'Task Alignment Explanation':25}: {result['task_alignment_explanation']}")
            logger.info(f"{'Optimization Guidance':25}: {result['optimization_guidance']}")
            logger.info(divider)

def write_response_to_file(response: str):
    import os
    # 使用相对路径，在当前工作目录下创建文件
    file_path = os.path.join(os.getcwd(), "response.text")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response)
        
def read_response_from_file(file_path=None) -> str:
    import os
    if file_path is None:
        file_path = os.path.join(os.getcwd(), "response.text")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
        