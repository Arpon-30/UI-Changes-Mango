# Changelog

All notable changes to `mango-disease-ai` are listed here. Versions follow
[Semantic Versioning](https://semver.org/).

## [0.2.1] - 2026-11-04

Version described in the SoftwareX article.

### Changed
- Affiliation text on the API welcome page, the bundled guide (`/guide`), `LICENSE` and
  `README.md` now reads American International University-Bangladesh.
- The bundled guide shows the current version number.

No changes to the model, the analysis results or the API.

## [0.2.0] - 2026-11-04

First release built from https://github.com/Arpon-30/UI-Changes-Mango.

### Added
- Bangla PDF reports: `generate_pdf(result, lang="bn")` and the `lang=en|bn` form field
  of `POST /api/report` (bundled Hind Siliguri font, needs `uharfbuzz`).
- Likely affected area outlined on the photo (`marked_base64`) and its share of the image
  (`affected_percent`); not produced for Healthy.
- `create_app(web_root=...)` so a website can be served on top of the REST API.
- Low-memory mode (`MANGO_LOW_MEMORY=1`) for small hosts such as Streamlit Community Cloud.
- Stricter mango check: a second gate combining the CLIP and AA-ENet confidences.

## [0.1.3] - 2026-09-20

Earlier release on [PyPI](https://pypi.org/project/mango-disease-ai/0.1.3/).

### Features
- `analyze()`: CLIP zero-shot mango validation, AA-ENet classification of 7 classes with
  all class probabilities, Grad-CAM++ heatmap and disease information.
- `generate_pdf()`: one-page English PDF diagnosis report.
- FastAPI REST API (`mango-api`): `GET /api/health`, `GET /api/diseases`,
  `POST /api/analyze`, `POST /api/report`, Swagger UI at `/docs`.
- Trained AA-ENet weights bundled in the package.

## [0.1.0] - [0.1.2]

Earlier PyPI releases of the same toolkit.
