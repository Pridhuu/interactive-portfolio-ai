# How to Deploy to Render

Since we've added a `render.yaml` file and fixed `requirements.txt`, you have two options for deployment.

## Option 1: Using Blueprints (Recommended)
This uses the `render.yaml` file to automatically configure everything.

1.  **Push your code** to GitHub/GitLab.
2.  Go to your **Render Dashboard**.
3.  Click **New +** and select **Blueprint**.
4.  Connect your repository (e.g. `interactive-portfolio-ai`).
5.  Render will check for `render.yaml`.
6.  Click **New Service** (or the button to proceed).
7.  Done! Your app will deploy.

## Option 2: Manual Web Service (Fixing Existing Service)
If you already created a Web Service and want to fix it:

1.  **Push your code** to GitHub/GitLab.
2.  Go to your **Render Dashboard** and click on your failed service.
3.  Click on **Settings** in the left sidebar.
4.  Scroll down to **Build & Deploy**.
5.  **Build Command:** `pip install -r requirements.txt`
6.  **Start Command:** Enter this EXACTLY:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```
    (Do **not** copy the \`\`\`bash part, just the text inside)
7.  **Environment Variables:**
    - (Optional) Add `PYTHON_VERSION` with value `3.11.9`.
8.  **Important:** Scroll up to the top right of the logs/deployment page, click **Manual Deploy** -> **Clear Build Cache & Deploy**.
    - *Clearing the cache is critical to remove the old broken requirements file from the build cache.*

## Troubleshooting
- If the build still fails, check the **Logs** tab.
- Look for `ModuleNotFoundError` or similar.
- Ensure your `requirements.txt` is committed and pushed.
