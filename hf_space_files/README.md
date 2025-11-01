---
title: Product Analyzer Sentiment API
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Product Analyzer Sentiment API

FastAPI endpoint for analyzing product review sentiment.

## Endpoints

- `GET /` - Health check
- `POST /analyze` - Analyze reviews

### Analyze Request
```json
{
  "reviews": [
    "Great product!",
    "Not worth the money."
  ]
}
```

### Analyze Response
```json
{
  "sentiment": {
    "positive": 50,
    "neutral": 0,
    "negative": 50
  },
  "pros": ["Quality", "Performance"],
  "cons": ["Pricing Concerns"],
  "score": 5.0,
  "best_platform": null
}
```

