'use client';

import React, { useState } from 'react';
import axios from 'axios';

type PriceRow = { platform: string; price?: number | null; currency?: string; url?: string | null };

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

  async function onSearch(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await axios.get(`${apiBase}/analyze`, { params: { product: query } });
      setResult(res.data);
    } catch (err: any) {
      setError(err?.message || 'Failed to analyze');
    } finally {
      setLoading(false);
    }
  }

  const prices: PriceRow[] = result?.product?.prices || [];
  const sentiment = result?.analysis?.sentiment;
  const platformComparison = result?.platform_comparison;

  return (
    <main className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Product Comparison & Review Analyzer</h1>
      <p className="text-gray-600 text-sm">Compare products across Amazon and Flipkart with sentiment analysis</p>
      <form onSubmit={onSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search product (e.g., iPhone 15)"
          className="flex-1 border rounded-md px-3 py-2"
        />
        <button
          type="submit"
          className="px-4 py-2 rounded-md bg-blue-600 text-white disabled:opacity-60"
          disabled={!query || loading}
        >
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>

      {error && <div className="text-red-600">{error}</div>}

      {result && (
        <div className="space-y-6">
          <section className="p-4 bg-white rounded-md shadow">
            <h2 className="font-medium mb-2">Product Summary</h2>
            <div className="text-sm text-gray-700">{result.product?.name}</div>
          </section>

          <section className="p-4 bg-white rounded-md shadow">
            <h2 className="font-medium mb-3">Prices</h2>
            <div className="overflow-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left border-b">
                    <th className="py-2">Platform</th>
                    <th className="py-2">Price</th>
                    <th className="py-2">Link</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.map((p: PriceRow, idx: number) => (
                    <tr key={idx} className="border-b">
                      <td className="py-2">{p.platform}</td>
                      <td className="py-2">
                        {p.price != null ? `${p.currency || 'INR'} ${p.price}` : '—'}
                      </td>
                      <td className="py-2">{p.url ? <a className="text-blue-600 underline" href={p.url} target="_blank">Open</a> : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="p-4 bg-white rounded-md shadow">
            <h2 className="font-medium mb-3">Overall Sentiment</h2>
            {sentiment ? (
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="p-3 bg-green-50 rounded">Positive: {sentiment.positive}%</div>
                <div className="p-3 bg-gray-50 rounded">Neutral: {sentiment.neutral}%</div>
                <div className="p-3 bg-red-50 rounded">Negative: {sentiment.negative}%</div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No sentiment available</div>
            )}
          </section>

          {platformComparison && platformComparison.comparison && Object.keys(platformComparison.comparison).length > 0 && (
            <section className="p-4 bg-white rounded-md shadow">
              <h2 className="font-medium mb-3">Platform Comparison</h2>
              {platformComparison.best_platform && (
                <div className="mb-4 p-3 bg-blue-50 rounded text-sm">
                  <strong>Best Platform:</strong> {platformComparison.best_platform} 
                  {platformComparison.comparison[platformComparison.best_platform]?.average_rating && (
                    <span className="ml-2">
                      (Avg Rating: {platformComparison.comparison[platformComparison.best_platform].average_rating.toFixed(1)}/5.0)
                    </span>
                  )}
                </div>
              )}
              <div className="space-y-4">
                {Object.entries(platformComparison.comparison).map(([platform, data]: [string, any]) => (
                  <div key={platform} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-3">
                      <h3 className="font-medium text-lg">{platform}</h3>
                      {data.average_rating && (
                        <div className="text-sm text-gray-600">
                          Avg Rating: <span className="font-semibold">{data.average_rating.toFixed(1)}/5.0</span>
                        </div>
                      )}
                      {data.review_count && (
                        <div className="text-sm text-gray-500">
                          {data.review_count} review{data.review_count !== 1 ? 's' : ''}
                        </div>
                      )}
                    </div>
                    {data.sentiment && (
                      <div className="grid grid-cols-3 gap-3 text-sm mb-2">
                        <div className="p-2 bg-green-50 rounded text-center">
                          <div className="text-xs text-gray-600 mb-1">Positive</div>
                          <div className="font-semibold text-green-700">{data.sentiment.positive}%</div>
                        </div>
                        <div className="p-2 bg-gray-50 rounded text-center">
                          <div className="text-xs text-gray-600 mb-1">Neutral</div>
                          <div className="font-semibold text-gray-700">{data.sentiment.neutral}%</div>
                        </div>
                        <div className="p-2 bg-red-50 rounded text-center">
                          <div className="text-xs text-gray-600 mb-1">Negative</div>
                          <div className="font-semibold text-red-700">{data.sentiment.negative}%</div>
                        </div>
                      </div>
                    )}
                    {data.overall_sentiment && (
                      <div className="mt-2">
                        <span className="text-xs text-gray-500">Overall: </span>
                        <span className={`text-sm font-medium ${
                          data.overall_sentiment === 'positive' ? 'text-green-600' :
                          data.overall_sentiment === 'negative' ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {data.overall_sentiment.charAt(0).toUpperCase() + data.overall_sentiment.slice(1)}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          <section className="p-4 bg-white rounded-md shadow grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <h3 className="font-medium mb-2">Pros</h3>
              <ul className="list-disc list-inside space-y-1">
                {(result?.analysis?.pros || []).map((x: string, i: number) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-medium mb-2">Cons</h3>
              <ul className="list-disc list-inside space-y-1">
                {(result?.analysis?.cons || []).map((x: string, i: number) => (
                  <li key={i}>{x}</li>
                ))}
              </ul>
            </div>
          </section>

          {result?.product?.reviews && result.product.reviews.length > 0 && (
            <section className="p-4 bg-white rounded-md shadow">
              <h2 className="font-medium mb-3">Reviews by Platform</h2>
              <div className="space-y-4">
                {Object.entries(
                  result.product.reviews.reduce((acc: any, review: any) => {
                    if (!acc[review.platform]) acc[review.platform] = [];
                    acc[review.platform].push(review);
                    return acc;
                  }, {} as Record<string, any[]>)
                ).map(([platform, reviews]: [string, any[]]) => (
                  <div key={platform} className="border-l-4 border-blue-500 pl-4">
                    <h3 className="font-medium mb-2 text-lg">{platform}</h3>
                    <div className="space-y-3">
                      {reviews.map((review: any, idx: number) => (
                        <div key={idx} className="bg-gray-50 rounded p-3">
                          <div className="flex justify-between items-start mb-1">
                            {review.title && (
                              <div className="font-medium text-sm">{review.title}</div>
                            )}
                            {review.rating && (
                              <div className="text-xs text-gray-600">
                                ⭐ {review.rating}/5.0
                              </div>
                            )}
                          </div>
                          <div className="text-sm text-gray-700">{review.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </main>
  );
}


