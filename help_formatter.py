from colorama import init, Fore, Style
import click

# Initialize colorama for cross-platform color support
init()

class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        formatter.write("CKA Practice Exam CLI Tool\n\n")
        formatter.write("This tool runs simulated Certified Kubernetes Administrator (CKA) exams by selecting and shuffling practice questions from the 'questions/' directory. Each question includes setup, verify, and cleanup scripts.\n\n")
        formatter.write(f"{Fore.BLUE}Available Commands:{Style.RESET_ALL}\n")
        commands = [
            ("add_question", "Add a new question template to the questions directory.", "python3 exam.py add_question --name 'New Kube Issue' --tags kubelet troubleshooting"),
            ("history", "View past exam history from history.json.", "python3 exam.py history"),
            ("list_questions", "List all available questions with names, tags, and descriptions.", "python3 exam.py list_questions"),
            ("start", "Start a practice exam with selected questions.", "python3 exam.py start --num-questions 3 --tags networking --dry-run"),
        ]
        for cmd, desc, ex in commands:
            formatter.write(f"  {Fore.BLUE}{cmd:<15}{Style.RESET_ALL} {desc}\n")
            formatter.write(f"  {' ':<15} {Fore.GREEN}Example: {ex}{Style.RESET_ALL}\n\n")
        formatter.write("Run 'python3 exam.py <command> --help' for detailed options and usage.\n")
        self.format_options(ctx, formatter)

class CustomCommand(click.Command):
    def format_help(self, ctx, formatter):
        formatter.write(f"{Fore.BLUE}Command: {self.name}{Style.RESET_ALL}\n\n")
        formatter.write(f"{self.help}\n\n")
        
        if self.options_metavar:
            formatter.write(f"{Fore.BLUE}Options:{Style.RESET_ALL}\n")
            for param in self.get_params(ctx):
                opts = [opt for opt in param.opts if opt.startswith('--')]
                if not opts:
                    continue
                param_type = param.type.name.upper() if hasattr(param.type, 'name') else 'TEXT'
                if param.multiple:
                    param_type += " (multiple)"
                help_text = param.help or ""
                opt_str = ", ".join(opts)
                formatter.write(f"  {opt_str:<20} {help_text}\n")
                formatter.write(f"  {' ':<20} Type: {param_type}\n\n")
        
        examples = {
            "add_question": "python3 exam.py add_question --name 'New Kube Issue' --tags kubelet troubleshooting",
            "history": "python3 exam.py history",
            "list_questions": "python3 exam.py list_questions",
            "start": "python3 exam.py start --num-questions 3 --tags networking --dry-run"
        }
        if self.name in examples:
            formatter.write(f"{Fore.BLUE}Example:{Style.RESET_ALL}\n")
            formatter.write(f"  {Fore.GREEN}{examples[self.name]}{Style.RESET_ALL}\n\n")
        
        formatter.write(f"Run 'python3 exam.py --help' to see all commands.")

COMMAND_HELP = {
    "add_question": (
        "Add a new question template to the questions directory. Creates a subdirectory with "
        "metadata.yaml and stub bash scripts (setup.sh, verify.sh, cleanup.sh). Edit them to add your question logic."
    ),
    "history": (
        "View the history of past exams from history.json (shows datetime, num_questions, score, pass)."
    ),
    "list_questions": (
        "List all available questions with their names, tags, and descriptions."
    ),
    "start": (
        "Start a practice exam by selecting and shuffling questions.\n\n"
        "The exam runs in this terminal for menu/timer, but open a separate terminal/tab to perform "
        "fixes (e.g., kubectl commands). Questions are pulled from the 'questions/' directory.\n\n"
        "After setup, use the interactive menu: [v] to verify your fix, [r] to re-show the question, "
        "[c] to cleanup and skip, [q] to quit the exam.\n\n"
        "Scoring: >66% is a pass. History is logged to history.json."
    )
}