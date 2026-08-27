import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import KnowledgeGraph from '../components/Graph/KnowledgeGraph';
import { HiArrowLeft, HiArrowPath, HiFunnel, HiMagnifyingGlass } from 'react-icons/hi2';

const GraphView = () => {
  const navigate = useNavigate();
  const [startNode, setStartNode] = useState('');
  const [maxDepth, setMaxDepth] = useState(2);
  const [jurisdiction, setJurisdiction] = useState('All');
  const [showFilters, setShowFilters] = useState(false);

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-stone-50 dark:bg-primary-950">
      {/* Header */}
      <div className="bg-white dark:bg-primary-900 border-b border-stone-200 dark:border-primary-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/')}
                className="p-2 rounded-lg hover:bg-stone-100 dark:hover:bg-primary-800 transition-colors"
              >
                <HiArrowLeft className="w-5 h-5 text-stone-600 dark:text-stone-400" />
              </button>
              <div>
                <h1 className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                  Legal Knowledge Graph
                </h1>
                <p className="text-sm text-stone-600 dark:text-stone-400">
                  Interactive visualization of legal relationships
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-primary-800 rounded-lg hover:bg-stone-200 dark:hover:bg-primary-700 transition-colors"
              >
                 <HiFunnel className="w-4 h-4" />
                Filters
              </button>
              <button
                onClick={handleRefresh}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-stone-700 dark:text-stone-300 bg-stone-100 dark:bg-primary-800 rounded-lg hover:bg-stone-200 dark:hover:bg-primary-700 transition-colors"
              >
                 <HiArrowPath className="w-4 h-4" />
                Refresh
              </button>
            </div>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="mt-4 p-4 bg-stone-50 dark:bg-primary-950 rounded-lg border border-stone-200 dark:border-primary-800">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-stone-700 dark:text-stone-300 mb-1">
                    Start Node
                  </label>
                  <div className="relative">
                     <HiMagnifyingGlass className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-400" />
                    <input
                      type="text"
                      value={startNode}
                      onChange={(e) => setStartNode(e.target.value)}
                      placeholder="e.g., Patents Act 1970"
                      className="w-full pl-10 pr-4 py-2 text-sm border border-stone-300 dark:border-primary-700 rounded-lg bg-white dark:bg-primary-900 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-stone-700 dark:text-stone-300 mb-1">
                    Max Depth
                  </label>
                  <select
                    value={maxDepth}
                    onChange={(e) => setMaxDepth(parseInt(e.target.value))}
                    className="w-full px-4 py-2 text-sm border border-stone-300 dark:border-primary-700 rounded-lg bg-white dark:bg-primary-900 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value={1}>1 (Direct relationships)</option>
                    <option value={2}>2 (Extended network)</option>
                    <option value={3}>3 (Full context)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-stone-700 dark:text-stone-300 mb-1">
                    Jurisdiction
                  </label>
                  <select
                    value={jurisdiction}
                    onChange={(e) => setJurisdiction(e.target.value)}
                    className="w-full px-4 py-2 text-sm border border-stone-300 dark:border-primary-700 rounded-lg bg-white dark:bg-primary-900 text-stone-900 dark:text-stone-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="All">All Jurisdictions</option>
                    <option value="India">India</option>
                    <option value="International">International</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <button
                    onClick={() => setShowFilters(false)}
                    className="w-full px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    Apply Filters
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <KnowledgeGraph
          startNode={startNode || null}
          searchQuery={startNode}
          maxDepth={maxDepth}
          jurisdiction={jurisdiction}
          height={680}
        />

        {/* Info Panel */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white dark:bg-primary-900 rounded-lg border border-stone-200 dark:border-primary-800">
            <h3 className="text-sm font-semibold text-stone-900 dark:text-stone-100 mb-2">
              How to Use
            </h3>
            <ul className="text-xs text-stone-600 dark:text-stone-400 space-y-1">
              <li>• Click and drag nodes to reposition</li>
              <li>• Use mouse wheel to zoom in/out</li>
              <li>• Click edges to see relationship types</li>
              <li>• Use filters to explore specific concepts</li>
            </ul>
          </div>
          <div className="p-4 bg-white dark:bg-primary-900 rounded-lg border border-stone-200 dark:border-primary-800">
            <h3 className="text-sm font-semibold text-stone-900 dark:text-stone-100 mb-2">
              Graph Features
            </h3>
            <ul className="text-xs text-stone-600 dark:text-stone-400 space-y-1">
              <li>• Statutes: Legal acts and regulations</li>
              <li>• Sections: Specific legal provisions</li>
              <li>• Concepts: Key legal terms</li>
              <li>• Frameworks: International treaties</li>
            </ul>
          </div>
          <div className="p-4 bg-white dark:bg-primary-900 rounded-lg border border-stone-200 dark:border-primary-800">
            <h3 className="text-sm font-semibold text-stone-900 dark:text-stone-100 mb-2">
              Relationship Types
            </h3>
            <ul className="text-xs text-stone-600 dark:text-stone-400 space-y-1">
              <li>• CONTAINS: Statute has sections</li>
              <li>• GOVERNS: Section applies to concepts</li>
              <li>• EXCLUDES: Section prohibits items</li>
              <li>• REFERENCES: Section cites cases</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GraphView;
