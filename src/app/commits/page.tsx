'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getCommits, getGitHubStatus, Commit, GitHubStatus } from '@/lib/api';

export default function CommitsPage() {
  const [commits, setCommits] = useState<Commit[]>([]);
  const [status, setStatus] = useState<GitHubStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [jiraFilter, setJiraFilter] = useState('');
  const pageSize = 20;

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [commitsResponse, statusResponse] = await Promise.all([
          getCommits({
            page,
            page_size: pageSize,
            jira_key: jiraFilter || undefined,
          }),
          getGitHubStatus().catch(() => null)
        ]);
        setCommits(commitsResponse.data.commits);
        setTotal(commitsResponse.data.total);
        if (statusResponse) {
          setStatus(statusResponse.data);
        }
      } catch (err) {
        setError('Failed to load commits');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [page, jiraFilter]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <Link href="/" className="text-blue-600 hover:text-blue-800 mb-2 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-4xl font-bold text-gray-900">GitHub Commits</h1>
          <p className="text-gray-600 mt-2">
            Commits linked to cloud migration bugs
          </p>
        </div>

        {/* Stats Cards */}
        {status && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Total Commits</div>
              <div className="text-2xl font-bold text-gray-900">{status.statistics.total_commits}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">With Jira Keys</div>
              <div className="text-2xl font-bold text-blue-600">{status.statistics.commits_with_jira_keys}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Bug Links</div>
              <div className="text-2xl font-bold text-green-600">{status.statistics.total_links}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm text-gray-500">Bugs with Commits</div>
              <div className="text-2xl font-bold text-purple-600">{status.statistics.bugs_with_commits}</div>
            </div>
          </div>
        )}

        {/* Filter */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="max-w-md">
            <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Jira Key</label>
            <input
              type="text"
              placeholder="e.g., MIG-1234"
              value={jiraFilter}
              onChange={(e) => { setJiraFilter(e.target.value.toUpperCase()); setPage(1); }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Commits List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">Loading commits...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">{error}</div>
          ) : commits.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              {jiraFilter ? `No commits found for ${jiraFilter}` : 'No commits found. Run GitHub sync to fetch commits.'}
            </div>
          ) : (
            <>
              <div className="divide-y divide-gray-200">
                {commits.map((commit) => (
                  <div key={commit.sha} className="p-4 hover:bg-gray-50">
                    <div className="flex items-start gap-4">
                      <a
                        href={commit.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 font-mono text-sm shrink-0"
                      >
                        {commit.short_sha}
                      </a>
                      <div className="flex-1 min-w-0">
                        <p className="text-gray-900 font-medium">{commit.message_headline}</p>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <span className="text-gray-500 text-sm">{commit.author_name}</span>
                          {commit.authored_at && (
                            <>
                              <span className="text-gray-300">·</span>
                              <span className="text-gray-500 text-sm">
                                {new Date(commit.authored_at).toLocaleDateString('en-US', {
                                  year: 'numeric',
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit'
                                })}
                              </span>
                            </>
                          )}
                        </div>
                        {commit.jira_keys.length > 0 && (
                          <div className="flex gap-2 mt-2 flex-wrap">
                            {commit.jira_keys.map((key) => (
                              <a
                                key={key}
                                href={`https://jira.atlassian.com/browse/${key}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 font-medium"
                              >
                                {key}
                              </a>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              <div className="px-6 py-4 border-t flex items-center justify-between bg-gray-50">
                <p className="text-sm text-gray-700">
                  Page {page} of {totalPages} ({total} total commits)
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-white disabled:hover:bg-transparent"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 hover:bg-white disabled:hover:bg-transparent"
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
