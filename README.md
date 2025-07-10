# Tiny CKA Exam Simulator

This is a lightweight CLI tool for practicing CKA (Certified Kubernetes Administrator) exam questions in a simulated environment. It randomly selects and shuffles questions, runs setup scripts to prepare the scenario on your kubeadm cluster, provides timers (7 minutes per question), allows verification of your fixes, and scores the exam (pass if >66%). History of exams is logged for review.

## Features
- **Modular Questions**: Each question is in its own directory under `questions/`, with `metadata.yaml` (config/tags) and bash scripts (`setup.sh`, `verify.sh`, `cleanup.sh`).
- **CLI Commands**: Built with Python and Click for easy use.
- **Timers**: Simple per-question timer (background thread) with total exam time estimate.
- **Dry-Run Mode**: Test the flow without affecting your cluster.
- **Tagging**: Filter questions by tags (e.g., `--tags kubelet`).
- **History Logging**: Basic JSON log of past exams (datetime, num_questions, score, pass).
- **Interactive Menu**: During exams, use [v] to verify, [q] to re-show question, [c] to skip/cleanup.
- **Separate Terminal Workflow**: Work on fixes (e.g., kubectl) in a new terminal/tab while the exam terminal handles the menu/timer.

## Prerequisites
- Ubuntu-based system with Python 3.
- Kubeadm cluster (1 master, 2 nodes: node01, node02) with passwordless SSH from master to nodes.
- kubectl and other Kubernetes tools installed.
- For NetworkPolicy questions: Ensure a CNI like Calico is used (Flannel doesn't enforce policies).

## Installation
1. Clone the repo: `git clone <repo-url> && cd tiny-cka-exam`
2. Install dependencies: `pip install -r requirements.txt` (requires click, pyyaml)
3. Make scripts executable: `chmod +x questions/*/*.sh`

## Usage
- **Start an Exam**: `python3 exam.py start --num-questions 3 --dry-run` (use --tags for filtering, remove --dry-run for real runs).
- **Add a Question**: `python3 exam.py add-question --name "New Question" --tags kubelet --tags troubleshooting` (generates template; edit YAML/scripts).
- **View History**: `python3 exam.py history`
- **Help**: `python3 exam.py --help` or `python3 exam.py <command> --help`

During exams:
- Open a separate terminal for fixes.
- Switch back to exam terminal for menu interactions.

## Adding/Removing Questions
- Add: Use `add-question` command, then edit the generated files.
- Remove: Delete the question's directory under `questions/`.

## Known Limitations
- Timers are simple (no auto-cleanup on timeout).
- Assumes running on the master node with sudo access.
- Dry-run simulates verifies (random pass/fail for testing).

## Contributing
- Add questions by PR-ing new directories.
- Update CHANGELOG.md manually for changes.

For issues, open a GitHub issue.