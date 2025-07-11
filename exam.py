import click
import random
import time
import subprocess
import json
import os
import yaml
import sys
import select
import signal
from datetime import datetime
from colorama import Fore, Style
from help_formatter import CustomGroup, CustomCommand, COMMAND_HELP

QUESTIONS_DIR = "questions"
HISTORY_FILE = "history.json"

def discover_questions(tags=None):
    questions = []
    for subdir in os.listdir(QUESTIONS_DIR):
        yaml_path = os.path.join(QUESTIONS_DIR, subdir, "metadata.yaml")
        if os.path.exists(yaml_path):
            with open(yaml_path, 'r') as f:
                meta = yaml.safe_load(f)
            meta['dir'] = subdir
            if not tags or any(tag in meta.get('tags', []) for tag in tags):
                questions.append(meta)
    return questions

def run_script(script_path, dry_run):
    if dry_run:
        print(f"{Fore.CYAN}[DRY-RUN] Would run: {script_path}{Style.RESET_ALL}")
        return 0, "Dry-run output"
    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"{Fore.RED}Error: {result.stderr}{Style.RESET_ALL}")
        return result.returncode, result.stdout
    except Exception as e:
        print(f"{Fore.RED}Script error: {e}{Style.RESET_ALL}")
        return 1, ""

@click.group(cls=CustomGroup)
def cli():
    pass

@cli.command(cls=CustomCommand, help=COMMAND_HELP["add_question"])
@click.option('--name', required=True, help="Name of the new question (e.g., 'New Kubelet Issue'). Will be used for the subdirectory name (lowercased, spaces to hyphens).")
@click.option('--tags', multiple=True, help="Tags for the question (e.g., --tags kubelet --tags troubleshooting). Can be used to filter during exams.")
def add_question(name, tags):
    q_dir = os.path.join(QUESTIONS_DIR, name.replace(" ", "-").lower())
    os.makedirs(q_dir, exist_ok=True)
    yaml_path = os.path.join(q_dir, "metadata.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump({
            "name": name,
            "description": "Edit this description",
            "hint": "Add a hint for this question",
            "tags": list(tags),
            "setup_script": "setup.sh",
            "verify_script": "verify.sh",
            "cleanup_script": "cleanup.sh",
            "time_limit_minutes": 7
        }, f)
    for script in ["setup.sh", "verify.sh", "cleanup.sh"]:
        with open(os.path.join(q_dir, script), 'w') as f:
            f.write("#!/bin/bash\n# Add your code here\n")
        os.chmod(os.path.join(q_dir, script), 0o755)
    print(f"Created template for '{name}' in {q_dir}")

@cli.command(cls=CustomCommand, help=COMMAND_HELP["list_questions"])
def list_questions():
    questions = discover_questions()
    if not questions:
        print("No questions available. Add some using 'add_question'.")
        return
    print(f"\n{Fore.BLUE}Available Questions:{Style.RESET_ALL}")
    for q in questions:
        print(f"- {q['name']} (Tags: {', '.join(q.get('tags', []))})")
        print(f"{Fore.BLUE}Description:{Style.RESET_ALL} {q['description']}\n")
        if q.get('hint'):
            print(f"{Fore.BLUE}Hint:{Style.RESET_ALL} {q['hint']}\n")

@cli.command(cls=CustomCommand, help=COMMAND_HELP["start"])
@click.option('--num-questions', type=int, default=5, help="Number of questions to include in the exam (default: 5). Must be <= available questions.")
@click.option('--tags', multiple=True, help="Filter questions by tags (e.g., --tags kubelet --tags troubleshooting). Only questions matching at least one tag are considered.")
@click.option('--dry-run', is_flag=True, help="Run in dry-run mode: Simulates script execution without actual cluster changes or verifies (useful for testing flow).")
def start(num_questions, tags, dry_run):
    def signal_handler(sig, frame):
        sys.stdout.write("\r" + " " * 80 + "\r")  # Clear lines
        sys.stdout.flush()
        print(f"{Fore.CYAN}Quitting exam due to interrupt...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Cleaning up...{Style.RESET_ALL}")
        run_script(os.path.join(QUESTIONS_DIR, q['dir'], q['cleanup_script']), dry_run)
        print(f"{Fore.BLUE}=== Exam Terminated ==={Style.RESET_ALL}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    questions = discover_questions(tags)
    if len(questions) < num_questions:
        print(f"{Fore.RED}Error: Only {len(questions)} questions available. Add more using 'add_question' or reduce --num-questions. Run 'list_questions' to see available questions.{Style.RESET_ALL}")
        return
    selected = random.sample(questions, num_questions)
    random.shuffle(selected)
    
    total_time = num_questions * 7
    print(f"\n{Fore.BLUE}=== Starting Exam ==={Style.RESET_ALL}")
    print(f"Questions: {num_questions}")
    print(f"Estimated Time: {total_time} minutes")
    print(f"Instructions: Open a separate terminal for fixes (e.g., kubectl, ssh). Use this terminal for the menu/timer ([v] verify, [r] re-show question, [c] cleanup/skip, [q] quit).")
    print(f"{Fore.BLUE}---{Style.RESET_ALL}\n")
    
    score = 0
    for i, q in enumerate(selected, 1):
        print(f"{Fore.BLUE}Question {i}/{num_questions}: {q['name']}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Description:{Style.RESET_ALL} {q['description']}\n")
        if q.get('hint'):
            print(f"{Fore.BLUE}Hint:{Style.RESET_ALL} {q['hint']}\n")
        print(f"{Fore.BLUE}Reminder:{Style.RESET_ALL} Use a separate terminal for fixes; return here to interact.")
        print(f"{Fore.BLUE}---{Style.RESET_ALL}")
        
        run_script(os.path.join(QUESTIONS_DIR, q['dir'], q['setup_script']), dry_run)
        
        start_time = time.time()
        time_limit = q['time_limit_minutes'] * 60
        print()  # Blank line for prompt and timer
        while True:
            elapsed = time.time() - start_time
            remaining = time_limit - elapsed
            if remaining <= 0:
                sys.stdout.write("\r" + " " * 80 + "\r")  # Clear prompt line
                sys.stdout.flush()
                print(f"{Fore.RED}Time's up!{Style.RESET_ALL}")
                break
            sys.stdout.write(f"\r{Fore.YELLOW}Action: [v] verify, [r] re-show question, [c] cleanup/skip, [q] quit: {Style.RESET_ALL}")
            sys.stdout.flush()
            sys.stdout.write(f"\n{Fore.YELLOW}Time left: {int(remaining // 60)}:{int(remaining % 60):02d}{Style.RESET_ALL}{' ' * 10}")
            sys.stdout.flush()
            
            rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
            if rlist:
                sys.stdout.write("\r" + " " * 80 + "\r\033[F\r" + " " * 80 + "\r")  # Clear timer and prompt lines
                sys.stdout.flush()
                action = sys.stdin.readline().strip().lower()
                if action:
                    print(f"{Fore.YELLOW}Action: [v] verify, [r] re-show question, [c] cleanup/skip, [q] quit: {Style.RESET_ALL}{action}")
                    if action == 'r':
                        print(f"\n{Fore.BLUE}Question {i}/{num_questions}: {q['name']}{Style.RESET_ALL}")
                        print(f"{Fore.BLUE}Description:{Style.RESET_ALL} {q['description']}\n")
                        if q.get('hint'):
                            print(f"{Fore.BLUE}Hint:{Style.RESET_ALL} {q['hint']}\n")
                        print(f"{Fore.BLUE}---{Style.RESET_ALL}")
                    elif action == 'c':
                        print(f"{Fore.CYAN}Skipping question...{Style.RESET_ALL}")
                        break
                    elif action == 'q':
                        print(f"{Fore.CYAN}Quitting exam...{Style.RESET_ALL}")
                        print(f"{Fore.CYAN}Cleaning up...{Style.RESET_ALL}")
                        run_script(os.path.join(QUESTIONS_DIR, q['dir'], q['cleanup_script']), dry_run)
                        print(f"{Fore.BLUE}=== Exam Terminated ==={Style.RESET_ALL}")
                        sys.exit(0)
                    elif action == 'v':
                        rc, _ = run_script(os.path.join(QUESTIONS_DIR, q['dir'], q['verify_script']), dry_run)
                        if rc == 0:
                            print(f"{Fore.GREEN}Verification passed!{Style.RESET_ALL}")
                            score += 1
                        else:
                            print(f"{Fore.RED}Verification failed.{Style.RESET_ALL}")
                        break
            
            sys.stdout.write("\r" + " " * 80 + "\r\033[F\r" + " " * 80 + "\r")  # Clear timer and prompt lines
            sys.stdout.flush()
        
        sys.stdout.write("\r" + " " * 80 + "\r")  # Clear final timer/prompt line
        sys.stdout.flush()
        print(f"{Fore.CYAN}Cleaning up...{Style.RESET_ALL}")
        run_script(os.path.join(QUESTIONS_DIR, q['dir'], q['cleanup_script']), dry_run)
        print(f"{Fore.BLUE}---{Style.RESET_ALL}\n")
    
    percent = (score / num_questions) * 100
    passed = percent > 66
    print(f"{Fore.BLUE}=== Exam Complete ==={Style.RESET_ALL}")
    print(f"Score: {score}/{num_questions} ({percent:.1f}%)")
    print(f"Result: {Fore.GREEN if passed else Fore.RED}{'Pass' if passed else 'Fail'}{Style.RESET_ALL}")
    
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    history = json.loads(content)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Warning: history.json is invalid or empty, starting fresh.{Style.RESET_ALL}")
    history.append({
        "datetime": datetime.now().isoformat(),
        "num_questions": num_questions,
        "score": int(percent),
        "pass": passed
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@cli.command(cls=CustomCommand, help=COMMAND_HELP["history"])
def history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                content = f.read().strip()
                if content:
                    print(json.dumps(json.loads(content), indent=2))
                else:
                    print("No history yet.")
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error: history.json is invalid or empty.{Style.RESET_ALL}")
    else:
        print("No history yet.")

if __name__ == '__main__':
    cli()