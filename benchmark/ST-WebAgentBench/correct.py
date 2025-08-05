def flatten_policies(json_list):
    for json_obj in json_list:
        policies = json_obj.get("policies")
        if isinstance(policies, list) and len(policies) > 0:
            # 如果 policies 的第一个元素仍是 list，就说明多嵌套了一层
            if isinstance(policies[0], list):
                # 展平一层
                flattened = []
                for sublist in policies:
                    if isinstance(sublist, list):
                        flattened.extend(sublist)
                    else:
                        flattened.append(sublist)
                json_obj["policies"] = flattened
    return json_list


# 示例使用
import json
import os

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

# Use dynamic path for file
test_file_path = os.path.join(get_project_root(), "benchmark", "ST-WebAgentBench", "stwebagentbench", "test.raw.json")
with open(test_file_path, "r", encoding="utf-8") as f:
    task_list = json.load(f)

task_list = flatten_policies(task_list)

with open("tasks_fixed.json", "w", encoding="utf-8") as f:
    json.dump(task_list, f, indent=4, ensure_ascii=False)
