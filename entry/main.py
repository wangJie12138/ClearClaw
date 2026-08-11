import os
import sys
import time
import asyncio
import random
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from clearclaw.core.filtered_checkpointer import AsyncFilteredCheckpointer
from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.styles import Style
from prompt_toolkit.application import get_app

from clearclaw.core.agent import create_agent_app
from clearclaw.core.config import DB_PATH
from clearclaw.core.bus import task_queue
from clearclaw.core.heartbeat import pacemaker_loop

from clearclaw.core.rag.retriever import ensure_indexed
from .cli import config_wizard
from dotenv import load_dotenv

from pathlib import Path

# 当前retriever.py文件
THIS_FILE = Path(__file__).resolve()
# core目录
CORE_DIR = THIS_FILE.parent
# core的上级：clearclaw
CLEARCLAW_ROOT = CORE_DIR.parent
# 知识库目录（外层workspace）
DEFAULT_KNOWLEDGE_DIR = CLEARCLAW_ROOT / "workspace" / "knowledge"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_line(text: str, delay: float = 0.008):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def print_banner():
    clear_screen()

    CYAN = '\033[38;5;51m'
    PURPLE = '\033[38;5;141m'
    SILVER = '\033[38;5;250m'
    DIM = '\033[2m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    WHITE = '\033[37m'

    logo = f"""{CYAN}{BOLD}
  ██████╗██╗     ███████╗ █████╗ ██████╗      ██████╗██╗      █████╗ ██╗    ██╗
 ██╔════╝██║     ██╔════╝██╔══██╗██╔══██╗    ██╔════╝██║     ██╔══██╗██║    ██║
 ██║     ██║     █████╗  ███████║██████╔╝    ██║     ██║     ███████║██║ █╗ ██║
 ██║     ██║     ██╔══╝  ██╔══██║██╔══██╗    ██║     ██║     ██╔══██║██║███╗██║
 ╚██████╗███████╗███████╗██║  ██║██║  ██║    ╚██████╗███████╗██║  ██║╚███╔███╔╝
  ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝     ╚═════╝╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝
{RESET}"""

    sub_title = f"{WHITE}{BOLD} 透明 · 记忆 · 协同 · 可信  {RESET}"

    quotes = [
        "Debugging: Where the magic breaks.",
        "First, make it run. Then make it fast.",
        "Undefined behavior is the best feature.",
        "Don’t touch code that already works.",
        "Stack overflow is not a snack.",
        "Documentation is optional, until it isn’t.",
        "If it compiles, it’s almost correct.",
        "Race conditions: invisible gremlins.",
        "Cache invalidation is hard.",
        "Premature optimization is the root of evil.",
        "Logs are your only witness.",
        "Null strikes without warning.",
        "Your local env is a liar.",
        "Production is a different planet.",
        "Comments explain why, not what."
    ]
    quote = random.choice(quotes)
    meta = f" {SILVER}✦{RESET} {CYAN}{quote}{RESET}"

    tip = (
        f"{PURPLE} ✦ {RESET}"
        f"{SILVER}{PURPLE}{BOLD}ClearClaw{RESET} 已完成启动。输入命令开始，输入 {PURPLE}/exit{RESET}{SILVER} 退出。{RESET}\n"
    )

    print(logo)
    print(sub_title)
    print() 
    time.sleep(0.12)
    print(meta)
    print() 
    type_line(tip, delay=0.004)


def cprint(text="", end="\n"):
    print_formatted_text(ANSI(str(text)), end=end)

def check_config():
    """检查配置是否完整，缺失则自动进入配置向导"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)

    # 检查是否有任何 API Key
    has_key = (
        os.getenv("DASHSCOPE_API_KEY") or
        os.getenv("OPENAI_API_KEY") or
        os.getenv("SILICONFLOW_API_KEY") or
        os.getenv("ZHIPU_API_KEY")
    )

    if not has_key:
        print("\n 检测到未配置任何API Key，自动进入配置向导...\n")
        config_wizard()

        # 配置完成后，重新加载 .env
        load_dotenv(env_path, override=True)

        # 再次检查
        has_key = (
            os.getenv("DASHSCOPE_API_KEY") or
            os.getenv("OPENAI_API_KEY") or
            os.getenv("SILICONFLOW_API_KEY") or
            os.getenv("ZHIPU_API_KEY")
        )
        if not has_key:
            print("\n 配置未完成，无法启动。请手动运行: clearclaw config")
            sys.exit(1)

        print("\n 配置完成！\n")

    return True

async def async_main():

    # ===== 自动索引知识库 =====
    ensure_indexed(DEFAULT_KNOWLEDGE_DIR)

    print_banner()
    
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
    
    current_provider = os.getenv("DEFAULT_PROVIDER", "aliyun")
    current_model = os.getenv("DEFAULT_MODEL", "glm-5")

    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory:
        wrapped_memory = AsyncFilteredCheckpointer(memory)
        app = create_agent_app(
            provider_name=current_provider,
            model_name=current_model,
            checkpointer=wrapped_memory
        )
        config = {"configurable": {"thread_id": "local_geek_master"}}

        class SpinnerState:
            action_words = [
                "Thinking...",              
                "Working...",               
                "Beep boop...",             
                "Eating bugs...",           
                "Charging battery...",      
                "Brewing coffee...",        
                "Blinking lights...",       
                "Polishing pixels...",      
                "Scanning matrix...",       
                "Warming up circuits...",   
                "Syncing data...",          
                "Pinging server..."         
            ]
            current_words = [] 
            is_spinning = False
            start_time = 0
            frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            is_tool_calling = False 
            tool_msg = ""           

        spinner = SpinnerState()


        def get_bottom_toolbar():
            if not spinner.is_spinning:
                return ANSI("") 
            
            elapsed = time.time() - spinner.start_time
            if spinner.is_tool_calling:
                display_msg = spinner.tool_msg
            else:
                idx_word = int(elapsed) % len(spinner.current_words)
                display_msg = f"👾 {spinner.current_words[idx_word]}"

            idx_frame = int(elapsed * 12) % len(spinner.frames)
            frame = spinner.frames[idx_frame]
            

            return ANSI(f"\033[38;5;51m{frame}\033[0m \033[38;5;250m{display_msg}\033[0m \033[38;5;141m[{elapsed:.1f}s]\033[0m")

        prompt_message = ANSI("\033[38;5;51m❯\033[0m ")
        placeholder_text = ANSI("\033[3m\033[38;5;242minput...\033[0m")

        async def agent_worker():
            while True:
                user_input = await task_queue.get()
                if user_input.lower() in ["/exit", "/quit"]:
                    task_queue.task_done()
                    break
                
                spinner.current_words = spinner.action_words.copy()
                random.shuffle(spinner.current_words)
                
                spinner.start_time = time.time()
                spinner.is_spinning = True
                spinner.is_tool_calling = False
                
                inputs = {"messages": [HumanMessage(content=user_input)]}
                try:
                    async for event in app.astream(inputs, config=config, stream_mode="updates"):
                        for node_name, node_data in event.items():
                            if node_name == "agent":
                                last_msg = node_data["messages"][-1]
                                
                                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                                    for tc in last_msg.tool_calls:
                                        spinner.is_tool_calling = True
                                        spinner.tool_msg = f"唤醒内置工具: {tc['name']}..."
                                        cprint(f"  ●\033[38;5;51m Tool Call: \033[0m{tc['name']}")
                                        cprint('')
                                        
                                elif last_msg.content:
                                    spinner.is_spinning = False
                                    
                                    lines = last_msg.content.strip().split('\n')
                                    if lines:
                                        formatted_out = f"  \033[38;5;141m❯\033[0m \033[38;5;250m{lines[0]}"
                                        for line in lines[1:]:
                                            formatted_out += f"\n    {line}"
                                        formatted_out += "\033[0m" 
                                        cprint(formatted_out)
                                    
                            elif node_name != "agent": 
                                spinner.is_tool_calling = False 
                                
                except Exception as e:
                    spinner.is_spinning = False
                    import traceback
                    err_stack = traceback.format_exc()
                    cprint(f"  \033[31m[!!! 引擎异常 : {e} ]\033[0m")
                    cprint(f"  \033[31m堆栈详情:\n{err_stack}\033[0m")

                spinner.is_spinning = False
                cprint() # 空出舒适的行距
                task_queue.task_done()

        async def user_input_loop():
            custom_style = Style.from_dict({
                'bottom-toolbar': 'bg:default fg:default noreverse',
            })
            
            session = PromptSession(
                bottom_toolbar=get_bottom_toolbar,
                style=custom_style,
                erase_when_done=True,
                reserve_space_for_menu=0  
            )
            
            async def redraw_timer():
                while True:
                    if spinner.is_spinning:
                        try:
                            get_app().invalidate()
                        except Exception:
                            pass
                    await asyncio.sleep(0.08)
                    
            redraw_task = asyncio.create_task(redraw_timer())
            
            while True:
                try:
                    user_input = await session.prompt_async(prompt_message, placeholder=placeholder_text)

                    user_input = user_input.strip()
                    if not user_input:
                        continue
                    

                    padded_bubble = f"  ❯ {user_input}    "
                    cprint(f"\033[48;2;38;38;38m\033[38;5;255m{padded_bubble}\033[0m\n")
                    
                    await task_queue.put(user_input)
                    if user_input.lower() in ["/exit", "/quit"]:
                        cprint("  \033[38;5;141m✦ 记忆已固化，ClearClaw进入休眠。\033[0m")
                        break
                        
                except (KeyboardInterrupt, EOFError):
                    cprint("\n  \033[38;5;141m✦ 强制中断，ClearClaw进入休眠。\033[0m")
                    await task_queue.put("/exit")
                    break

            redraw_task.cancel() 

        with patch_stdout():
            worker = asyncio.create_task(agent_worker())
            heartbeat_worker = asyncio.create_task(pacemaker_loop(task_queue=task_queue, check_interval=10))
            await user_input_loop()
            await task_queue.join()
            worker.cancel()
            heartbeat_worker.cancel()

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()