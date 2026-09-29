# How to Publish `mango-disease-ai` on PyPI

Follow these steps **in order**. After completion, anyone in the world can run:
```bash
pip install mango-disease-ai
```

---

## Step 1 — Create Your PyPI Account

1. Go to **https://pypi.org/account/register/**
2. Fill in:
   - Username (e.g. `aiub-rd-icca` or your name)
   - Email address
   - Password
3. Check your email → click the **verification link**
4. Log in to confirm your account works

> ⚠️ Also create a TestPyPI account at **https://test.pypi.org/account/register/**  
> This lets you test publishing without affecting the real PyPI.

---

## Step 2 — Create an API Token (for uploading)

Instead of your password, PyPI uses API tokens for security.

1. Log in to https://pypi.org
2. Go to **Account Settings** → **API tokens**
3. Click **"Add API token"**
4. Give it a name: `mango-disease-ai-upload`
5. Scope: **"Entire account"** (for first publish; can restrict later)
6. Click **"Add token"**
7. **Copy the token immediately** — it starts with `pypi-` and is only shown once!

Save it somewhere safe (e.g. Notepad — you'll need it in Step 5).

---

## Step 3 — Install Build Tools

Open PowerShell and run:
```powershell
pip install build twine
```

---

## Step 4 — Build the Package

Navigate to your project folder and run:
```powershell
cd "e:\AIUB R&D ICCA\Updated Deploy\LastUpdatedmango"
python -m build
```

This creates a `dist/` folder with two files:
```
dist/
├── mango_disease_ai-0.1.0.tar.gz      ← source distribution
└── mango_disease_ai-0.1.0-py3-none-any.whl  ← wheel (faster install)
```

---

## Step 5 — Upload to TestPyPI (Dry Run)

First test on the test server (safe — doesn't affect real PyPI):
```powershell
python -m twine upload --repository testpypi dist/*
```

When prompted:
- **Username**: `__token__`  (literally the word `__token__`)
- **Password**: paste your API token (starts with `pypi-`)

Then verify it worked:
```bash
pip install --index-url https://test.pypi.org/simple/ mango-disease-ai
```

---

## Step 6 — Upload to Real PyPI

Once you've verified everything works on TestPyPI:
```powershell
python -m twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: paste your API token

That's it! Your package is now live at:
**https://pypi.org/project/mango-disease-ai/**

---

## Step 7 — Test the Installation

Open a **new terminal** (with a fresh Python environment) and run:
```bash
pip install mango-disease-ai
python -c "from mango_disease_ai import analyze; print('Package installed successfully!')"
```

---

## Releasing Future Updates

When you make improvements, update the version in `pyproject.toml`:
```toml
version = "0.1.1"  # or "0.2.0" for bigger changes
```

Then rebuild and re-upload:
```powershell
python -m build
python -m twine upload dist/*
```

---

## Version Numbering Guide

| Change Type | Example | When to Use |
|------------|---------|-------------|
| Bug fix | `0.1.0` → `0.1.1` | Small fix |
| New feature | `0.1.0` → `0.2.0` | New endpoint or function |
| Major change | `0.1.0` → `1.0.0` | Breaking API change |

---

## Troubleshooting

**`twine upload` fails with "File already exists"**  
→ You cannot re-upload the same version. Bump the version number.

**`pip install mango-disease-ai` not found after upload**  
→ Wait 1–2 minutes. PyPI needs time to index new packages.

**Model weights too large for PyPI (100 MB limit)**  
→ The `AA-ENet_proposed.pt` file is ~18 MB which is fine.  
→ If it were larger, we'd auto-download it from HuggingFace Hub.

---

## Summary Checklist

- [ ] Create PyPI account at https://pypi.org/account/register/
- [ ] Verify email
- [ ] Create API token in Account Settings
- [ ] Run `pip install build twine`
- [ ] Run `python -m build` → creates `dist/` folder
- [ ] Test on TestPyPI: `twine upload --repository testpypi dist/*`
- [ ] Publish to PyPI: `twine upload dist/*`
- [ ] Verify: `pip install mango-disease-ai`
