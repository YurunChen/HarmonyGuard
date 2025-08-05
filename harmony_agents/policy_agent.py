#!/usr/bin/env python3
"""
LLM-based Policy Agent - Enhanced with PDF and Webpage processing capabilities
Optimized version that only keeps policy.json output
"""

import os
import json
import asyncio
import re
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
import requests
from bs4 import BeautifulSoup
import pdfplumber

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utility.tools import is_similar, get_reference_limit, read_security_policy_categories

# Import MCP server
from agents.mcp import MCPServerStdio

# Import config loader
from utility.config_loader import get_default_loader
from utility.logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger('policy_agent')

class PolicyAgent_Parse:
    """LLM-based Policy Processing Agent with PDF and Webpage support"""
    
    def __init__(self, mcp_server: MCPServerStdio, processor_context: dict):
        """
        Initialize agent
        
        Args:
            mcp_server: MCP server instance
            processor_context: Processor context information
        """
        self.mcp_server = mcp_server
        self.context = processor_context
        
        # Load OpenAI configuration
        config_loader = get_default_loader()
        try:
            openai_config = config_loader.get_openai_config('policy_agent')
        except KeyError as e:
            logger.error("Missing OpenAI configuration for policy_agent in config.yaml")
            raise ValueError(f"Missing OpenAI configuration: {e}")
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=openai_config['api_key'],
            base_url=openai_config['base_url'],
            timeout=openai_config['timeout']
        )
        
        # Initialize tool descriptions
        self.tool_descriptions = self._get_tool_descriptions()
        self.messages = []
        
        # Create thought process logger
        self.thought_logger = self._create_thought_logger()
        
        logger.info("PolicyAgent initialized with OpenAI client")
    
    def _create_thought_logger(self) -> logging.Logger:
        """Create dedicated logger for thought process"""
        thought_logger = get_logger(f"thought_process.{self.context['organization']}")
        
        # Create log file in process directory
        log_file = os.path.join(self.context["process_dir"], "thought_process.log")
        file_handler = logging.FileHandler(log_file)
        
        # Get logging format from config
        config_loader = get_default_loader()
        logging_config = config_loader.get_logging_config()
        log_format = logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        file_handler.setFormatter(logging.Formatter(log_format))
        thought_logger.addHandler(file_handler)
        
        # Add console handler for real-time debugging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        thought_logger.addHandler(console_handler)
        
        thought_logger.propagate = False
        return thought_logger
    
    def _get_tool_descriptions(self) -> list:
        """Get descriptions of available tools in OpenAI format"""
        tools = [
            {
                "name": "extract_text_from_pdf",
                "description": "Extract text content from a PDF file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pdf_path": {"type": "string", "description": "Path to PDF file"},
                        "output_txt_path": {"type": "string", "description": "Output path for extracted text"},
                        "organization": {"type": "string", "description": "Organization name"},
                        "process_dir": {"type": "string", "description": "Path to processing directory"}
                    },
                    "required": ["pdf_path", "output_txt_path", "organization", "process_dir"]
                }
            },
            {
                "name": "extract_text_from_webpage",
                "description": "Extract text content from a webpage URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "Webpage URL"},
                        "output_txt_path": {"type": "string", "description": "Output path for extracted text"}
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "extract_policies_from_file",
                "description": "Extract policy provisions from a TXT file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to TXT file"},
                        "organization": {"type": "string", "description": "Organization name"},
                        "organization_description": {"type": "string", "description": "Organization description"},
                        "target_subject": {"type": "string", "description": "Target subject"},
                        "policy_db_path": {"type": "string", "description": "Output path for policies"}
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "review_results",
                "description": "Review processing results and generate summary report",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "process_dir": {"type": "string", "description": "Path to processing directory"},
                        "organization": {"type": "string", "description": "Organization name"}
                    },
                    "required": ["process_dir", "organization"]
                }
            }
        ]
        
        # Convert to OpenAI-compatible tool format
        openai_tools = []
        for tool in tools:
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        
        return openai_tools
    
    async def initialize_llm(self):
        """Initialize the LLM with system context"""
        # System prompt
        system_prompt = (
            "You are a Policy Processing Expert. Your task is to process policy documents through the following steps: "
            "1. Extract text from source (PDF, webpage, or TXT) "
            "2. Extract policies from text "
            "3. Review the extracted policies, remove duplicates"
            f"Organization: {self.context['organization']}({self.context['organization_description']}), "
            f"Target Subject: {self.context['target_subject']}. "
            "\n\nAvailable Tools:"
        )
        
        # Add tool descriptions using the raw tool info
        for tool in self.tool_descriptions:
            tool_info = tool['function']
            system_prompt += f"\n- {tool_info['name']}: {tool_info['description']}"
            if 'parameters' in tool_info:
                params = ", ".join(tool_info['parameters']['properties'].keys())
                system_prompt += f"\n  Parameters: {params}"
        
        system_prompt += (
            "\n\nWorkflow Sequence: "
            "1. If input is PDF or webpage, extract text first → "
            "2. Extract policies from text → "
            "3. Review final results and remove duplicates\n\n"
            "Follow these instructions carefully:\n"
            "1. Assess input type before starting (PDF, URL, or TXT)\n"
            "2. Call ONE tool per step and wait for results\n"
            "3. Only call review_results when all previous steps are complete\n"
            "4. Always use the tool call format to invoke tools\n"
            "5. When not calling tools, use regular text messages to reason\n"
            "6. Final review requires generating a comprehensive summary\n"
        )
        
        # Set up initial message history
        self.messages = [{"role": "system", "content": system_prompt}]
        
        # Log system prompt to thought process
        self.thought_logger.info("===== SYSTEM PROMPT =====\n%s\n========================", system_prompt)
        logger.info("LLM context initialized")
    
    async def generate_llm_response(self, user_message: str) -> dict:
        """
        Generate response from the OpenAI model
        
        Args:
            user_message: The user message to send to the model
            
        Returns:
            Model response content
        """
        # Add user message to context
        self.messages.append({"role": "user", "content": user_message})
        
        # Log user message to thought process
        self.thought_logger.info("===== USER INPUT =====\n%s\n======================", user_message)
        
        try:
            # Load OpenAI configuration for model settings
            config_loader = get_default_loader()
            try:
                openai_config = config_loader.get_openai_config('policy_agent')
            except KeyError as e:
                logger.error("Missing OpenAI configuration for policy_agent in config.yaml")
                raise ValueError(f"Missing OpenAI configuration: {e}")
            
            # Generate response using OpenAI API
            response = await self.client.chat.completions.create(
                model=openai_config['model'],
                messages=self.messages,
                tools=self.tool_descriptions,
                tool_choice="auto",
                temperature=openai_config['temperature'],
                max_tokens=openai_config['max_tokens']
            )
            
            # Process the response
            response_message = response.choices[0].message
            self.messages.append(response_message)
            
            # Check for tool calls
            tool_calls = response_message.tool_calls
            
            # Log response to thought process
            if tool_calls:
                log_msg = "===== TOOL CALL =====\n"
                for tool_call in tool_calls:
                    log_msg += (
                        f"Tool: {tool_call.function.name}\n"
                        f"Arguments: {tool_call.function.arguments}\n"
                    )
                log_msg += "====================="
                self.thought_logger.info(log_msg)
            elif response_message.content:
                self.thought_logger.info(
                    "===== REASONING =====\n%s\n=====================", 
                    response_message.content
                )
            else:
                self.thought_logger.warning("Empty LLM response received")

            if tool_calls:
                # Return the first tool call (we only support one tool call per step)
                tool_call = tool_calls[0]
                return {
                    "type": "tool_call",
                    "tool_name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments),
                    "id": tool_call.id  # Capture actual tool call ID
                }
            else:
                # Handle text response
                if response_message.content:
                    return {"type": "text", "content": response_message.content}
                else:
                    logger.warning("No content in model response")
                    return {"type": "error", "message": "No content in model response"}
                
        except Exception as e:
            error_msg = f"Error generating LLM response: {str(e)}"
            logger.error(error_msg)
            self.thought_logger.error("LLM ERROR: %s", error_msg)
            return {"type": "error", "message": error_msg}
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """Execute tool call with improved response handling"""
        # Log tool execution start
        self.thought_logger.info(
            ">>>> EXECUTING TOOL: %s\nParameters: %s", 
            tool_name, 
            json.dumps(parameters, indent=2)
        )
        
        start_time = datetime.now()
        
        try:
            # Prepare parameters based on tool type
            if tool_name == "review_results":
                full_params = {
                    "process_dir": parameters.get("process_dir", ""),
                    "organization": parameters.get("organization", self.context["organization"])
                }
            elif tool_name == "extract_text_from_pdf":
                full_params = {
                    "pdf_path": parameters.get("pdf_path"),
                    "output_txt_path": parameters.get("output_txt_path"),
                    "organization": self.context["organization"],
                    "process_dir": parameters.get("process_dir", "")
                }
            elif tool_name == "extract_policies_from_file":
                full_params = {
                    "organization": self.context["organization"],
                    "organization_description": self.context["organization_description"],
                    "target_subject": self.context["target_subject"],
                    **parameters
                }
            else:
                full_params = parameters
            
            # Call MCP server
            response = await self.mcp_server.call_tool(tool_name, full_params)
            
            # Process response with JSON handling
            result = {"status": "success"}  # Default status
            
            if hasattr(response, 'content') and response.content:
                try:
                    # Attempt to parse as JSON
                    content = response.content[0].text
                    parsed = json.loads(content)
                    
                    # If parsed is a dict, merge with result
                    if isinstance(parsed, dict):
                        result.update(parsed)
                    else:
                        result["result"] = parsed
                except json.JSONDecodeError:
                    # Plain text response
                    result["result"] = response.content[0].text
            else:
                result["result"] = str(response)
            
            # Log successful execution
            exec_time = (datetime.now() - start_time).total_seconds()
            self.thought_logger.info(
                "<<<< TOOL EXECUTION COMPLETE: %s\n"
                "Status: %s\n"
                "Execution Time: %.2fs\n"
                "Result: %s",
                tool_name,
                result.get("status", "success"),
                exec_time,
                json.dumps(result, indent=2)[:1000]  # Limit output length
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Error executing tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            
            # Log error to thought process
            exec_time = (datetime.now() - start_time).total_seconds()
            self.thought_logger.error(
                "<<<< TOOL EXECUTION FAILED: %s\n"
                "Error: %s\n"
                "Execution Time: %.2fs",
                tool_name,
                error_msg,
                exec_time
            )
            
            return {"status": "error", "message": error_msg}
    
    async def extract_text_from_pdf(self, pdf_path: str, output_txt_path: str = None) -> dict:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to PDF file
            output_txt_path: Optional output path for text
            
        Returns:
            Extraction result
        """
        try:
            # Set default output path if not provided
            if not output_txt_path:
                output_txt_path = os.path.join(
                    self.context["process_dir"],
                    f"{self.context['organization']}_extracted_text.txt"
                )
            
            # Extract text from PDF
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n\n"
            
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
            return {"status": "error", "message": error_msg}
    
    async def extract_text_from_webpage(self, url: str, output_txt_path: str = None) -> dict:
        """
        Extract text content from a webpage
        
        Args:
            url: Webpage URL
            output_txt_path: Optional output path for text
            
        Returns:
            Extraction result
        """
        try:
            # Set default output path if not provided
            if not output_txt_path:
                output_txt_path = os.path.join(
                    self.context["process_dir"],
                    f"{self.context['organization']}_extracted_text.txt"
                )
            
            # Fetch webpage content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Load configuration for timeout
            config_loader = get_default_loader()
            try:
                openai_config = config_loader.get_openai_config('policy_agent')
            except KeyError as e:
                logger.error("Missing OpenAI configuration for policy_agent in config.yaml")
                raise ValueError(f"Missing OpenAI configuration: {e}")
            response = requests.get(url, headers=headers, timeout=openai_config['timeout'])
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                element.decompose()
            
            # Get text and clean up
            text = soup.get_text()
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove excessive newlines
            text = text.strip()
            
            # Save extracted text
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            return {
                "status": "success",
                "message": f"Extracted text from webpage and saved to {output_txt_path}",
                "txt_path": output_txt_path
            }
        except Exception as e:
            error_msg = f"Error extracting text from webpage: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    async def run(self, input_path: str):
        """
        Run the policy processing pipeline with enhanced error handling and logging.
        Handles the complete workflow from input to final policy output.
        """
        # Initialize LLM context
        await self.initialize_llm()
        
        # Determine input type
        input_type = self.determine_input_type(input_path)
        
        # Log processing start
        self.thought_logger.info("===== PROCESSING STARTED =====")
        self.thought_logger.info("Input: %s (%s)", input_path, input_type)
        self.thought_logger.info("Organization: %s", self.context["organization"])
        self.thought_logger.info("Target Subject: %s", self.context["target_subject"])
        
        # Initial processing state
        current_state = {
            "step": 1,
            "status": "starting",
            "input_type": input_type,
            "text_extracted": False,
            "file_processed": False,
            "policies_extracted": False,
            "completed": False,
            "error": None
        }
        
        # File paths configuration
        org_name = self.context["organization"]
        files = {
            "input_path": input_path,
            "txt_path": None,
            "policy_path": os.path.join(self.context["process_dir"], f"{org_name}_policies.json"),
            "process_dir": self.context["process_dir"]
        }
        
        logger.info(f"Starting policy processing for: {input_path} (type: {input_type})")
        
        # Agent processing loop
        max_iterations = 25
        for iteration in range(1, max_iterations + 1):
            try:
                # Build state prompt for LLM
                user_prompt = (
                    "Current Processing State:\n"
                    f"{json.dumps(current_state, indent=2)}\n\n"
                    "Available Files:\n"
                    f"{json.dumps(files, indent=2)}\n\n"
                    "Determine the next action based on the current state."
                )
                
                # Log iteration start
                self.thought_logger.info("---- ITERATION %d ----", iteration)
                self.thought_logger.info("Current State:\n%s", json.dumps(current_state, indent=2))
                self.thought_logger.info("Available Files:\n%s", json.dumps(files, indent=2))
                
                # Get agent decision
                logger.debug(f"Iteration {iteration}: Requesting agent decision")
                response = await self.generate_llm_response(user_prompt)
                
                if response.get("type") == "error":
                    raise RuntimeError(f"LLM error: {response.get('message')}")
                
                # Handle tool calls
                if response.get("type") == "tool_call":
                    tool_name = response["tool_name"]
                    params = response.get("arguments", {})
                    
                    logger.info(f"Executing tool: {tool_name} with params: {params}")
                    tool_result = await self.execute_tool(tool_name, params)
                    
                    # Add tool result to message history
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": response["id"],
                        "name": tool_name,
                        "content": json.dumps({
                            "status": tool_result.get("status"),
                            "message": tool_result.get("message", tool_result.get("summary", "Tool executed"))
                        })
                    })
                    
                    # Handle tool-specific state updates
                    if tool_result["status"] != "success":
                        current_state["error"] = tool_result.get("message")
                        continue
                    
                    if tool_name in ["extract_text_from_pdf", "extract_text_from_webpage"]:
                        files["txt_path"] = tool_result.get("txt_path")
                        current_state.update({
                            "text_extracted": True,
                            "status": "text_extracted"
                        })
                    
                    elif tool_name == "extract_policies_from_file":
                        current_state.update({
                            "policies_extracted": True,
                            "file_processed": True,
                            "status": "policies_extracted"
                        })
                    
                    elif tool_name == "review_results":
                        # Safe handling of review results
                        summary_path = tool_result.get("summary_path", "unknown_path")
                        logger.info(f"Processing complete. Summary: {summary_path}")
                        
                        if "summary" in tool_result:
                            logger.info(f"\n{tool_result['summary']}")
                        
                        current_state.update({
                            "completed": True,
                            "status": "completed"
                        })
                        break
                
                # Handle text responses
                elif response.get("type") == "text":
                    logger.debug(f"Agent reasoning: {response.get('content')}")
                    current_state["status"] = "reasoning"
                
                # Check for completion
                if current_state.get("completed"):
                    break
                    
            except Exception as e:
                error_msg = f"Iteration {iteration} failed: {str(e)}"
                logger.error(error_msg, exc_info=True)
                self.thought_logger.error("ITERATION ERROR: %s", error_msg)
                current_state.update({
                    "error": error_msg,
                    "status": "failed"
                })
                break
        
        # Final status logging
        if current_state["completed"]:
            logger.info("Policy processing completed successfully")
            self.thought_logger.info("===== PROCESSING COMPLETED SUCCESSFULLY =====")
        else:
            logger.warning(f"Processing terminated. Final state: {current_state}")
            self.thought_logger.warning(
                "===== PROCESSING TERMINATED =====\n"
                "Final State: %s", 
                json.dumps(current_state, indent=2)
            )
        
        return {
            "status": "completed" if current_state["completed"] else "failed",
            "final_state": current_state,
            "output_files": {
                "policy_file": files["policy_path"],
                "summary_file": os.path.join(files["process_dir"], "processing_summary.md")
            }
        }
    
    def determine_input_type(self, input_path: str) -> str:
        """
        Determine the type of input (PDF, URL, or TXT)
        
        Args:
            input_path: Input path or URL
            
        Returns:
            Input type: 'pdf', 'url', or 'txt'
        """
        # Check if it's a URL
        if input_path.startswith("http://") or input_path.startswith("https://"):
            return "url"
        
        # Check file extension
        input_lower = input_path.lower()
        if input_lower.endswith(".pdf"):
            return "pdf"
        elif input_lower.endswith(".txt"):
            return "txt"
        
        # Default to txt if unknown
        return "txt"
    
class PolicyAgent_Update:
    
    def __init__(self, policy_file_path: str, policy_ids: list[str], reference_example: str, output_file: str):
        self.policy_file_path = policy_file_path
        self.policy_ids = policy_ids
        self.reference_example = reference_example
        self.output_file = output_file
        self.logger = get_logger('policy_agent_update')

    def update_policy(self):
        update_results = {
            "total_policies_loaded": 0,
            "policies_updated": 0,
            "policies_skipped": 0,
            "policies_not_found": 0,
            "details": []
        }
        
        try:
            policies = read_security_policy_categories(self.policy_file_path)
            update_results["total_policies_loaded"] = len(policies)
        except Exception as e:
            self.logger.error(f"Failed to load policy file: {str(e)}")
            return update_results

        if not self.policy_ids:
            return update_results

        for policy_id in self.policy_ids:
            policy = next((p for p in policies if str(p.get("policy_id")) == str(policy_id)), None)

            if not policy:
                update_results["policies_not_found"] += 1
                update_results["details"].append({
                    "policy_id": policy_id,
                    "status": "not_found",
                    "message": f"Policy ID {policy_id} not found in policy file"
                })
                continue

            references = policy.get("reference", [])
            limit = get_reference_limit(policy)

            if any(is_similar(self.reference_example, existing) for existing in references):
                update_results["policies_skipped"] += 1
                update_results["details"].append({
                    "policy_id": policy_id,
                    "status": "skipped",
                    "message": f"Reference too similar to existing ones"
                })
                continue

            if len(references) >= limit:
                references.pop(0)  # Remove oldest reference

            references.append(self.reference_example)
            policy["reference"] = references
            update_results["policies_updated"] += 1
            update_results["details"].append({
                "policy_id": policy_id,
                "status": "updated",
                "message": f"Added new reference, total references: {len(references)}"
            })

        if update_results["policies_updated"] > 0:
            try:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump(policies, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.logger.error(f"Failed to write policy file: {str(e)}")
            
        return update_results
            
            
class PolicyProcessor:
    """
    Policy Processing Controller
    Uses Policy Agent for autonomous processing
    """
    
    def __init__(self, organization: str, organization_description: str, target_subject: str):
        """
        Initialize processor
        
        Args:
            organization: Organization name
            organization_description: Organization description
            target_subject: Target subject
        """
        self.organization = organization
        self.organization_description = organization_description
        self.target_subject = target_subject
        
        # Set output directory to root directory
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "policy_processing_output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create unique process ID
        self.process_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.process_dir = os.path.join(self.output_dir, f"process_{self.process_id}")
        os.makedirs(self.process_dir, exist_ok=True)
        
        logger.info(f"PolicyProcessor initialized for {organization}")
        logger.info(f"Output directory: {self.process_dir}")
    
    async def process_policy_input(self, mcp_server: MCPServerStdio, input_path: str):
        """
        Process policy input using Policy Agent
        
        Args:
            mcp_server: MCP server instance
            input_path: Path to input file (PDF/TXT) or URL
        """
        # Create processor context
        context = {
            "organization": self.organization,
            "organization_description": self.organization_description,
            "target_subject": self.target_subject,
            "process_dir": self.process_dir
        }
        
        # Create and run Policy Agent
        agent = PolicyAgent_Parse(mcp_server, context)
        await agent.run(input_path)


async def main():
    """Main function: Process policy input (PDF, URL, or TXT)"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process policy input (PDF, URL, or TXT)")
    parser.add_argument("--input", "-i", required=True, help="Path to input file (PDF/TXT) or URL")
    parser.add_argument("--organization", "-org", required=True, help="Organization name")
    parser.add_argument("--organization-description", "-desc", default="", help="Organization description")
    parser.add_argument("--target-subject", "-subject", default="User", help="Target subject of policies")
    
    args = parser.parse_args()
    
    # Load MCP configuration
    config_loader = get_default_loader()
    try:
        mcp_config = config_loader.get_config()['mcp_server']
    except KeyError as e:
        logger.error("Missing MCP server configuration in config.yaml")
        raise ValueError(f"Missing MCP server configuration: {e}")
    
    # Initialize environment variables
    env_vars = os.environ.copy()
    
    # Create MCP server instance
    async with MCPServerStdio(
        name="Policy Processing MCP",
        params={
            "command": "python",
            "args": ["-m", "mcp_server"],
            "env": env_vars,
        },
        cache_tools_list=True,
        client_session_timeout_seconds=mcp_config['client_session_timeout'],
    ) as mcp_server:
        # Initialize policy processor
        processor = PolicyProcessor(
            organization=args.organization,
            organization_description=args.organization_description,
            target_subject=args.target_subject
        )
        
        # Execute processing workflow
        await processor.process_policy_input(mcp_server, args.input)

if __name__ == "__main__":
    asyncio.run(main())