# Quick Setup Guide: Deploy to Hugging Face Space

## Step 1: Create Your Space

1. Go to https://huggingface.co/spaces
2. Click **"Create new Space"**
3. Fill in:
   - **Space name**: `product-analyzer-sentiment` (or your choice)
   - **SDK**: Select **"Docker"**
   - **Visibility**: Public
4. Click **"Create Space"**

## Step 2: Upload Files

1. In your Space, go to the **"Files and versions"** tab
2. Click **"Add file"** → **"Upload files"**
3. Upload these files from the `hf_space_files/` folder:
   - `app.py`
   - `Dockerfile`
   - `README.md` (optional, but recommended)

## Step 3: Wait for Deployment

- The Space will automatically build (takes 2-5 minutes)
- Watch the **"Logs"** tab to see build progress
- Once it shows "Running", your API is ready!

## Step 4: Get Your Space URL

Your Space URL will be:
```
https://your-username-product-analyzer-sentiment.hf.space
```

## Step 5: Update Backend Configuration

Edit `docker-compose.yml`:

```yaml
environment:
  - HF_API_BASE=https://your-username-product-analyzer-sentiment.hf.space
  - HF_MODEL=  # Leave empty for custom Space endpoint
```

Or update `backend/.env`:

```
HF_API_BASE=https://your-username-product-analyzer-sentiment.hf.space
HF_MODEL=
```

## Step 6: Restart Backend

```bash
docker-compose restart backend
```

## Step 7: Test It!

```bash
curl "http://localhost:8000/analyze?product=test"
```

Check the logs:
```bash
docker-compose logs backend | grep "Hugging Face"
```

## Troubleshooting

### Space Build Fails
- Check the **Logs** tab in your Space
- Ensure `Dockerfile` and `app.py` are in the root of your Space

### API Returns 404
- Verify your Space URL is correct
- Check that the Space status is "Running"
- The endpoint should be: `https://your-space.hf.space/analyze`

### Model Loading Takes Time
- First request may take 30-60 seconds (cold start)
- Subsequent requests will be faster

## Optional: Custom Model

To use a different sentiment model, edit `hf_space_files/app.py`:

```python
model_name = "your-preferred-model-name"
```

Popular alternatives:
- `distilbert-base-uncased-finetuned-sst-2-english` (faster)
- `nlptown/bert-base-multilingual-uncased-sentiment` (multilingual)

