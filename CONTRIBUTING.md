# Contributing to mango-disease-ai

Thank you for your interest in improving mango-disease-ai. Bug reports, feature requests,
documentation fixes and code contributions are all welcome.

## Reporting a problem or asking a question

Open an issue at https://github.com/Arpon-30/UI-Changes-Mango/issues and include:

- what you did (code, command or the steps in the web application),
- what you expected and what happened instead (full error message),
- your operating system, Python version and `mango-disease-ai` version
  (`python -c "import mango_disease_ai; print(mango_disease_ai.__version__)"`).

For questions you can also email 23-50158-1@student.aiub.edu.

## Contributing code

1. Fork the repository and create a branch from `main`.
2. Install the package in editable mode with the development tools:

   ```bash
   pip install -e ".[api,dev]"
   ```

3. Make your change. Keep the public API (`analyze()`, `generate_pdf()` and the REST
   endpoints) backward compatible, or explain the change in the pull request.
4. Add or update tests in `tests/` and run them:

   ```bash
   pytest
   ```

5. Add a line to `CHANGELOG.md` under the unreleased version.
6. Open a pull request describing what changed and why.

## Important notes

- The AmropaliNet web application on Streamlit Community Cloud is deployed from `main`
  (`streamlit_app.py`, `requirements.txt`, `templates/`, `static/`). Test it locally with
  `streamlit run streamlit_app.py` before changing these files.
- The trained weights `mango_disease_ai/AA-ENet_proposed.pt` are stored as a normal file
  (not Git LFS) so that ZIP downloads and the PyPI package contain the real model.
  Do not replace them without retraining notes and new evaluation results.
- In user-facing text, use a single hyphen instead of long dashes.

## Code of conduct

Be respectful and constructive. Harassment or discrimination of any kind is not accepted.
