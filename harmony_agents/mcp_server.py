#!/usr/bin/env python3
"""
Policy Extraction MCP Tool for ShieldAgent.
Provides capabilities for extracting text from policy documents (PDF/HTML)
and parsing structured policies from the extracted text.
"""

import os
import json
import pathlib
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import logging
import base64
import queue
import threading
from collections import deque



# For PDF processing
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from datetime import datetime

from fastmcp import FastMCP
from openai import OpenAI

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.tools import chat_text, read_security_policy_categories
from utility.config_loader import get_config_loader, get_default_loader
from utility.logger import get_logger
import pdfplumber
from difflib import SequenceMatcher

# Initialize logger for this module
logger = get_logger("mcp_server")

# Create FastMCP instance
tool_mcp = FastMCP("Policy Extraction Server")

# Load configuration globally - use default loader which searches for config.yaml in parent directories
config_loader = get_default_loader()
try:
    mcp_config = config_loader.get_config()['mcp_server']
    model_config = mcp_config['openai']
    logger.info("Using OpenAI configuration")
except KeyError as e:
    logger.error("Missing MCP server configuration in config.yaml")
    raise ValueError(f"Missing MCP server configuration: {e}")

# Initialize OpenAI client globally
try:
    openai_client = OpenAI(
        api_key=model_config['api_key'],
        base_url=model_config['base_url']
    )
except KeyError as e:
    logger.error(f"Missing model configuration field: {e}")
    raise ValueError(f"Missing model configuration field: {e}")

# Add a global variable to store the pending document sections
# Using a thread-safe queue to store the sections
document_sections_queue = queue.Queue()
visited_sections = set()  # To track which sections have already been visited
    

@tool_mcp.tool()
def extract_text_from_pdf(
    pdf_path: str,
    output_txt_path: Optional[str] = None,
    organization: Optional[str] = None,
    process_dir: Optional[str] = None
) -> dict:
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        output_txt_path (str, optional): Path to save the extracted text. If not provided, it will be generated using organization and process_dir.
        organization (str, optional): Name of the organization, used to generate default output path.
        process_dir (str, optional): Directory to save the output file if output_txt_path is not provided.

    Returns:
        dict: Result containing status, message, and output text path (if successful).
    """
    try:
        # Set default output path if not provided
        if not output_txt_path:
            if not organization or not process_dir:
                raise ValueError("Either output_txt_path or both organization and process_dir must be provided.")
            output_txt_path = os.path.join(
                process_dir,
                f"{organization}_extracted_text.txt"
            )

        # Extract text from PDF
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"

        # Save extracted text
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(text)

        return {
            "status": "success",
            "message": f"Extracted text from PDF and saved to {output_txt_path}",
            "txt_path": output_txt_path
        }

    except Exception as e:
        error_msg = f"Error extracting text from PDF: {str(e)}"
        logger.error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }




@tool_mcp.tool()
def extract_text_from_html(html_path: str, output_txt_path: Optional[str] = None, organization: Optional[str] = None, process_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract text content from an HTML file.
    
    Args:
        html_path: Path to the HTML file
        output_txt_path: Path to save the extracted text. If not provided, it will be generated using organization and process_dir.
        organization: Name of the organization, used to generate default output path.
        process_dir: Directory to save the output file if output_txt_path is not provided.
        
    Returns:
        Dict: Information about the extraction including the file path where text was saved
    """
    try:
        # Set default output path if not provided
        if not output_txt_path:
            if not organization or not process_dir:
                raise ValueError("Either output_txt_path or both organization and process_dir must be provided.")
            output_txt_path = os.path.join(
                process_dir,
                f"{organization}_extracted_text.txt"
            )
        
        # Check if HTML file exists
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        
        # Read HTML file
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get the page title
        title = soup.title.string if soup.title else "No title"
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            element.decompose()
        
        # Extract headings to understand document structure
        headings = []
        for i in range(1, 7):  # h1 to h6
            for heading in soup.find_all(f'h{i}'):
                headings.append(f"h{i}: {heading.get_text(strip=True)}")
        
        # Get text and clean up
        text = soup.get_text(separator='\n')
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
        text = text.strip()
        
        # Format the output
        output = f"--- {title} ---\n\n"
        output += f"Source File: {html_path}\n"
        output += "\n"
        
        if headings:
            output += "--- DOCUMENT STRUCTURE ---\n"
            output += "\n".join(headings)
            output += "\n\n"
        
        output += "--- CONTENT ---\n"
        output += text
        
        # Write the extracted text to the output file
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(output)
            
        logger.info(f"Saved extracted HTML text to {output_txt_path}")
        
        # Get a preview of the content (first 1000 chars)
        preview_count = 1000
        preview = text[:preview_count] + "..." if len(text) > preview_count else text
        
        # Return structured data with file path directly accessible
        result = {
            "success": True,
            "file_path": output_txt_path,
            "txt_path": output_txt_path,
            "source": html_path,
            "title": title,
            "headings_count": len(headings),
            "preview": preview,
            "message": f"""HTML TEXT EXTRACTION COMPLETE:
- Source: {html_path}
- Title: {title}
- Number of headings: {len(headings)}
- Full page content saved to: {output_txt_path}
- Page content preview: {preview}

If needed, USE THIS FILE PATH to extract policies: {output_txt_path}"""
        }
        
        return result
    
    except Exception as e:
        error_msg = f"Error extracting text from HTML: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

@tool_mcp.tool()
def extract_policies_from_file(file_path: str, organization: str, organization_description: str, target_subject: str, policy_db_path: str, user_request: str = "") -> Dict[str, Any]:
    """
    Extract structured policies from a text file and save them to a central JSON file.
    
    Args:
        file_path: Path to the file containing text to extract policies from
        organization: Name of the organization
        
    Returns:
        Dict: A dictionary containing extracted policies and metadata
    """

    # Check if file exists
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File does not exist: {file_path}",
            "policies": [],
            "count": 0
        }
        
    # Read text from file
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
        
    logger.info(f"Read {len(text)} characters from {file_path}")
    
    # Get file info for reference
    file_info = os.path.basename(file_path)
        
    system_prompt = """You are a helpful policy extraction model to identify actionable policies from organizational safety guidelines. Your task is to extract all the meaningful policies from the provided organization handbook which sets restrictions or guidelines for user or entity behaviors in this organization. You will extract specific elements from the given policies and guidelines to produce structured and actionable outputs. Meanwhile, you should follow the user's request and extract policies accordingly."""
    
    user_prompt = f"""As a policy extraction model to extract and clean up useful policies from {organization} ({organization_description}), your tasks are:
1. Read and analyze the provided safety policy document (e.g. likely a PDF handbook or HTML website). Specifically, this document may contain irrelevant information such as structure text, headers, footers, etc. However, you should focus on meaningful policies that constrain the behaviors of the target subject {target_subject}.
2. Exhaust all meaningful policies that are concrete and explicitly constrain the behaviors of {target_subject}. You should carefully analyze what are the target audience or subject for each policy, and avoid extracting policies that are not targeting {target_subject}. For example, if the target subject is "user" or "customer" of the organization, you should avoid extracting policies that target "developer" or "employee" of the organization.
3. Extract each individual policy separately into a policy block, where you should try to use the original text from the document as much as possible. Avoid paraphrasing or generalizing the original text that may change the original meaning.
- For each individual policy, extract the following four elements in a block:
   1) Definitions: Any term definitions, boundaries, or interpretative descriptions for the policy to ensure it can be interpreted without any ambiguity. These definitions should be organized in a list.
   2) Scope: Conditions under which this policy is enforceable (e.g. time period, user group).
   3) Policy Description: The exact description of the policy detailing the restriction or guideline targeting {target_subject}.
   4) Reference Examples: (Leave this section empty.)
   5) risk level: the risk level of violating this policy.
4. If the user has provided an additional request, you should follow the user's request and extract policies accordingly. If not, you should extract all the meaningful policies from the document.

USER REQUEST: {user_request}

Here is the document to extract policies from:

---Start of Document---
{text[:150000]}
---End of Document---

**Output format**:
Provide the output in the following JSON format:
```json
[
  {{
    "definitions": ["A list of term definitions or interpretive descriptions."],
    "scope": "Conditions under which the policy is enforceable.",
    "policy_description": "Exact description of the individual policy targeting {target_subject}.",
    "reference": []
  }},
  ...
]
```
"""

    # Initialize policies
    policies = None
    
    # Try up to 3 times to get a valid JSON response
    for _ in range(5):
        try:
            # logger.info(f"user_prompt: {user_prompt}")
            
            response = chat_text(
                prompt=user_prompt, 
                system=system_prompt, 
                model=model_config['model'],
                client=openai_client,
                max_tokens=model_config['max_tokens'], 
                temperature=model_config['temperature'],
                )

            # with open(f"response_{file_info}.txt", "w", encoding="utf-8") as f:
            #     f.write(response)

            # logger.info(f"user_prompt: {user_prompt}")

            # logger.info(f"Internal response: {response}")
            # input("Press Enter to continue...")
            # Extract the JSON part from the response
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
        
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                # Validate JSON by parsing it
                policies = json.loads(json_str)
                logger.info(f"Extracted {len(policies)} policies from {file_path}")
            
            break

        except Exception as e:
            logger.error(f"Error extracting policies from file: {str(e)}")
            # logger.error(f"Response: {response}")
            continue

    if policies is None:
        return {
            "success": False,
            "error": f"Failed to extract policies from {file_path}",
            "policies": [],
            "count": 0
        }
        
    # Add source file information to each policy
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for idx, policy in enumerate(policies):
        policy["source_file"] = file_path
        policy["extraction_time"] = timestamp
    
    # For very large files, handle them in chunks if needed
    if len(text) > 100000:
        logger.info(f"Large file detected ({len(text)} chars). Processing first 100k characters.")
        logger.info(f"Extracted {len(policies)} policies from the first chunk.")
    
    # Create a local file with just the extracted policies from this file
    output_dir = os.path.dirname(file_path)
    local_policies_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(file_path))[0]}_policies.json")
    with open(local_policies_file, 'w', encoding='utf-8') as f:
        json.dump(policies, f, indent=2)
    
    logger.info(f"Saved extracted policies to {local_policies_file}")
    
    # Save to central JSON file if path is provided
    if policy_db_path:
        all_policies = []
        num_existing_policies = 0
        # Load existing policies if the file exists
        if os.path.exists(policy_db_path):
            try:
                with open(policy_db_path, 'r', encoding='utf-8') as f:
                    all_policies = json.load(f)
                    num_existing_policies = len(all_policies)
            except json.JSONDecodeError:
                logger.warning(f"Could not load existing policies from {policy_db_path}. Creating new file.")
        
        # Add new policies
        all_policies.extend(policies)

        policy_counter = num_existing_policies
        for local_policy, global_policy in zip(policies, all_policies):
            global_policy["policy_id"] = policy_counter
            local_policy["policy_id"] = policy_counter
            policy_counter += 1
        
        # Save all policies
        with open(policy_db_path, 'w', encoding='utf-8') as f:
            json.dump(all_policies, f, indent=2)
        
        logger.info(f"Added {len(policies)} policies to policy database file at {policy_db_path}")
    
    
    # Extract policy descriptions for the text portion of the return
    policy_descriptions = [policy.get("policy_description", "No description available") for policy in policies]
    descriptions_text = "\n\n".join([f"{i+1}. {desc}" for i, desc in enumerate(policy_descriptions)])
    
    # Return structured data with all important information
    return {
        "success": True,
        "count": len(policies),
        "policies": policies,
        "policy_descriptions": policy_descriptions,
        "local_file": local_policies_file,
        "policy_db_path": policy_db_path,
        "text_output": f"""EXTRACTED {len(policies)} POLICIES FROM {file_path}:

{descriptions_text}
"""
    }


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


@tool_mcp.tool()
def update_policy(policy_file_path: str, policy_ids: list, reference_examples: str, output_file: str = ""):
    """
    Updates policies by adding reference examples using FIFO logic:
    - If a policy exceeds its reference limit, remove the oldest entry first.
    - Avoids adding similar references.
    """
    if not output_file:
        output_file = policy_file_path

    try:
        all_policies = read_security_policy_categories(policy_file_path)
        logging.info(f"Loaded {len(all_policies)} policies from {policy_file_path}")
    except Exception as e:
        logging.error(f"Failed to load policy file: {str(e)}")
        return

    if not policy_ids:
        logging.info("No policy IDs to update.")
        return

    updated_count = 0

    for policy_id in policy_ids:
        target_policy = next((p for p in all_policies if str(p.get("policy_id")) == str(policy_id)), None)

        if not target_policy:
            logging.warning(f"Policy ID {policy_id} not found.")
            continue

        references = target_policy.get("reference", [])
        limit = get_reference_limit(target_policy)

        # 去重逻辑：新引用与任一已有引用过于相似，则跳过
        if any(is_similar(reference_examples, ref) for ref in references):
            logging.info(f"Reference for policy {policy_id} is too similar to existing ones. Skipping.")
            continue

        # FIFO：如果超过限制，先移除最早的一个引用
        if len(references) >= limit:
            removed = references.pop(0)
            logging.info(f"Policy {policy_id} exceeded limit ({limit}). Removed oldest reference: {removed[:60]}...")

        # 添加新引用
        references.append(reference_examples)
        target_policy["reference"] = references
        updated_count += 1
        logging.info(f"Policy {policy_id} updated with new reference.")

    if updated_count > 0:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_policies, f, indent=2, ensure_ascii=False)
            logging.info(f"Successfully updated {updated_count} policy(ies).")
        except Exception as e:
            logging.error(f"Failed to write updated policy file: {str(e)}")
    else:
        logging.info("No policy updates were applied.")

    

@tool_mcp.tool()
def review_results(process_dir: str, organization: str) -> dict:
    """
    Process and clean policy data in MCP server
    1. Adds sequential numeric policy_id
    2. Removes metadata fields
    3. Generates summary report
    """
    try:
        # File Path Handling
        policy_file = os.path.join(process_dir, f"{organization}_policies.json")
        
        if not os.path.exists(policy_file):
            raise FileNotFoundError(f"Policy file not found: {policy_file}")

        # Data Loading and Validation
        with open(policy_file, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        # Normalize data structure
        policies = raw_data["policies"] if isinstance(raw_data, dict) and "policies" in raw_data else raw_data
        
        if not isinstance(policies, list):
            raise ValueError("Invalid policy data format")

        # Data Cleaning and Transformation
        cleaned_policies = []
        seen_content = set()
        
        for idx, policy in enumerate(policies, start=1):
            # Convert to dict if necessary
            if not isinstance(policy, dict):
                policy = {"content": str(policy)}
            
            # Remove unwanted metadata
            policy.pop("source_file", None)
            policy.pop("extraction_time", None)
            
            # Deduplication
            content_key = json.dumps(
                {k: v for k, v in policy.items() if k != "policy_id"},
                sort_keys=True
            )
            
            if content_key not in seen_content:
                seen_content.add(content_key)
                policy["policy_id"] = idx
                cleaned_policies.append(policy)

        # Save Cleaned Data
        output_data = {"policies": cleaned_policies} if isinstance(raw_data, dict) else cleaned_policies
        with open(policy_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Generate Statistics
        stats = {
            "total_policies": len(cleaned_policies),
            "duplicates_removed": len(policies) - len(cleaned_policies),
        }

        # Create Summary
        summary_content = (
            f"# Policy Processing Report\n\n"
            f"## Organization: {organization}\n"
            f"## Processing Summary\n"
            f"- Final Policies: {stats['total_policies']}\n"
            f"- Duplicates Removed: {stats['duplicates_removed']}\n\n"
            f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        summary_path = os.path.join(process_dir, "processing_summary.md")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)

        # Return result structure
        result = {
            "status": "success",
            "policy_file": policy_file,
            "summary_path": summary_path,
            "summary": summary_content,
            "stats": stats
        }
        
        return result

    except Exception as e:
        return {
            "status": "error",
            "message": f"Policy review failed: {str(e)}",
            "error_type": type(e).__name__
        }


if __name__ == "__main__":
    tool_mcp.run()
