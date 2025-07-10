import click
import random
import threading
import time
import subprocess
import json
import os
import yaml
from datetime import datetime

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
        print(f"[DRY-RUN] Would run: {script_path}")
        return 0, "Dry-run output"
    try:
        result = subprocess.run(["bash", script_path], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Error: {result.stderr}")
        return result.returncode, result.stdout
    except Exception as e:
        print(f"Script error: {e}")
        return 1, ""

def simple_timer(minutes, stop_event):
    start = time.time()
    while not stop_event.is_set():
        elapsed = time.time() - start
        remaining = minutes * 60 - elapsed
        if remaining <= 0:
            print("Time's up!")
            break
        print(f"Time left: {int(remaining // 60)}:{int(remaining % 60):02d}", end='\r')
        time.sleep(10)  # Update every 10s for simplicity

@click.group(help="CKA Practice Exam CLI Tool\n\nThis tool allows you to run simulated CKA exams by selecting and shuffling practice questions. Each question has setup, verify, and cleanup scripts. Use 'start' to begin an exam, 'add_question' to create new ones, and 'history' to view past results.\n\nRun commands with --help for more details.")
def cli():
    pass

@cli.command(help="Add a new question template to the questions directory. This creates a subdirectory with metadata.yaml and stub bash scripts (setup.sh, verify.sh, cleanup.sh). Edit them to add your question logic.")
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

@cli.command(help="Start a practice exam by selecting and shuffling questions.\n\nThe exam runs in this terminal for menu/timer, but open a separate terminal/tab to perform fixes (e.g., kubectl commands). Questions are pulled from the 'questions/' directory.\n\nAfter setup, use the interactive menu: [v] to verify your fix, [q] to re-show the question, [c] to cleanup and skip.\n\nScoring: >66% is a pass. History is logged to history.json.")
@click.option('--num-questions', type=int, default=5, help="Number of questions to include in the exam (default: 5). Must be <= available questions.")
@click.option('--tags', multiple=True, help="Filter questions by tags (e.g., --tags kubelet --tags troubleshooting). Only questions matching at least one tag are considered.")
@click.option('--dry-run', is_flag=True, help="Run in dry-run mode: Simulates script execution without actual cluster changes or verifies (useful for testing flow).")
def start(num_questions, tags, dry_run):
    questions = discover_questions(tags)
    if len(questions) < num_questions:
        print(f"Only {len(questions)} questions available.")
        return
    selected = random.sample(questions, num_questions)
    random.shuffle(selected)
    
    total_time = num_questions * 7  # Assuming 7 mins per question
    print(f"\nStarting exam with {num_questions} questions (total estimated time: {total_time} minutes).")
    print("IMPORTANT: Open a separate terminal/tab to work on fixes (e.g., kubectl, ssh). Use this terminal for the menu/timer ([v] verify, [q] re-show question, [c] cleanup/skip).")
    
    score = 0
    for q in selected:
        print(f"\nQuestion: {q['name']}\n{q['description']}")
        print("Reminder: Use a separate terminal for fixes; return here to interact.")
        q_dir = os.path.join(QUESTIONS_DIR, q['dir'])
        
        # Setup
        run_script(os.path.join(q_dir, q['setup_script']), dry_run)
        
        # Timer (simple background)
        stop_event = threading.Event()
        timer_thread = threading.Thread(target=simple_timer, args=(q['time_limit_minutes'], stop_event))
        timer_thread.start()
        
        # Wait for user
        while True:
            action = input("Press [v] to verify, [q] to re-show question, [c] to cleanup/skip: ").lower()
            if action == 'q':
                print(q['description'])
            elif action == 'c':
                break
            elif action == 'v':
                rc, _ = run_script(os.path.join(q_dir, q['verify_script']), dry_run)
                if rc == 0:
                    score += 1
                break
        
        stop_event.set()
        timer_thread.join()
        
        # Cleanup
        run_script(os.path.join(q_dir, q['cleanup_script']), dry_run)
    
    percent = (score / num_questions) * 100
    passed = percent > 66
    print(f"\nScore: {score}/{num_questions} ({percent:.1f}%) - Pass: {passed}")
    
    # Log history
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    history.append({
        "datetime": datetime.now().isoformat(),
        "num_questions": num_questions,
        "score": int(percent),
        "pass": passed
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

@cli.command(help="View the history of past exams from history.json (shows datetime, num_questions, score, pass).")
def history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            print(json.dumps(json.load(f), indent=2))
    else:
        print("No history yet.")

if __name__ == '__main__':
    cli()