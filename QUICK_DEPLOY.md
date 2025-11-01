# Quick Deploy to Your Hugging Face Space

Your Space is ready! Here's how to deploy:

## 1. Clone Your Space

```powershell
git clone https://huggingface.co/spaces/iambatmanboom/product-analyzer-sentiment
cd product-analyzer-sentiment
```

**When prompted for password:** Use your Hugging Face access token (with write permissions)  
Get token at: https://huggingface.co/settings/tokens

## 2. Copy Files

Copy these files from `hf_space_files/` folder to your cloned Space directory:

```powershell
# From product_analyzer root directory
Copy-Item hf_space_files\app.py product-analyzer-sentiment\
Copy-Item hf_space_files\requirements.txt product-analyzer-sentiment\
Copy-Item hf_space_files\Dockerfile product-analyzer-sentiment\
Copy-Item hf_space_files\README.md product-analyzer-sentiment\
```

Or manually:
- Copy `hf_space_files/app.py` → `product-analyzer-sentiment/app.py`
- Copy `hf_space_files/requirements.txt` → `product-analyzer-sentiment/requirements.txt`
- Copy `hf_space_files/Dockerfile` → `product-analyzer-sentiment/Dockerfile`
- Copy `hf_space_files/README.md` → `product-analyzer-sentiment/README.md`

## 3. Commit and Push

```powershell
cd product-analyzer-sentiment

git add app.py requirements.txt Dockerfile README.md
git commit -m "Add FastAPI sentiment analysis application"
git push
```

## 4. Wait for Deployment

- Go to: https://huggingface.co/spaces/iambatmanboom/product-analyzer-sentiment
- Check the "Logs" tab
- Wait 2-5 minutes
- When status shows "Running", it's ready!

## 5. Test Your Space

Your Space URL: `https://iambatmanboom-product-analyzer-sentiment.hf.space`

Test it:
```powershell
# Health check
curl https://iambatmanboom-product-analyzer-sentiment.hf.space/

# Test analyze endpoint
curl -X POST https://iambatmanboom-product-analyzer-sentiment.hf.space/analyze `
  -H "Content-Type: application/json" `
  -d '{\"reviews\": [\"Great product!\", \"Not worth it.\"]}'
```

## 6. Update Backend

Once your Space is running, update `docker-compose.yml`:

```yaml
environment:
  - HF_API_BASE=https://iambatmanboom-product-analyzer-sentiment.hf.space
  - HF_MODEL=
```

Then restart:
```powershell
docker-compose restart backend
```

## Done! 🎉

Your backend will now use your deployed Hugging Face Space for sentiment analysis!

