import { useEffect, useState, useCallback } from 'react';
import { API } from '../api';

const ORIGIN = (API.defaults?.baseURL || 'http://127.0.0.1:8000/api').replace(/\/api\/?$/, '');

const TABS = [
  { key: 'all', label: 'All' },
  { key: 'interest', label: 'My sports' },
  { key: 'nearby', label: 'Nearby' },
  { key: 'connections', label: 'Connections' },
];
const BADGES = { interest: 'Your sport', nearby: 'Near you', connection: 'Connection' };

function authorName(p) {
  const a = p.author;
  if (a && typeof a === 'object') {
    const full = a.full_name || `${a.first_name || ''} ${a.last_name || ''}`.trim();
    return full || a.username || 'Member';
  }
  return p.author_name || p.author_username || p.username || 'Member';
}

function countOf(p, ...keys) {
  for (const k of keys) {
    const v = p[k];
    if (typeof v === 'number') return v;
    if (Array.isArray(v)) return v.length;
  }
  return 0;
}

export default function CommunityFeed() {
  const [source, setSource] = useState('all');
  const [posts, setPosts] = useState([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [fallback, setFallback] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async (src, pg) => {
    setLoading(true);
    setError('');
    try {
      const res = await API.get('/feed/', { params: { source: src, page: pg, limit: 10 } });
      const data = res.data;
      setPosts((prev) => (pg === 1 ? data.results : [...prev, ...data.results]));
      setHasNext(data.has_next);
      setFallback(data.fallback);
      setPage(pg);
    } catch (e) {
      const status = e.response?.status;
      setError(status === 401 ? 'Please log in again.' : `Could not load the feed${status ? ` (${status})` : ''}.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(source, 1);
  }, [source, load]);

  return (
    <section>
      <div className="mb-3">
        <h2 className="text-xl font-bold text-slate-900">Community feed</h2>
        <p className="text-sm text-slate-500">Matched to your sports, your area and your connections</p>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setSource(t.key)}
            className={
              'rounded-full px-4 py-1.5 text-sm font-semibold border ' +
              (source === t.key
                ? 'bg-orange-500 border-orange-500 text-white'
                : 'bg-white border-slate-200 text-slate-600 hover:border-orange-300')
            }
          >
            {t.label}
          </button>
        ))}
      </div>

      {fallback && source === 'all' && (
        <p className="mb-3 rounded-xl bg-orange-50 px-4 py-2 text-sm text-orange-700">
          Add your sport and PIN code in your profile to personalise this feed. Showing the latest posts for now.
        </p>
      )}

      {error && <p className="mb-3 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-700">{error}</p>}

      <div className="space-y-4">
        {posts.map((p) => {
          const name = authorName(p);
          const img = p.image ? (String(p.image).startsWith('http') ? p.image : ORIGIN + p.image) : null;
          return (
            <article key={p.id} className="rounded-2xl border border-slate-200 bg-white">
              <div className="flex items-center gap-3 p-5 pb-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 font-bold text-orange-600">
                  {name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div className="font-bold text-slate-900">{name}</div>
                  <div className="text-xs text-slate-400">
                    {p.post_type}
                    {p.sport ? ` · ${p.sport}` : ''} · {new Date(p.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <p className="whitespace-pre-line px-5 pb-3 text-slate-800">{p.content}</p>
              {img && <img src={img} alt="" className="w-full object-cover" />}

              {p.reasons && p.reasons.length > 0 && (
                <div className="flex flex-wrap gap-2 px-5 pb-3">
                  {p.reasons.map((r) => (
                    <span key={r} className="rounded-full bg-orange-50 px-2.5 py-0.5 text-xs font-semibold text-orange-600">
                      {BADGES[r] || r}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex gap-6 border-t border-slate-100 px-5 py-3 text-sm text-slate-500">
                <span>♡ {countOf(p, 'likes_count', 'like_count', 'likes')}</span>
                <span>💬 {countOf(p, 'comments_count', 'comment_count', 'comments')}</span>
              </div>
            </article>
          );
        })}
      </div>

      {!loading && !error && posts.length === 0 && (
        <p className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-slate-500">
          Nothing here yet. Follow people, add your sport, or switch to another tab.
        </p>
      )}

      {loading && <p className="py-4 text-center text-slate-400">Loading…</p>}

      {hasNext && !loading && (
        <div className="py-4 text-center">
          <button
            onClick={() => load(source, page + 1)}
            className="rounded-full border border-orange-500 px-6 py-2 font-semibold text-orange-600 hover:bg-orange-50"
          >
            Load more
          </button>
        </div>
      )}
    </section>
  );
}