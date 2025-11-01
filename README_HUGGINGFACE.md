# Using Hugging Face for Model Inference

This project now uses Hugging Face Inference API instead of running Ollama locally.

## Setup Options

### Option 1: Use Public Hugging Face Models (Free, with rate limits)

1. **Get a Hugging Face API Token (Optional but Recommended)**
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with "Read" permissions
   - Add it to `backend/.env`:
     ```
     HF_API_TOKEN=your_token_here
     ```

2. **Configure Model** (in `backend/.env` or docker-compose.yml):
   ```
   HF_API_BASE=https://api-inference.huggingface.co/models
   HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
   ```

3. **Alternative Models** (faster, smaller):
   - For sentiment analysis: `HF_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest`
   - For text generation: `HF_MODEL=microsoft/Phi-3-mini-4k-instruct`
   - For balanced: `HF_MODEL=meta-llama/Llama-3.1-8B-Instruct`

### Option 2: Use Your Own Hugging Face Space

If you want to host your own model on a Hugging Face Space:

1. **Create a Space on Hugging Face:**
   - Go to https://huggingface.co/spaces
   - Create a new Space
   - Choose a model that supports API inference
   - Deploy your model

2. **Update Configuration:**
   ```
   HF_API_BASE=https://your-username-your-space.hf.space
   HF_MODEL=  # Leave empty or use your custom endpoint
   ```

   Or if using a specific model in your space:
   ```
   HF_API_BASE=https://api-inference.huggingface.co/models
   HF_MODEL=your-username/your-model-name
   ```

### Option 3: Use Hugging Face Inference Endpoints (Paid, but faster)

1. **Create an Inference Endpoint:**
   - Go to https://huggingface.co/inference-endpoints
   - Create a new endpoint
   - Copy the endpoint URL

2. **Update Configuration:**
   ```
   HF_API_BASE=https://your-endpoint-id.region.inference.endpoints.huggingface.cloud
   HF_MODEL=  # Leave empty if using custom endpoint
   ```

## Environment Variables

Add to `backend/.env`:

```env
# Hugging Face Configuration
HF_API_BASE=https://api-inference.huggingface.co/models
HF_MODEL=meta-llama/Llama-3.1-8B-Instruct
HF_API_TOKEN=your_token_here  # Optional but recommended
```

## Rate Limits

- **Free tier**: Limited requests per day
- **With API token**: Higher rate limits
- **Inference Endpoints**: No rate limits (paid)

## Testing

After starting your services:

```bash
docker-compose up -d
docker-compose logs -f backend
```

Make a search request and check the logs for:
- `Querying Hugging Face API at ...`
- `Hugging Face response received: ...`

## Troubleshooting

1. **503 Model Loading Error**: The model is loading. Wait 10-30 seconds and try again.
2. **Rate Limit Errors**: Add your HF_API_TOKEN for higher limits
3. **Timeout Errors**: Model might be slow. Consider using a smaller model.

## Recommended Models for Sentiment Analysis

- `cardiffnlp/twitter-roberta-base-sentiment-latest` - Fast, specialized for sentiment
- `nlptown/bert-base-multilingual-uncased-sentiment` - Multilingual support
- `meta-llama/Llama-3.1-8B-Instruct` - Best quality but slower

