# Deploy AmropaliNet live

> **Important (checked September 2026):** since July 2026, Hugging Face **no longer lets free
> accounts create Docker Spaces**. You need the **PRO plan ($9/month)**. Free accounts only get
> static Spaces (no server, so the AI cannot run) or ZeroGPU Gradio Spaces.

## Which option?

| Option | Cost | Card? | Online 24/7? |
|---|---|---|---|
| A. Your laptop + Cloudflare Tunnel (below) | Free | No | Only while the laptop runs |
| B. GitHub Codespaces | Free (monthly hours) | No | Only while running |
| C. Oracle Cloud Always Free VM (24 GB RAM) | Free | Yes (verification) | Yes |
| D. Google Cloud Run | Free within limits | Yes | Yes (cold start) |
| E. Hugging Face Spaces PRO (steps below) | $9 / month | Yes | Yes |

Render / Vercel / Netlify / Koyeb free plans do not work: about 512 MB RAM, the AI needs about 2 GB.

**Streamlit Community Cloud** (free) can only run the old `streamlit_app.py`, not the new
website (HTML + FastAPI). Its free apps get about 1 GB RAM, and PyTorch + AA-ENet + the CLIP
mango checker need more, so the app is likely to stop with "over its resource limits".

## Option A - free public link from your laptop (best for demos)

1. Start the app: `python run.py` (it runs on http://localhost:8000).
2. Download `cloudflared` for Windows: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
3. In a second terminal:
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
4. It prints a link like `https://something-random.trycloudflare.com` - open it on any phone.
   The camera works because the link is https. The link changes each time you start it and
   works only while both terminals are open.

## Option E - Hugging Face Spaces (PRO, $9/month)

The project is already prepared for this: `Dockerfile` (port 7860) and the settings block at the
top of `README.md`. With PRO, choose **CPU basic** hardware (2 vCPU, 16 GB RAM).

## Step 1 - Create a Hugging Face account
Sign up at https://huggingface.co/join, verify your email, and subscribe to **PRO** at https://huggingface.co/pricing.

## Step 2 - Create a Space
1. Go to https://huggingface.co/new-space
2. **Space name:** `AmropaliNet`
3. **License:** MIT
4. **SDK:** choose **Docker** → template **Blank**
5. **Hardware:** **CPU basic - 2 vCPU · 16 GB** (needs a PRO account for Docker Spaces)
6. **Visibility:** Public
7. Click **Create Space**

## Step 3 - Upload the project (easiest: in the browser)
1. In your new Space, open the **Files** tab → **Add file** → **Upload files**.
2. From the project folder, drag in these files and folders:

   | Upload | Why |
   |---|---|
   | `Dockerfile` | How to build the app |
   | `README.md` | Tells Hugging Face: Docker, port 7860 (replace the default README) |
   | `api/` | Website server |
   | `mango_disease_ai/` | AI library + the 18 MB model + Bangla fonts |
   | `templates/` | Web page |
   | `static/` | Design, scripts, images |

   You do **not** need the notebook, `docs/`, or the old Streamlit files.
3. Write a commit message like `First deploy` and click **Commit changes to main**.

Large files (the 18 MB model, fonts) are handled automatically by the web upload.

## Step 4 - Wait for the build
- The **Logs** tab shows the build. The first build takes about **10-15 minutes**
  (it installs PyTorch and downloads the mango checker once).
- When it says **Running**, your site is live at:
  `https://huggingface.co/spaces/<your-username>/AmropaliNet`
  and the direct link (best for phones and QR codes):
  `https://<your-username>-amropalinet.hf.space`

## Step 5 - Test
1. Open the link on your phone → **Scan with camera** → photograph a mango.
2. Try **বাংলা** and a Bangla PDF.
3. Developers / judges: `https://<your-username>-amropalinet.hf.space/docs`

## Updating later
Upload the changed files again (Files → Add file → Upload files). The Space rebuilds by itself.

## Good to know
- A free Space **sleeps after about 48 hours without visitors**. The next visitor wakes it up;
  that takes 1-2 minutes. Open the link yourself a few minutes before a demo or judging.
- Free CPU: one scan takes a few seconds.
- If the build fails, the **Logs** tab shows the error - copy it and ask for help.

## Using git instead of the browser (optional)
```bash
git clone https://huggingface.co/spaces/<your-username>/AmropaliNet
# copy Dockerfile, README.md, api/, mango_disease_ai/, templates/, static/ into it
cd AmropaliNet
git lfs install
git lfs track "*.pt" "*.ttf"
git add .gitattributes .
git commit -m "Deploy AmropaliNet"
git push      # username: your HF name, password: an HF access token (Write)
```
Hugging Face requires Git LFS for files over 10 MB, so the `git lfs track` line is needed for the model.
