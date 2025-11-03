# Contributing to Bank Statement RAG Bot

First off, thank you for considering contributing to Bank Statement RAG Bot! It's people like you that make this project better for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct:
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
 - OS: [e.g. macOS, Windows, Linux]
 - Python Version: [e.g. 3.11]
 - Browser (for Streamlit): [e.g. Chrome, Firefox]

**Additional context**
Any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case**: Why would this be useful?
- **Current behavior** vs **desired behavior**
- **Possible implementation**: If you have ideas on how to implement it

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Ensure all existing tests pass
   - Add new tests for new features
   - Test manually with the CLI and Streamlit interface

4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
   
   Use clear commit messages:
   - `feat: Add support for new bank format`
   - `fix: Resolve category matching bug`
   - `docs: Update installation instructions`
   - `refactor: Simplify extraction logic`

5. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots/GIFs if UI changes

## Development Setup

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bank-statement-rag.git
   cd bank-statement-rag
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp config.json.example config.json
   # Add your OpenAI API key
   ```

5. **Run tests** (when available)
   ```bash
   pytest
   ```

## Project Structure

Understanding the codebase:

```
src/
├── extraction.py      # PDF parsing logic - Add support for new formats here
├── processing.py      # Categorization - Add new categories here
├── embeddings.py      # Vector store management
├── query_engine.py    # Query handling logic
└── rag_system.py      # Main orchestrator

streamlit_app/
├── pages/            # Individual page modules
├── charts.py         # Add new chart types here
└── utils.py          # Helper functions
```

## Areas We Need Help With

### High Priority
- [ ] Support for more bank statement formats (BMO, TD, etc.)
- [ ] Unit tests and integration tests
- [ ] Better error handling and logging
- [ ] Performance optimization for large datasets

### Medium Priority
- [ ] Additional categorization rules for different regions
- [ ] New visualization types (spending forecasts, anomaly detection)
- [ ] Multi-language support
- [ ] Mobile-responsive Streamlit interface

### Low Priority
- [ ] Dark mode for Streamlit
- [ ] Export reports in PDF format
- [ ] Email notifications for spending alerts
- [ ] Integration with bank APIs

## Adding Support for New Bank Formats

One of the most valuable contributions is adding support for different bank statement formats:

1. **Create a new extraction function** in `src/extraction.py`:
   ```python
   def extract_bank_name_format(file_path):
       """Extract transactions from Bank Name statements."""
       # Your extraction logic
       return transactions_df
   ```

2. **Add detection logic** to identify the bank format
3. **Test with sample statements** (anonymize sensitive data)
4. **Document the format** in comments

## Coding Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

**Example:**
```python
def categorize_transaction(description: str) -> str:
    """
    Categorize a transaction based on its description.
    
    Args:
        description: Transaction description/merchant name
        
    Returns:
        Category name (e.g., 'groceries', 'dining', 'other')
    """
    # Implementation
```

## Documentation

- Update README.md if you change functionality
- Add docstrings to new functions
- Update code comments for complex logic
- Create examples for new features

## Testing Guidelines

When tests are available:
- Write unit tests for new functions
- Test edge cases
- Ensure tests are reproducible
- Mock external API calls (OpenAI)

## Questions?

- **Open a Discussion** on GitHub for general questions
- **Join our community** (if we create one - Discord/Slack)
- **Email maintainer**: abdulrahmanadetsi@gmail.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in the README

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Bank Statement RAG Bot better!** 