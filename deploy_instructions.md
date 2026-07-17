# Deploy Sleep Investigation Agent to Streamlit Cloud

## Quick Deployment (Recommended)

Streamlit Cloud is the easiest way to deploy this app as a website. It handles all dependencies automatically.

### Steps:

1. **Push to GitHub**
   ```bash
   cd C:\Users\navee\CascadeProjects\sleep-investigation-agent
   git init
   git add .
   git commit -m "Initial commit"
   # Create a new repository on GitHub first
   git remote add origin https://github.com/YOUR_USERNAME/sleep-investigation-agent.git
   git push -u origin main
   ```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "Deploy now"
   - Connect your GitHub account
   - Select your repository
   - Click "Deploy"

3. **Add OpenAI API Key (Optional)**
   - In Streamlit Cloud dashboard, go to your app settings
   - Add "OPENAI_API_KEY" in secrets
   - Enter your API key

4. **Access Your App**
   - Streamlit Cloud will provide a URL like: https://your-app-name.streamlit.app
   - Share this URL with your team

## Alternative: Local Web Server

If you prefer to run locally without installing dependencies, you can use a simpler version.

## Alternative: Docker Deployment

Create a Dockerfile for containerized deployment:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t sleep-agent .
docker run -p 8501:8501 sleep-agent
```

## Access from Anywhere

Once deployed to Streamlit Cloud:
- Access from any browser
- No installation needed for users
- Share URL with QA team
- Free tier available for personal use
