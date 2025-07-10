import argparse
import os
import yaml

QUESTIONS_DIR = "questions"

def main():
    parser = argparse.ArgumentParser(description="Add a new question template")
    parser.add_argument('--name', required=True, help="Name of the question")
    parser.add_argument('--tags', nargs='+', default=[], help="Tags for the question")
    args = parser.parse_args()

    q_dir = os.path.join(QUESTIONS_DIR, args.name.replace(" ", "-").lower())
    os.makedirs(q_dir, exist_ok=True)
    yaml_path = os.path.join(q_dir, "metadata.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump({
            "name": args.name,
            "description": "Edit this description",
            "tags": args.tags,
            "setup_script": "setup.sh",
            "verify_script": "verify.sh",
            "cleanup_script": "cleanup.sh",
            "time_limit_minutes": 7
        }, f)
    for script in ["setup.sh", "verify.sh", "cleanup.sh"]:
        script_path = os.path.join(q_dir, script)
        with open(script_path, 'w') as f:
            f.write("#!/bin/bash\n# Add your code here\n")
        os.chmod(script_path, 0o755)
    print(f"Created template for '{args.name}' in {q_dir}")

if __name__ == "__main__":
    main()