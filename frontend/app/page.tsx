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

  return (
    <main className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Product Review Analyzer</h1>
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
            <h2 className="font-medium mb-3">Sentiment</h2>
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
        </div>
      )}
    </main>
  );
}


