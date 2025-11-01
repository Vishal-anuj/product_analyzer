# Deploy to Hugging Face Space - Step by Step

Your Space is already created at: `iambatmanboom/product-analyzer-sentiment`

## Step 1: Clone the Space Repository

```powershell
# Clone the repo (use your access token as password when prompted)
git clone https://huggingface.co/spaces/iambatmanboom/product-analyzer-sentiment

cd product-analyzer-sentiment
```

**Note:** When prompted for password, use a Hugging Face access token with **write** permissions.
Generate one at: https://huggingface.co/settings/tokens

## Step 2: Copy Files to Space Directory

Copy these files from `hf_space_files/` to your cloned Space directory:

1. `app.py` → Copy to Space directory
2. `requirements.txt` → Copy to Space directory  
3. `Dockerfile` → Copy to Space directory
4. `README.md` → Copy to Space directory (optional, for Space description)

## Step 3: Commit and Push

```powershell
# Add all files
git add app.py requirements.txt Dockerfile README.md

# Commit
git commit -m "Add FastAPI sentiment analysis application"

# Push to deploy
git push
```

## Step 4: Wait for Deployment

- Go to: https://huggingface.co/spaces/iambatmanboom/product-analyzer-sentiment
- Check the "Logs" tab to see build progress
- Wait 2-5 minutes for deployment
- Once it shows "Running", your API is ready!

## Step 5: Test Your Space

Your Space will be available at:
```
https://iambatmanboom-product-analyzer-sentiment.hf.space
```

Test it:
```powershell
# Health check
curl https://iambatmanboom-product-analyzer-sentiment.hf.space/

# Test analysis endpoint
curl -X POST https://iambatmanboom-product-analyzer-sentiment.hf.space/analyze `
  -H "Content-Type: application/json" `
  -d '{\"reviews\": [\"Great product!\", \"Not worth the money.\"]}'
```

## Step 6: Update Backend Configuration

Once your Space is running, update `docker-compose.yml`:

```yaml
environment:
  - HF_API_BASE=https://iambatmanboom-product-analyzer-sentiment.hf.space
  - HF_MODEL=  # Leave empty for custom Space endpoint
```

Or update `backend/.env`:

```
HF_API_BASE=https://iambatmanboom-product-analyzer-sentiment.hf.space
HF_MODEL=
```

Then restart:
```powershell
docker-compose restart backend
```

## Troubleshooting

### Build Fails
- Check the "Logs" tab in your Space
- Ensure all files are in the root of the Space directory
- Verify `Dockerfile` and `requirements.txt` are correct

### Model Loading Takes Time
- First request may take 30-60 seconds (cold start)
- The model downloads on first use

### API Returns 404
- Verify Space status is "Running"
- Check that endpoint is `/analyze` (not `/api/analyze`)

## Files Summary

The Space needs these files:
- ✅ `app.py` - FastAPI application
- ✅ `requirements.txt` - Python dependencies
- ✅ `Dockerfile` - Docker configuration
- ✅ `README.md` - Space description (optional)

All files are ready in the `hf_space_files/` folder!

