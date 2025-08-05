import argparse
import os
import uuid
from datetime import datetime
from time import sleep
from browsergym.experiments import EnvArgs
import gymnasium as gym
import browsergym.core
from dotenv import load_dotenv
import browsergym.webarena
import browsergym.stwebagentbench
import warnings
from st_bench import DemoAgentArgs, action_set
from stwebagentbench.utils.args import parse_arguments
from stwebagentbench.utils.data_collector import DataCollector
import time
import functools
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utility.logger import get_logger

# Initialize logger for this module
logger = get_logger("st_bench_loop")

# Suppress the specific warnings
warnings.filterwarnings("ignore", message="WARN: env.chat to get variables from other wrappers is deprecated")
warnings.filterwarnings("ignore", message="WARN: env.shape to get variables from other wrappers is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="beartype")
warnings.filterwarnings("ignore", category=UserWarning, message="Field .* has conflict with protected namespace .*")
warnings.filterwarnings("ignore", category=UserWarning,
                        message="WARN: The obs returned by the `reset()` method is not within the observation space.")
warnings.filterwarnings("ignore", category=UserWarning,
                        message="WARN: env.page to get variables from other wrappers is deprecated")

__SLOW_MO = 1000 if "DISPLAY_BROWSER" in os.environ else None
__HEADLESS = False if "DISPLAY_BROWSER" in os.environ else True

STWEBAGENTBENCH = "STWebAgentBenchEnv"

def retry_on_exception(max_retries=3, delay=2, backoff=2, exceptions=(Exception,)):
    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"[Retry] Exception in {func.__name__}: {e} (attempt {retries + 1})")
                    time.sleep(current_delay)
                    retries += 1
                    current_delay *= backoff
            raise
        return wrapper
    return decorator_retry

class EvaluationFramework:
    def __init__(self, args):
        load_dotenv()
        self.args = args
        self.SUPPORTED_ENVS = {STWEBAGENTBENCH: self.run_st_bench}

        self.run_id = str(uuid.uuid4())
        self.base_data_path = os.path.join('../../output/stweb')
        os.makedirs(self.base_data_path, exist_ok=True)
        self.data_collector = None

        self.env_args = EnvArgs(
            task_name=args.env_id,
            max_steps=1,
            headless=args.headless,
            viewport={"width": 1500, "height": 1280},
            slow_mo=args.slow_mo,
        )

    def init_data_collector(self, env_id, task_name, exp_i):
        self.data_collector = DataCollector(self.base_data_path, env_id, task_name, exp_i)

    def load_exp_args(self, policies=None):
        self.agent = self.init_agent(self.args, policies)

    def init_agent(self, args, policies):
        return DemoAgentArgs(model_name="gpt-4o-mini").make_agent()

    def eval(self):
        try:
            self.SUPPORTED_ENVS[self.args.env_id]()
        except Exception as e:
            import traceback
            self.data_collector.record_failure(str(e), traceback.format_exc())
            logger.error(f"Error: {str(e)}")
            logger.error(traceback.format_exc())
        finally:
            self.data_collector.save_to_csv()
            self.data_collector.save_to_json()

    def setup_webarena(self):
        pass

    @staticmethod
    def get_next_experiment_number(base_path, env_id, task_name):
        exp_path = os.path.join(base_path, env_id, task_name)
        if not os.path.exists(exp_path):
            return 1
        existing_exps = [d for d in os.listdir(exp_path) if d.startswith('exp_') and os.path.isdir(os.path.join(exp_path, d))]
        if not existing_exps:
            return 1
        return max([int(d.split('_')[1]) for d in existing_exps]) + 1

    @retry_on_exception()
    def safe_add_message(self, chat, role, msg):
        import json
        # Convert None to 'null' string to avoid JS ReferenceError
        if msg is None:
            msg = 'null'
        elif not isinstance(msg, str):
            msg = json.dumps(msg)
        chat.add_message(role, msg)


    @retry_on_exception()
    def safe_reset(self, env):
        return env.reset()

    def agent_loop(self, env, obs, info, max_steps):
        page = env.page
        logger.info(f"Task goal: {obs['goal']}")

        pointer_env = self.get_pointer_env(env)

        state = {
            "next": "",
            "pages": [],
            "page": page,
            "input": obs["goal"],
            "prediction": None,
            "scratchpad": [],
            "observation": "",
            "img": "",
            "annotations": obs,
            "extension_obj": None,
            "actions": "",
            "url": page.url,
            "elements": "",
            "messages": [],
            "env": env,
            "pointer_env": pointer_env,
            "policy": "",
            "update_policy_reason": "First policy to be created",
            "read_page": "",
            "env_policies": obs.get("policies", ""),
        }

        loop_data = {
            'steps': [],
            'total_reward': 0,
            'terminated': False,
            'truncated': False,
            'agent_predictions': []
        }

        done = False
        violated_policies = []
        

        while not done:
            new_obs = self.agent.obs_preprocessor(obs)
            
            # 生成初始action
            action = self.agent.get_action(new_obs)
            if action is None or (isinstance(action, str) and action.strip() == ""):
                logger.info("[Info] Agent returned empty action, ending task loop.")
                break
            
            # 执行action并处理异常
            step_success = False
            max_retries = 3
            retry_count = 0
            step_exception = None
            
            while not step_success and retry_count < max_retries:
                try:
                    # 尝试执行action
                    new_obs, reward, terminated, truncated, new_info = env.step(action)
                    step_success = True
                except Exception as e:
                    retry_count += 1
                    step_exception = e
                    logger.error(f"[Error] Step execution failed: {str(e)}")
                    
                    if retry_count < max_retries:
                        # 重新生成action
                        logger.info(f"[Retry {retry_count}/{max_retries}] Regenerating action...")
                        action = self.agent.get_action(new_obs)
                        if action is None or (isinstance(action, str) and action.strip() == ""):
                            logger.info("[Info] Regenerated action is empty, aborting retry.")
                            break
                    else:
                        logger.error(f"[Error] Max retries reached ({max_retries}), aborting step.")
            
            # 处理执行结果
            if step_success:
                # 执行成功：记录消息和步骤数据
                self.safe_add_message(env.chat, 'assistant', action)
                
                # 更新观察和安全策略信息
                obs, info = new_obs, new_info
                if "safety_report" in info:
                    for policy_report in info['safety_report']:
                        if policy_report['violated']:
                            violated_policies.append(policy_report)
                
                # 记录步骤数据
                step_data = {
                    'action': action,
                    'observation': obs,
                    'reward': reward,
                    'terminated': terminated,
                    'truncated': truncated,
                }
                loop_data['steps'].append(step_data)
                loop_data['total_reward'] += reward
                loop_data['terminated'] = terminated
                loop_data['truncated'] = truncated
                loop_data['task_info_gt'] = info if 'task_info' not in loop_data else loop_data['task_info_gt'] + info
                done = terminated or truncated
                logger.debug(f"Additional Info: {info}")
            else:
                # 执行失败：处理异常情况
                error_msg = f"Step failed after {max_retries} retries"
                if step_exception:
                    error_msg += f": {str(step_exception)}"
                logger.error(f"[Fatal] {error_msg}")
                
                # 记录失败信息
                loop_data['step_error'] = error_msg
                done = True

        # 后续处理保持不变
        logger.info(f"Violated policies: {violated_policies}")
        success_under_policies = len(violated_policies) == 0 and loop_data['total_reward'] >= 1.0
        logger.info(f"Success under policy: {success_under_policies}")
        loop_data['success_under_policies'] = success_under_policies

        if done:
            logger.info("Environment terminated or truncated.")
            last_step = loop_data['steps'][-1] if loop_data['steps'] else None
            if last_step:
                logger.info(f"Final reward: {last_step['reward']}, Terminated: {last_step['terminated']}, Truncated: {last_step['truncated']}")
            return loop_data

        logger.info("Agent loop completed.")
        return loop_data

    def run_st_bench(self):
        if self.args.specific_tasks_range:
            start, end = map(int, self.args.specific_tasks_range.split('-'))
            tasks = browsergym.stwebagentbench.ALL_ST_BENCH_TASK_IDS[start:end + 1]
            if not tasks:
                logger.warning("No tasks found for the specified range.")
                return
        else:
            tasks = browsergym.stwebagentbench.ALL_ST_BENCH_TASK_IDS

        total_rewards = []
        for task in tasks:
            env_id = self.args.env_id.split('.')[0]
            exp_i = self.get_next_experiment_number(self.base_data_path, env_id, task)
            self.init_data_collector(env_id, task, exp_i)

            task_data = {
                'task_name': str(task),
                'start_time': datetime.now().isoformat()
            }

            logger.info(f"Task: {task}")

            env = gym.make(task,
                          headless=True,
                          action_mapping=action_set.to_python_code,
                          timeout=30000)

            obs, info = self.safe_reset(env)
            policies = obs['policies'] if 'policies' in obs else ''
            self.load_exp_args(policies)
            task_data['initial_observation'] = obs
            self.safe_add_message(env.chat, role="assistant", msg="On it. Please wait...")

            loop_data = self.agent_loop(env, obs, info, self.args.max_steps)

            task_data.update(loop_data)
            reward = loop_data['total_reward']
            task_data.update({
                'end_time': datetime.now().isoformat()
            })
            self.data_collector.collect_data(task_data)
            self.data_collector.save_to_csv()
            self.data_collector.save_to_json()

            total_rewards.append(reward)
            sleep(3)
            env.close()

        logger.info(f"Total rewards: {sum(total_rewards)}")
        logger.info(f"Average reward: {sum(total_rewards) / len(total_rewards)}")

    @staticmethod
    def get_pointer_env(env):
        if hasattr(env, 'spec'):
            if env.spec.id.split('.')[0] in [STWEBAGENTBENCH]:
                pointer_env = env.env.env
            else:
                pointer_env = env
        else:
            pointer_env = env

        return pointer_env

def main_sync(args):
    eval_framework = EvaluationFramework(args)
    logger.info("Starting evaluation...")
    eval_framework.eval()
    logger.info("Evaluation completed.")

if __name__ == '__main__':
    argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description='Run the agent')
    args = parse_arguments(parser)
    args.env_id = STWEBAGENTBENCH
    args.specific_tasks_range = "47-47"
    main_sync(args)