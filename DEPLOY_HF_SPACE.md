# Deploying Model to Hugging Face Space

Follow these steps to deploy your model to Hugging Face Spaces:

## Step 1: Create a Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Space name**: `product-analyzer-sentiment` (or your preferred name)
   - **SDK**: Choose "Docker" (most flexible) or "Gradio" (easier UI)
   - **Visibility**: Public or Private
4. Click "Create Space"

## Step 2: Set Up Your Space

### If using Docker SDK:

1. In your Space, go to "Files and versions" tab
2. Upload or create these files:

**`Dockerfile`**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    transformers \
    torch \
    accelerate \
    sentencepiece \
    fastapi \
    uvicorn \
    pydantic

# Copy model loading script
COPY app.py /app/app.py

EXPOSE 7860

CMD ["python", "app.py"]
```

**`app.py`**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load a sentiment analysis model
# You can change this to any model you prefer
model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sentiment_pipeline = pipeline("sentiment-analysis", model=model_name, device=-1)

# For text generation (pros/cons analysis), use a smaller model
# Uncomment if you want text generation too:
# from transformers import AutoTokenizer, AutoModelForCausalLM
# text_model = "microsoft/Phi-3-mini-4k-instruct"
# tokenizer = AutoTokenizer.from_pretrained(text_model)
# text_generator = AutoModelForCausalLM.from_pretrained(text_model)

class AnalyzeRequest(BaseModel):
    reviews: list[str]

class SentimentResponse(BaseModel):
    sentiment: dict
    pros: list[str]
    cons: list[str]
    score: float

@app.get("/")
def read_root():
    return {"status": "ready", "model": model_name}

@app.post("/analyze", response_model=SentimentResponse)
async def analyze_reviews(request: AnalyzeRequest):
    """Analyze reviews and return sentiment + pros/cons"""
    reviews_text = "\n".join(request.reviews[:50])
    
    # Get sentiment
    results = sentiment_pipeline(reviews_text[:512])  # Limit input length
    
    # Calculate percentages
    positive = sum(1 for r in results if r['label'] in ['POSITIVE', 'LABEL_2', 'LABEL_1'])
    negative = sum(1 for r in results if r['label'] in ['NEGATIVE', 'LABEL_0'])
    neutral = len(results) - positive - negative
    
    total = len(results) if results else 1
    pos_pct = int((positive / total) * 100)
    neg_pct = int((negative / total) * 100)
    neu_pct = 100 - pos_pct - neg_pct
    
    # Extract pros/cons (simple keyword-based for now)
    pros = []
    cons = []
    for review in request.reviews[:10]:
        review_lower = review.lower()
        if any(kw in review_lower for kw in ["good", "great", "excellent", "love", "recommend"]):
            pros.append("Positive feedback from reviews")
            break
        if any(kw in review_lower for kw in ["bad", "terrible", "poor", "disappointed"]):
            cons.append("Some concerns mentioned in reviews")
            break
    
    # Calculate score
    score = 5.0 + (pos_pct - neg_pct) / 20.0
    score = max(1.0, min(10.0, score))
    
    return SentimentResponse(
        sentiment={"positive": pos_pct, "neutral": neu_pct, "negative": neg_pct},
        pros=pros if pros else ["Positive aspects identified"],
        cons=cons if cons else ["No major concerns"],
        score=round(score, 1)
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

3. Add a `requirements.txt` (optional, Docker handles it differently):
```
transformers
torch
accelerate
sentencepiece
fastapi
uvicorn
pydantic
```

### If using Gradio SDK:

Create `app.py`:
```python
import gradio as gr
from transformers import pipeline

# Load model
model = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")

def analyze(reviews):
    results = model(reviews)
    return str(results)

iface = gr.Interface(
    fn=analyze,
    inputs=gr.Textbox(lines=5, placeholder="Enter reviews..."),
    outputs="text"
)

iface.launch()
```

## Step 3: Deploy Your Space

1. Push your files to the Space (or use the web editor)
2. Wait for the Space to build (usually 2-5 minutes)
3. Once running, note your Space URL: `https://your-username-product-analyzer-sentiment.hf.space`

## Step 4: Configure Backend to Use Your Space

Update your `docker-compose.yml` or `backend/.env`:

```yaml
# In docker-compose.yml, update the HF_API_BASE:
environment:
  - HF_API_BASE=https://your-username-product-analyzer-sentiment.hf.space
  - HF_MODEL=  # Leave empty for custom endpoint
```

Or in `backend/.env`:
```
HF_API_BASE=https://your-username-product-analyzer-sentiment.hf.space
HF_MODEL=
```

## Step 5: Update Backend Code

You may need to update `backend/services/ollama_client.py` to handle custom endpoints differently.

## Quick Alternative: Use Pre-built Sentiment Model

Instead of deploying, you can use a working public model:

1. Update `docker-compose.yml`:
```yaml
HF_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
```

2. The backend will automatically adapt to use sentiment analysis models.

