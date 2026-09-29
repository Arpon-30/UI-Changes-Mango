# AmropaliNet — Deployment & Development Guide

## Project Overview

**AmropaliNet** is a web-based AI system for classifying 7 Amropali mango fruit diseases using the **AA-ENet** model (EfficientNet-B0 + CBAM attention + Transformer encoder). The system provides:

- Real-time disease classification with confidence scores
- Grad-CAM visualization showing which regions contributed to the prediction
- Professional PDF report generation with diagnosis and treatment recommendations
- Mango validation via CLIP zero-shot learning to reject non-mango images
- Dark/light theme support with responsive design
- Disease encyclopedia with flipcard interactions

## Architecture

### Backend Stack
- **Framework**: Flask 3.0+
- **ML**: PyTorch 2.0+, TIMM (EfficientNet, Transformer)
- **Model**: AA-ENet (~5.8M parameters)
- **Inference**: CPU-optimized with CLIP for mango detection
- **Reporting**: FPDF2 for PDF generation
- **Deployment**: Docker (CPU-only for HF Spaces)

### Frontend Stack
- **Templates**: Jinja2 (Flask)
- **Styling**: CSS3 (glassmorphism, dark/light themes)
- **Interactivity**: Vanilla JavaScript (no frameworks)
- **Features**: Drag-drop upload, flipcards, smooth animations, responsive

### Key Files
```
├── app.py              # Flask server, API routes, startup
├── model.py            # AA-ENet architecture, CBAM, model loading
├── inference.py        # Classification, Grad-CAM, mango detection (CLIP)
├── report.py           # PDF report generation with branding
├── Dockerfile          # Multi-stage build, CPU PyTorch
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Jinja2 template with all UI sections
├── static/
│   ├── css/style.css   # Theme system, 1277 lines
│   └── js/main.js      # Event handling, 541 lines
├── .gitattributes      # Git LFS for large model files
└── .gitignore          # Standard Python + .venv
```

### Model Files
- `AA-ENet_proposed.pt` (18 MB) — Trained model weights
- `fruit_classifier.pth` (43 MB) — Legacy classifier (unused, can be removed)

## API Endpoints

### GET /
Serves the main HTML page.

### GET /api/health
Health check endpoint.
```json
{ "status": "ok" }
```

### GET /api/diseases
Returns all disease information (metadata, symptoms, remedies).

### POST /api/classify
**Request**: Multipart form with `image` file
**Response**:
```json
{
  "classification": {
    "predicted_class": "Healthy",
    "confidence": 0.9876,
    "all_scores": [
      {"class": "Healthy", "score": 0.9876},
      {"class": "Anthracnose", "score": 0.0045},
      ...
    ]
  },
  "gradcam": {
    "original_b64": "...",
    "heatmap_b64": "..."
  },
  "disease_info": { ... }
}
```

Errors (422 if not mango, 400 if invalid, 500 if processing fails).

### POST /api/report
**Request**: Multipart form with `image` and `user_name`
**Response**: PDF file (application/pdf)

Errors: 400 (no name), 422 (not mango), 500 (generation failed).

## Deployment

### Local Development
```bash
# Create venv
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or: source .venv/bin/activate  # macOS/Linux

# Install deps
pip install -r requirements.txt

# Run
python app.py
# Visit http://localhost:5000
```

### Docker (HF Spaces)
```bash
docker build -t amropalienet:latest .
docker run -p 7860:7860 amropalienet:latest
```

The Dockerfile:
- Uses `python:3.10-slim` base
- Installs CPU-only PyTorch (saves ~1.5GB)
- Creates non-root user (HF Spaces requirement)
- Runs gunicorn with 1 worker, 4 threads, 120s timeout
- Exposes port 7860

### Environment Variables
None required for basic operation. For production:
- `FLASK_ENV=production` (Flask default)
- `WORKERS=1` (gunicorn, already in Dockerfile)

## Configuration

### Image Processing
- Input size: 224×224 (ImageNet standard)
- Normalization: ImageNet mean/std
- Format: JPEG, PNG, WebP, BMP, TIFF (max 10 MB)

### Mango Validation
- Uses CLIP zero-shot classification
- 8 candidate labels (mango fruit, leaf, non-mango categories)
- Confidence threshold: 50%
- Falls back gracefully with 422 error if rejected

### Disease Classification
- 7 classes: Anthracnose, Bacterial Canker, Healthy, Powdery Mildew, Scab, Sooty Mould, Stem End Rot
- Model confidence threshold (not enforced by API, can be added to frontend)
- Top-1 prediction returned with all class scores

### Grad-CAM
- Targets `model.reduce` layer (after backbone, before Transformer)
- Resized to input image dimensions
- Blended 55% original + 45% heatmap for visualization
- Returned as base64 PNG

## Frontend Features

### Theme Toggle
- Dark theme (default, emerald-on-dark)
- Light theme (emerald-on-light)
- Persisted in `localStorage` as `mangoai-theme`

### Disease Encyclopedia
- 7 flip-cards (click to reveal symptoms & treatment)
- Mirrored data from backend (DISEASE_DATA in main.js)
- Fully responsive grid

### Upload Flow
1. Drag-drop or click to select image
2. Preview appears with remove button
3. Click "Analyze Disease" → loading spinner
4. Results show: confidence ring, disease class, all scores, Grad-CAM, remedies, report form
5. Enter name and download PDF

### Error Handling
- File validation (type, size)
- Network error catching
- Mango detection rejection
- Classification failures → toast notifications
- All feedback is user-friendly (no stack traces)

## Security Considerations

### Input Validation
- ✅ File type checked (MIME + extension)
- ✅ File size limited (10 MB)
- ✅ Image dimensions validated by PyTorch
- ✅ User name sanitized for filename

### Data Handling
- ✅ Images processed in-memory (no disk storage)
- ✅ PDF generated on-the-fly (no persistent storage)
- ✅ No API keys or credentials in code
- ✅ CORS not enabled (single-origin deployment)

### Potential Improvements
- Add rate limiting (e.g., Flask-Limiter)
- Add request logging with IP sanitization
- Add content-security-policy headers
- Implement CSRF protection if forms added

## Performance Optimization

### Model Loading
- Singleton pattern: models loaded once at startup, cached
- PyTorch in eval mode (no gradients except for Grad-CAM)
- CPU inference only (no CUDA dependencies)

### Frontend
- CSS critical path minimized (no external fonts initially)
- JS in IIFE to avoid global scope pollution
- Images served as base64 (no extra requests)
- Lazy loading for disease cards (fade-in on scroll)

### Inference Time (Typical)
- Mango detection: ~0.5–1s (CLIP)
- Classification: ~0.2–0.5s (AA-ENet)
- Grad-CAM: ~0.3–0.8s (backward pass required)
- **Total: ~1–2 seconds** (acceptable for user experience)

## Testing

### Manual Smoke Tests
1. Upload mango fruit image → should classify with high confidence
2. Upload non-mango image → should reject with 422 error
3. Upload very large file (>10MB) → should reject with 400 error
4. Corrupt/invalid image → should reject with 400 error
5. Download PDF report → file should open properly
6. Toggle dark/light theme → should persist on reload
7. Click disease cards → should flip smoothly

### Automated (if added)
```bash
pytest tests/  # (not currently in repo)
```

## Troubleshooting

### Model Loading Fails
- Ensure `AA-ENet_proposed.pt` exists in project root
- Check file size (should be ~18 MB)
- Verify GPU/CPU match in code vs. machine

### CLIP Download Fails
- CLIP model auto-downloaded from HuggingFace on first run
- Requires internet connection
- Cached in `~/.cache/huggingface/` after first download
- In HF Spaces, this works automatically

### Report PDF Generation Fails
- Check temporary file permissions
- Ensure fpdf2 is installed
- Verify image base64 strings are valid

### Flask App Won't Start
- Check port 7860 is not in use
- Verify all imports resolve (run `python app.py` directly)
- Check logs for model loading errors

## Future Enhancements

### Potential Features
1. Batch classification (upload multiple images)
2. Confidence threshold tuning in UI
3. Export results as CSV/JSON
4. Model explainability dashboard (SHAP values)
5. Fine-tuning interface for custom datasets
6. API rate limiting & authentication
7. Multi-language support

### Performance
1. Quantized model variant (INT8) for faster inference
2. Model distillation (smaller model, similar accuracy)
3. Caching inference results (same image hash)
4. Async classification for parallel requests

### Monitoring
1. Sentry integration for error tracking
2. Prometheus metrics (inference time, error rate)
3. CloudWatch/ELK for centralized logging

## Git LFS Configuration

Large files are tracked via Git LFS:
```bash
# .gitattributes already configured for *.pt and *.pth
git lfs pull  # Download large files
```

Model files in `.gitattributes`:
- `*.pt` (AA-ENet weights)
- `*.pth` (legacy classifier)

## Deployment Checklist

- [ ] Model file (AA-ENet_proposed.pt) present and accessible
- [ ] All dependencies in requirements.txt and pinned
- [ ] Docker build succeeds without errors
- [ ] Flask app starts with `docker run`
- [ ] Health endpoint responds: `/api/health`
- [ ] Upload endpoint accepts image: `POST /api/classify`
- [ ] Report endpoint generates PDF: `POST /api/report`
- [ ] Frontend loads and renders correctly
- [ ] Theme toggle persists across page reloads
- [ ] Mango detection rejects non-mango images
- [ ] Grad-CAM visualization generates
- [ ] PDF downloads with correct filename
- [ ] Error messages are user-friendly
- [ ] Responsive design works on mobile
- [ ] No console errors in browser DevTools

## Support & Attribution

**Research Group**: AIUB R&D ICCA Research Group  
**Model**: AA-ENet (EfficientNet-B0 + CBAM + Transformer)  
**Dataset**: 3,500 Amropali mango images (500 per disease class)  
**Deployment**: Hugging Face Spaces  
**License**: MIT
