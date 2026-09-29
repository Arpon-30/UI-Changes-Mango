# Deploy AmropaliNet live for free - Hugging Face Spaces

**Why Hugging Face Spaces?** It is free, gives a public `https://` link (the phone camera
needs https), and its free CPU machine has **16 GB RAM** - enough for PyTorch + AA-ENet + CLIP.
Most other free hosts (Render, Vercel, Netlify, PythonAnywhere) give 512 MB RAM or cannot run
PyTorch, so the app would crash there.

The project is already prepared: `Dockerfile` (port 7860) and the settings block at the top
of `README.md`.

## Step 1 - Create a Hugging Face account
Sign up at https://huggingface.co/join (free) and verify your email.

## Step 2 - Create a Space
1. Go to https://huggingface.co/new-space
2. **Space name:** `AmropaliNet`
3. **License:** MIT
4. **SDK:** choose **Docker** → template **Blank**
5. **Hardware:** **CPU basic - 2 vCPU · 16 GB · FREE**
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
