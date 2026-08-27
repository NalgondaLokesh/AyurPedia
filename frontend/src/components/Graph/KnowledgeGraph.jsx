import React, { useState, useCallback, useEffect, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Handle,
  Position,
  useReactFlow,
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  HiShieldCheck,
  HiDocumentText,
  HiScale,
  HiBeaker,
  HiGlobeAmericas,
  HiCheckCircle,
  HiTag,
  HiBookmark,
  HiBuildingLibrary,
  HiSparkles,
  HiXMark,
  HiArrowsPointingOut,
  HiArrowPath
} from 'react-icons/hi2';
import api from '../../services/api';

// Visual styling tokens and colors for circle nodes
const NODE_CONFIGS = {
  Document: {
    bg: '#2563eb', // blue-600
    glow: 'rgba(37, 99, 235, 0.4)',
    border: '#1d4ed8',
    icon: HiBuildingLibrary,
    label: 'Document',
    size: 48,
    tier: 0
  },
  Statute: {
    bg: '#2563eb',
    glow: 'rgba(37, 99, 235, 0.4)',
    border: '#1d4ed8',
    icon: HiBuildingLibrary,
    label: 'Statute',
    size: 48,
    tier: 0
  },
  Law: {
    bg: '#0284c7', // sky-600
    glow: 'rgba(2, 132, 199, 0.4)',
    border: '#0369a1',
    icon: HiScale,
    label: 'Law',
    size: 46,
    tier: 0
  },
  Framework: {
    bg: '#0891b2', // cyan-600
    glow: 'rgba(8, 145, 178, 0.4)',
    border: '#0e7490',
    icon: HiGlobeAmericas,
    label: 'Framework',
    size: 46,
    tier: 0
  },
  Jurisdiction: {
    bg: '#475569', // slate-600
    glow: 'rgba(71, 85, 105, 0.4)',
    border: '#334155',
    icon: HiGlobeAmericas,
    label: 'Jurisdiction',
    size: 44,
    tier: 0
  },
  Section: {
    bg: '#16a34a', // green-600
    glow: 'rgba(22, 163, 74, 0.4)',
    border: '#15803d',
    icon: HiDocumentText,
    label: 'Section',
    size: 40,
    tier: 1
  },
  Article: {
    bg: '#059669', // emerald-600
    glow: 'rgba(5, 150, 105, 0.4)',
    border: '#047857',
    icon: HiDocumentText,
    label: 'Article',
    size: 40,
    tier: 1
  },
  Regulation: {
    bg: '#d97706', // amber-600
    glow: 'rgba(217, 119, 6, 0.4)',
    border: '#b45309',
    icon: HiShieldCheck,
    label: 'Regulation',
    size: 40,
    tier: 1
  },
  Compliance: {
    bg: '#e11d48', // rose-600
    glow: 'rgba(225, 29, 72, 0.4)',
    border: '#be123c',
    icon: HiCheckCircle,
    label: 'Compliance',
    size: 38,
    tier: 2
  },
  Entity: {
    bg: '#7c3aed', // violet-600
    glow: 'rgba(124, 58, 237, 0.4)',
    border: '#6d28d9',
    icon: HiSparkles,
    label: 'Entity',
    size: 36,
    tier: 2
  },
  Topic: {
    bg: '#4f46e5', // indigo-600
    glow: 'rgba(79, 70, 229, 0.4)',
    border: '#4338ca',
    icon: HiTag,
    label: 'Topic',
    size: 36,
    tier: 2
  },
  Formulation: {
    bg: '#0d9488', // teal-600
    glow: 'rgba(13, 148, 136, 0.4)',
    border: '#0f766e',
    icon: HiBeaker,
    label: 'Formulation',
    size: 38,
    tier: 2
  },
  Ingredient: {
    bg: '#ea580c', // orange-600
    glow: 'rgba(234, 88, 12, 0.4)',
    border: '#c2410c',
    icon: HiBeaker,
    label: 'Ingredient',
    size: 36,
    tier: 2
  },
  Concept: {
    bg: '#9333ea', // purple-600
    glow: 'rgba(147, 51, 234, 0.4)',
    border: '#7e22ce',
    icon: HiBookmark,
    label: 'Concept',
    size: 36,
    tier: 2
  },
  Case: {
    bg: '#ca8a04', // yellow-600
    glow: 'rgba(202, 138, 4, 0.4)',
    border: '#a16207',
    icon: HiScale,
    label: 'Case',
    size: 38,
    tier: 2
  }
};

// Edge relationship styling
const RELATION_STYLES = {
  GOVERNED_BY: { stroke: '#3b82f6', bg: '#eff6ff', text: '#1d4ed8' },
  HAS_SECTION: { stroke: '#22c55e', bg: '#f0fdf4', text: '#15803d' },
  HAS_ARTICLE: { stroke: '#10b981', bg: '#ecfdf5', text: '#047857' },
  BELONGS_TO: { stroke: '#14b8a6', bg: '#f0fdfa', text: '#0f766e' },
  CONTAINS_ENTITY: { stroke: '#a855f7', bg: '#faf5ff', text: '#6d28d9' },
  HAS_TOPIC: { stroke: '#6366f1', bg: '#eef2ff', text: '#4338ca' },
  REQUIRES: { stroke: '#f43f5e', bg: '#fff1f2', text: '#be123c' },
  RELATES_TO: { stroke: '#8b5cf6', bg: '#f5f3ff', text: '#5b21b6' },
  REFERENCES: { stroke: '#f59e0b', bg: '#fffbeb', text: '#b45309' },
  REFERS_TO: { stroke: '#06b6d4', bg: '#ecfeff', text: '#0e7490' },
  DEFAULT: { stroke: '#94a3b8', bg: '#f8fafc', text: '#475569' }
};

// Small Circle Node Component
const CircleGraphNode = ({ data, selected }) => {
  const label = data.label || data.type || 'Entity';
  const config = NODE_CONFIGS[label] || NODE_CONFIGS.Entity;
  const Icon = config.icon;
  const size = config.size || 38;

  const nodeTitle = data.name || data.title || data.id || '';
  const sectionBadge = data.section || data.number;

  return (
    <div className="relative flex flex-col items-center group cursor-pointer select-none">
      {/* Target Handles */}
      <Handle
        type="target"
        position={Position.Top}
        className="!opacity-0 !w-2 !h-2 !pointer-events-none"
      />
      <Handle
        type="target"
        position={Position.Left}
        className="!opacity-0 !w-2 !h-2 !pointer-events-none"
      />

      {/* Circle Body */}
      <div
        className={`relative flex items-center justify-center rounded-full text-white transition-all duration-300 transform group-hover:scale-115 ${
          selected
            ? 'scale-125 ring-4 ring-offset-2 ring-primary-500 z-30'
            : 'hover:shadow-lg'
        }`}
        style={{
          width: `${size}px`,
          height: `${size}px`,
          backgroundColor: config.bg,
          boxShadow: selected
            ? `0 0 20px ${config.glow}, 0 0 40px ${config.glow}`
            : `0 4px 14px ${config.glow}`,
          border: `2.5px solid ${selected ? '#ffffff' : 'rgba(255, 255, 255, 0.85)'}`
        }}
      >
        {/* Inner Icon or Section text */}
        {sectionBadge && String(sectionBadge).length <= 4 ? (
          <span className="text-[11px] font-extrabold tracking-tighter drop-shadow">
            {sectionBadge}
          </span>
        ) : (
          <Icon className="w-4 h-4 drop-shadow" />
        )}

        {/* Small Type Indicator Dot */}
        <span
          className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-white"
          style={{ backgroundColor: config.border }}
        />
      </div>

      {/* Text Label Beneath Circle */}
      <div className="mt-1.5 max-w-[130px] text-center pointer-events-none">
        <span
          className={`inline-block px-2 py-0.5 rounded-md text-[11px] font-semibold leading-tight line-clamp-2 transition-all ${
            selected
              ? 'bg-stone-900 text-white shadow-md'
              : 'bg-white/90 dark:bg-stone-900/90 text-stone-800 dark:text-stone-100 border border-stone-200/80 dark:border-stone-800 shadow-sm backdrop-blur-sm group-hover:border-primary-400'
          }`}
        >
          {nodeTitle}
        </span>
      </div>

      {/* Source Handles */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!opacity-0 !w-2 !h-2 !pointer-events-none"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!opacity-0 !w-2 !h-2 !pointer-events-none"
      />
    </div>
  );
};

const nodeTypes = {
  custom: CircleGraphNode
};

/**
 * Concentric Force Layout for Circle Nodes.
 * Spreads root documents/statutes in center, sections in middle orbit, and entities on outer ring.
 */
const calculateConcentricLayout = (nodes, edges) => {
  if (!nodes.length) return [];

  const tiers = { 0: [], 1: [], 2: [] };
  nodes.forEach((node) => {
    const label = node.data?.label || node.label || 'Entity';
    const tier = NODE_CONFIGS[label]?.tier ?? 2;
    tiers[tier].push(node);
  });

  const centerX = 500;
  const centerY = 400;
  const tierRadii = { 0: 170, 1: 340, 2: 520 };

  const positionedNodes = [];

  Object.entries(tiers).forEach(([tierStr, tierNodes]) => {
    const tier = parseInt(tierStr, 10);
    const radius = tierRadii[tier] || 460;
    const count = tierNodes.length;

    tierNodes.forEach((node, idx) => {
      const angle = (2 * Math.PI * idx) / (count || 1) - Math.PI / 2;
      const jitterX = Math.sin(idx * 2.5) * 15;
      const jitterY = Math.cos(idx * 2.5) * 15;

      const x = centerX + radius * Math.cos(angle) + jitterX;
      const y = centerY + radius * Math.sin(angle) + jitterY;

      positionedNodes.push({
        ...node,
        position: { x, y }
      });
    });
  });

  return positionedNodes;
};

const KnowledgeGraphInner = ({
  startNode = null,
  maxDepth = 2,
  height = 680,
  jurisdiction = 'All',
  searchQuery = ''
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNodeData, setSelectedNodeData] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });

  const { fitView } = useReactFlow();

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((event, node) => {
    setSelectedNodeData(node.data);
  }, []);

  // Fetch graph data from backend API
  const fetchGraphData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (startNode) params.append('start_node', startNode);
      params.append('max_depth', maxDepth);
      if (jurisdiction !== 'All') params.append('jurisdiction', jurisdiction);

      const response = await api.get(`/api/graph/explore?${params.toString()}`);
      const data = response.data;

      if (data.success && data.nodes) {
        // 1. Transform Nodes into Circle Graph Nodes
        const rawNodes = data.nodes.map((node) => {
          const label = node.label || node.data?.labels?.[0] || 'Entity';
          const name = node.data?.name || node.data?.title || node.id;
          return {
            id: String(node.id),
            type: 'custom',
            data: {
              id: node.id,
              name,
              label,
              section: node.data?.section || node.data?.number,
              jurisdiction: node.data?.jurisdiction,
              year: node.data?.year,
              category: node.data?.category || node.data?.type,
              context: node.data?.context || node.data?.title,
              ...node.data
            }
          };
        });

        // 2. Transform Edges with curved arrows & compact relationship badges
        const rawEdges = (data.relationships || []).map((rel, idx) => {
          const relType = rel.type || 'RELATES_TO';
          const relStyle = RELATION_STYLES[relType] || RELATION_STYLES.DEFAULT;

          return {
            id: rel.id || `edge-${rel.from}-${rel.to}-${idx}`,
            source: String(rel.from),
            target: String(rel.to),
            label: relType.replace(/_/g, ' '),
            type: 'floating' || 'smoothstep',
            animated: ['REQUIRES', 'GOVERNS', 'CONTAINS_ENTITY'].includes(relType),
            markerEnd: {
              type: MarkerType.ArrowClosed,
              color: relStyle.stroke,
              width: 14,
              height: 14
            },
            style: {
              stroke: relStyle.stroke,
              strokeWidth: 1.75,
              opacity: 0.85
            },
            labelStyle: {
              fontSize: 9,
              fontWeight: 700,
              fill: relStyle.text,
              fontFamily: 'Inter, system-ui, sans-serif'
            },
            labelBgStyle: {
              fill: relStyle.bg,
              fillOpacity: 0.9,
              rx: 4,
              ry: 4
            },
            labelBgPadding: [4, 2]
          };
        });

        // 3. Apply Concentric Orbital Layout
        const layoutedNodes = calculateConcentricLayout(rawNodes, rawEdges);

        setNodes(layoutedNodes);
        setEdges(rawEdges);
        setStats({ nodes: layoutedNodes.length, edges: rawEdges.length });

        setTimeout(() => {
          fitView({ padding: 0.2, duration: 600 });
        }, 150);
      } else {
        throw new Error(data.message || 'No graph data found');
      }
    } catch (err) {
      console.error('Failed to load graph data:', err);
      setError(err.message || 'Failed to fetch graph data');
    } finally {
      setLoading(false);
    }
  }, [startNode, maxDepth, jurisdiction, setNodes, setEdges, fitView]);

  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  // Filter nodes based on category pill
  const filteredNodes = useMemo(() => {
    if (activeFilter === 'All') return nodes;
    return nodes.map((n) => ({
      ...n,
      hidden: n.data.label !== activeFilter
    }));
  }, [nodes, activeFilter]);

  // Filter edges based on visible nodes
  const filteredEdges = useMemo(() => {
    if (activeFilter === 'All') return edges;
    const visibleNodeIds = new Set(
      filteredNodes.filter((n) => !n.hidden).map((n) => n.id)
    );
    return edges.map((e) => ({
      ...e,
      hidden: !visibleNodeIds.has(e.source) || !visibleNodeIds.has(e.target)
    }));
  }, [edges, filteredNodes, activeFilter]);

  // Handle Search Highlighting & Zoom
  useEffect(() => {
    if (!searchQuery.trim() || !nodes.length) return;
    const match = nodes.find((n) =>
      n.data.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (match) {
      setSelectedNodeData(match.data);
      fitView({
        nodes: [{ id: match.id }],
        duration: 800,
        padding: 1.0
      });
    }
  }, [searchQuery, nodes, fitView]);

  return (
    <div
      className="relative rounded-2xl overflow-hidden border border-stone-200 dark:border-primary-800 bg-stone-900/5 dark:bg-stone-950/40 shadow-inner"
      style={{ height }}
    >
      {/* Category Filter Pills */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-1.5 bg-white/90 dark:bg-primary-900/90 backdrop-blur-md px-3 py-2 rounded-2xl border border-stone-200 dark:border-primary-700 shadow-md flex-wrap max-w-[85%]">
        <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider mr-1">
          Nodes:
        </span>
        {['All', 'Document', 'Law', 'Section', 'Entity', 'Topic', 'Formulation', 'Compliance'].map((cat) => {
          const cfg = NODE_CONFIGS[cat];
          return (
            <button
              key={cat}
              onClick={() => setActiveFilter(cat)}
              className={`text-xs px-2.5 py-1 rounded-xl font-medium transition-all flex items-center gap-1.5 ${
                activeFilter === cat
                  ? 'bg-primary-600 text-white shadow-sm'
                  : 'text-stone-700 dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-primary-800'
              }`}
            >
              {cfg && (
                <span
                  className="w-2 h-2 rounded-full inline-block"
                  style={{ backgroundColor: cfg.bg }}
                />
              )}
              {cat}
            </button>
          );
        })}
      </div>

      {/* Live Graph Counters */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2 bg-white/90 dark:bg-primary-900/90 backdrop-blur-md px-3.5 py-2 rounded-2xl border border-stone-200 dark:border-primary-700 shadow-md text-xs font-semibold text-stone-700 dark:text-stone-300">
        <span>Nodes: <strong className="text-primary-600 dark:text-primary-400">{stats.nodes}</strong></span>
        <span className="text-stone-300 dark:text-primary-700">|</span>
        <span>Edges: <strong className="text-emerald-600 dark:text-emerald-400">{stats.edges}</strong></span>
        <button
          onClick={fetchGraphData}
          title="Recalculate Force Layout"
          className="ml-1 p-1 rounded-lg hover:bg-stone-100 dark:hover:bg-primary-800 text-stone-500"
        >
          <HiArrowPath className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-white/80 dark:bg-primary-950/80 backdrop-blur-sm">
          <div className="text-center">
            <div className="inline-block w-9 h-9 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-3"></div>
            <p className="text-sm font-medium text-stone-700 dark:text-stone-300">
              Rendering circle nodes & graph edges...
            </p>
          </div>
        </div>
      )}

      {/* Error Notice */}
      {error && !loading && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-20 bg-rose-50 border border-rose-200 text-rose-800 px-4 py-3 rounded-2xl shadow-lg text-sm flex items-center gap-2">
          <span>Failed to load graph: {error}</span>
          <button onClick={fetchGraphData} className="underline font-semibold ml-2">Retry</button>
        </div>
      )}

      {/* ReactFlow Canvas */}
      <ReactFlow
        nodes={filteredNodes}
        edges={filteredEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        maxZoom={2.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.9 }}
      >
        <Background color="#94a3b8" gap={24} size={1.2} />
        <Controls className="!bg-white !dark:bg-primary-900 !border !border-stone-200 !dark:border-primary-700 !shadow-lg !rounded-2xl" />
        <MiniMap
          nodeStrokeWidth={2}
          nodeColor={(node) => {
            const label = node.data?.label || 'Entity';
            return NODE_CONFIGS[label]?.bg || '#94a3b8';
          }}
          className="!bg-white/90 !dark:bg-primary-900/90 !border !border-stone-200 !dark:border-primary-700 !rounded-2xl !shadow-md"
        />
      </ReactFlow>

      {/* Interactive Node Inspector Drawer */}
      {selectedNodeData && (
        <div className="absolute top-4 bottom-4 right-4 z-20 w-80 bg-white/95 dark:bg-primary-900/95 backdrop-blur-lg border border-stone-200 dark:border-primary-700 rounded-3xl shadow-2xl p-5 flex flex-col justify-between overflow-y-auto animate-in slide-in-from-right duration-200">
          <div>
            {/* Header with Circular Type Badge */}
            <div className="flex items-start justify-between gap-2 pb-3 border-b border-stone-200 dark:border-primary-800">
              <div className="flex items-center gap-2.5">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-md"
                  style={{
                    backgroundColor: (NODE_CONFIGS[selectedNodeData.label] || NODE_CONFIGS.Entity).bg
                  }}
                >
                  {selectedNodeData.section || selectedNodeData.number || (
                    React.createElement(
                      (NODE_CONFIGS[selectedNodeData.label] || NODE_CONFIGS.Entity).icon,
                      { className: 'w-4 h-4' }
                    )
                  )}
                </div>
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-stone-500">
                    {selectedNodeData.label || 'Entity'}
                  </span>
                  <h3 className="text-sm font-bold text-stone-900 dark:text-stone-100 leading-snug">
                    {selectedNodeData.name || selectedNodeData.title || selectedNodeData.id}
                  </h3>
                </div>
              </div>
              <button
                onClick={() => setSelectedNodeData(null)}
                className="p-1 rounded-lg hover:bg-stone-100 dark:hover:bg-primary-800 text-stone-500"
              >
                <HiXMark className="w-5 h-5" />
              </button>
            </div>

            {/* Properties Grid */}
            <div className="mt-4 space-y-3 text-xs">
              {selectedNodeData.jurisdiction && (
                <div>
                  <span className="font-semibold text-stone-500 dark:text-stone-400 block mb-0.5">Jurisdiction</span>
                  <span className="text-stone-800 dark:text-stone-200 bg-stone-100 dark:bg-primary-800 px-2 py-1 rounded-lg inline-block font-medium">
                    {selectedNodeData.jurisdiction}
                  </span>
                </div>
              )}

              {(selectedNodeData.section || selectedNodeData.number) && (
                <div>
                  <span className="font-semibold text-stone-500 dark:text-stone-400 block mb-0.5">Section / Article</span>
                  <span className="text-stone-800 dark:text-stone-200 font-mono bg-stone-100 dark:bg-primary-800 px-2 py-1 rounded-lg inline-block font-semibold">
                    {selectedNodeData.section || selectedNodeData.number}
                  </span>
                </div>
              )}

              {selectedNodeData.type && (
                <div>
                  <span className="font-semibold text-stone-500 dark:text-stone-400 block mb-0.5">Classification Type</span>
                  <span className="text-stone-800 dark:text-stone-200">
                    {selectedNodeData.type}
                  </span>
                </div>
              )}

              {selectedNodeData.context && (
                <div>
                  <span className="font-semibold text-stone-500 dark:text-stone-400 block mb-0.5">Context & Summary</span>
                  <p className="text-stone-700 dark:text-stone-300 leading-relaxed bg-stone-50 dark:bg-primary-950 p-2.5 rounded-xl border border-stone-200 dark:border-primary-800">
                    {selectedNodeData.context}
                  </p>
                </div>
              )}

              {selectedNodeData.ingredients && Array.isArray(selectedNodeData.ingredients) && (
                <div>
                  <span className="font-semibold text-stone-500 dark:text-stone-400 block mb-0.5">Ingredients</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedNodeData.ingredients.map((ing, i) => (
                      <span key={i} className="px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md text-[11px]">
                        {ing}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action Footer */}
          <div className="pt-4 mt-4 border-t border-stone-200 dark:border-primary-800 flex gap-2">
            <button
              onClick={() => {
                fitView({ nodes: [{ id: selectedNodeData.id }], duration: 600, padding: 1.0 });
              }}
              className="flex-1 py-2 px-3 bg-stone-100 dark:bg-primary-800 hover:bg-stone-200 dark:hover:bg-primary-700 text-stone-800 dark:text-stone-200 text-xs font-semibold rounded-xl transition-colors flex items-center justify-center gap-1.5"
            >
              <HiArrowsPointingOut className="w-4 h-4" /> Focus Node
            </button>
            <button
              onClick={() => setSelectedNodeData(null)}
              className="py-2 px-3 bg-primary-600 hover:bg-primary-700 text-white text-xs font-semibold rounded-xl transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const KnowledgeGraph = (props) => (
  <ReactFlowProvider>
    <KnowledgeGraphInner {...props} />
  </ReactFlowProvider>
);

export default KnowledgeGraph;
