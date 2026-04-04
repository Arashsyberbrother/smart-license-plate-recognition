# Contributing Guidelines

Thank you for your interest in contributing to the Smart License Plate Recognition project!

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Create a new issue with:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment info (OS, Python version, etc.)

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Discuss implementation approach

### Submitting Pull Requests

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/your-feature-name`
3. **Make changes** following code style guidelines
4. **Write tests** for new functionality
5. **Run tests**: `cd backend && pytest tests/ -v`
6. **Commit**: Use conventional commits format
7. **Push** and open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/smart-license-plate-recognition.git
cd smart-license-plate-recognition

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov=app

# Frontend setup
cd ../frontend
npm install
npm test
```

## Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Use async/await for I/O operations
- Write docstrings for public functions
- Max line length: 100 characters

### JavaScript/React (Frontend)
- Use functional components with hooks
- Use ES6+ syntax
- Follow React best practices
- Component names in PascalCase
- Utility functions in camelCase

## Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(detection): add support for motorcycle plates

- Added motorcycle plate pattern recognition
- Updated province mapping for motorcycle codes

Closes #42
```

## Testing

- Backend: pytest with minimum 80% coverage
- Frontend: React Testing Library
- All tests must pass before merging

## Review Process

1. Automated CI checks must pass
2. At least one reviewer approval required
3. No merge conflicts
4. Documentation updated if needed
