# Contributing to Choral LLM Workbench

Thank you for your interest in contributing to the Choral LLM Workbench! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- (Optional) Git LFS for handling large binary files

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/choral-llm-workbench.git
   cd choral-llm-workbench
   ```
3. Install the project in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Install Git LFS hooks (if not already installed):
   ```bash
   git lfs install
   ```

## Development Workflow

### Branch Strategy

- `main`: Primary development branch (protected)
- `feature/feature-name`: Feature development
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes

### Creating Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes following the coding standards below
3. Test your changes thoroughly
4. Commit your changes with descriptive messages
5. Push to your fork and create a pull request

### Code Standards

#### Python Code Style

- Use **Black** for code formatting (configured in pyproject.toml)
- Follow **PEP 8** guidelines
- Use type hints where possible
- Maximum line length: 88 characters

#### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstring format
- Update README.md for user-facing changes
- Add inline comments for complex logic

#### Testing

- Write tests for all new functionality
- Use pytest framework
- Aim for high code coverage
- Place tests in the `tests/` directory

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

Examples:
```
feat(audio): add MIDI export functionality

Add support for exporting scores to MIDI format with configurable
tempo and instrument mapping.

Closes #123
```

```
fix(cli): resolve Gradio app startup issue

Fix the NoneType error when launching the CLI interface without
proper configuration validation.
```

## Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest
   ```
2. **Format code**: Apply Black formatting
   ```bash
   black .
   ```
3. **Lint code**: Run flake8
   ```bash
   flake8 .
   ```
4. **Type check**: Run mypy (if applicable)
   ```bash
   mypy .
   ```
5. **Update documentation**: Update relevant docs and README

### Pull Request Guidelines

1. Use descriptive title and description
2. Link relevant issues in the description
3. Include screenshots for UI changes
4. Add "WIP" (Work in Progress) prefix if not ready for review
5. Request review from maintainers

### Review Process

- Maintainers will review your PR
- Address all feedback promptly
- Keep the PR updated with your latest changes
- Once approved, maintainers will merge the PR

## Project Structure

```
choral-llm-workbench/
├── cli/                 # Command-line interfaces and Gradio apps
├── core/               # Core business logic
│   ├── audio/          # Audio processing
│   ├── editor/         # Score editing
│   ├── llm/           # LLM integration
│   └── score/         # Score handling
├── tests/              # Test suite
├── docs/              # Documentation
├── examples/          # Example files
└── config/            # Configuration management
```

## Handling Binary Files

This project uses Git LFS for large binary files:

- Music files: `.xml`, `.mxl`, `.mid`, `.midi`
- Audio files: `.mp3`, `.wav`, `.flac`
- Archives: `.zip`

These files are automatically tracked by LFS via `.gitattributes`.

## Reporting Issues

When reporting bugs:

1. Use the GitHub issue tracker
2. Provide detailed description of the problem
3. Include steps to reproduce
4. Add relevant error messages and logs
5. Specify your environment (OS, Python version, etc.)

## Asking Questions

- Use GitHub Discussions for general questions
- Check existing issues and discussions first
- Provide context and be specific about your needs

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions. Follow the [Python Community Code of Conduct](https://www.python.org/psf/conduct/).

Thank you for contributing!