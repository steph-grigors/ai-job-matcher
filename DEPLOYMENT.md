# AI Job Matcher - Deployment Guide

## 🚀 Deploying to Streamlit Community Cloud

### Prerequisites
- GitHub account
- Code pushed to GitHub repository: `ai-job-matcher`
- API keys ready:
  - OpenAI API key
  - Adzuna App ID & API Key

---

## 📋 Step-by-Step Deployment

### Step 1: Push Code to GitHub

Make sure all files are committed and pushed:

```bash
# Add new files
git add .streamlit/config.toml
git add packages.txt
git add .gitignore

# Commit
git commit -m "Prepare for Streamlit Cloud deployment"

# Push to main branch
git push origin main
```

### Step 2: Create `.gitkeep` Files

Ensure empty directories are tracked:

```bash
touch data/resumes/.gitkeep
touch data/cache/.gitkeep
touch data/vector_store/.gitkeep

git add data/*/.gitkeep
git commit -m "Add .gitkeep files for empty directories"
git push
```

### Step 3: Sign Up for Streamlit Community Cloud

1. Go to https://share.streamlit.io/
2. Click **"Sign up"** or **"Continue with GitHub"**
3. Authorize Streamlit to access your GitHub account

### Step 4: Deploy Your App

1. Click **"New app"** button
2. Fill in the deployment form:
   - **Repository:** `your-username/ai-job-matcher`
   - **Branch:** `main`
   - **Main file path:** `app/main.py`
3. Click **"Advanced settings"** (IMPORTANT!)

### Step 5: Configure Secrets (API Keys)

In the Advanced settings, under **"Secrets"**, paste this TOML format:

```toml
# LLM API Keys
OPENAI_API_KEY = "sk-your-openai-key-here"

# Adzuna API
ADZUNA_APP_ID = "your-adzuna-app-id"
ADZUNA_API_KEY = "your-adzuna-api-key"

# Configuration
ADZUNA_COUNTRY = "be"  # or your preferred default
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"
ENABLE_CACHE = "false"  # Redis not available on Streamlit Cloud free tier
```

**⚠️ IMPORTANT:**
- Replace with your actual API keys
- Never commit secrets to GitHub!
- Set `ENABLE_CACHE = "false"` (no Redis on Streamlit Cloud)

### Step 6: Deploy!

1. Click **"Deploy!"**
2. Wait 2-5 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## 🔧 Post-Deployment Configuration

### Update `app/config.py` for Cloud Compatibility

The app should automatically read from Streamlit secrets, but verify the config reads from both `.env` and `st.secrets`:

```python
# In config.py, Pydantic Settings automatically reads from environment variables
# Streamlit Cloud injects secrets as environment variables, so it should work!
```

### Disable Redis Caching

Since Streamlit Cloud free tier doesn't support Redis, make sure caching is disabled:

In `.env.example` and deployment secrets, set:
```
ENABLE_CACHE=false
```

The app will work without caching, just slightly slower on repeated searches.

---

## 📊 Monitoring Your App

### View Logs
1. Go to your app on Streamlit Cloud
2. Click **"Manage app"**
3. Click **"Logs"** to see real-time logs

### Check Usage
- **Free tier limits:**
  - Unlimited public apps
  - 1 GB RAM per app
  - Community support

### Update Your App
Simply push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```

Streamlit Cloud automatically redeploys on push!

---

## 🐛 Troubleshooting

### App Won't Start
- Check logs for errors
- Verify all API keys are set correctly
- Ensure `requirements.txt` is complete

### Import Errors
- Make sure `app/__init__.py` exists
- Check all dependencies are in `requirements.txt`

### Redis Connection Errors
- Set `ENABLE_CACHE=false` in secrets
- The app should gracefully degrade without Redis

### File Upload Issues
- Streamlit Cloud has ephemeral storage
- Uploaded files are deleted after session ends (this is expected)

### API Rate Limits
- Monitor your OpenAI usage
- Monitor your Adzuna quota (1000 calls/month free)

---

## 🔒 Security Best Practices

### Never Commit Secrets
```bash
# Always check before committing
git status

# If you accidentally committed secrets:
git reset HEAD~1
git push --force
```

### Rotate API Keys
If you accidentally expose keys:
1. Immediately revoke/regenerate on provider websites
2. Update secrets in Streamlit Cloud
3. Redeploy app

### Make App Private (Optional)
In Streamlit Cloud:
1. Go to app settings
2. Under "Sharing", select **"Private"**
3. Invite specific users with email

---

## 💰 Cost Estimation

### Streamlit Cloud
- **Free tier:** $0/month
- Unlimited public apps

### API Costs (Pay-as-you-go)
- **OpenAI GPT-4o-mini:**
  - Resume parsing: ~$0.002 per resume
  - Job matching (10 jobs): ~$0.02 per search
  - Typical usage: $5-20/month for moderate use

- **Adzuna:**
  - Free tier: 1000 calls/month
  - Each job search = 1 call
  - Upgrade: $50/month for 10,000 calls

### Total Estimated Cost
- **Minimal usage:** $0/month (Streamlit) + $5/month (OpenAI) = **$5/month**
- **Moderate usage:** $0 + $20 = **$20/month**
- **Heavy usage:** $0 + $50 (OpenAI) + $50 (Adzuna) = **$100/month**

---

## 🎉 Your App is Live!

Share your app URL:
```
https://your-app-name.streamlit.app
```

Add it to your:
- ✅ Portfolio website
- ✅ LinkedIn projects
- ✅ Resume
- ✅ GitHub README

---

## 📚 Additional Resources

- **Streamlit Docs:** https://docs.streamlit.io/
- **Deployment Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum:** https://discuss.streamlit.io/

---

*Happy Deploying! 🚀*
