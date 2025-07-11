# Changelog

All notable changes to this project will be documented in this file. This is manually updated for now.

## [0.2.0] - 2025-07-11
### Changed
- Moved add question functionality into main exam.py file 
- Added better --help output

### Fixed
- various issues with question and timer formatting
- enabled graceful quit via q 


## [0.1.0] - 2025-07-10
### Added
- Initial repo structure with Python CLI (exam.py) using Click for commands: start, add-question, history.
- Modular questions directory with YAML metadata and bash scripts (setup/verify/cleanup).
- Random shuffling/selection of questions.
- Simple background timer per question (7 mins default).
- Scoring (>66% pass) and JSON history logging.
- Dry-run mode for testing.
- Interactive menu during exams ([v], [q], [c]).
- Tagging system for question filtering.
- Instructions for separate terminal workflow.
- Initial 3 questions: kubelet-config-misconfig, cronjob-curl-nginx, sidecar-logging-error.
- add_question.py as standalone helper (integrated in exam.py).
- README.md with setup/usage.
- CHANGELOG.md for tracking.

### Changed
- N/A (initial release).

### Fixed
- N/A (initial release).