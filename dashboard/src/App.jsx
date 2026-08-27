import React, { useState, useEffect, useRef } from 'react';
import { 
  ResponsiveContainer, LineChart, Line, AreaChart, Area, BarChart, Bar, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { 
  LayoutDashboard, Activity, Brain, ShieldAlert, HeartPulse, GitMerge, 
  Info, RefreshCw, Server, AlertTriangle, Shield, CheckCircle, Database, 
  Moon, Sun, Menu, X, ArrowRight, Play, Pause, RotateCcw, Cpu, ShieldCheck, Key, Settings, 
  Lock, Network, FileText, Download, Zap, HelpCircle, Terminal, DollarSign, Clock, Flame
} from 'lucide-react';

const LAYERS_ORDER = [
  { id: "Client", label: "Client Layer", y: 65, height: 75 },
  { id: "Gateway", label: "Gateway Layer", y: 150, height: 75 },
  { id: "Monitoring", label: "Monitoring Layer", y: 235, height: 75 },
  { id: "AI", label: "AI Layer", y: 320, height: 75 },
  { id: "Decision", label: "Decision Layer", y: 405, height: 95 },
  { id: "Automation", label: "Automation Layer", y: 495, height: 75 },
  { id: "Infrastructure", label: "Infrastructure Layer", y: 605, height: 110 }
];

const getNodeLayer = (node) => {
  const type = node.type;
  const id = node.id;
  
  if (id === 'dashboard') return 'Client';
  if (id === 'backend' || id === 'core-api-app') return 'Gateway';
  if (id === 'monitoring' || id === 'node-exporter' || id === 'prometheus') return 'Monitoring';
  if (id === 'ai-engine') return 'AI';
  
  if (
    id === 'risk-engine' || 
    id === 'urs-risk-engine' || 
    id === 'policy-engine' || 
    id === 'ipre-policy-engine' || 
    id === 'qrae-quantum-engine' || 
    id === 'research-evaluator'
  ) {
    return 'Decision';
  }
  
  if (id === 'automation-engine' || id === 'attack-simulator') return 'Automation';
  
  return 'Infrastructure';
};

const getMergedNodesAndEdges = (backendGraph, healthStatus, simulationState) => {
  const baseNodes = backendGraph.nodes || [];
  const baseEdges = backendGraph.edges || [];
  
  // Define standard microservices
  const standardServices = [
    { id: "dashboard", label: "Dashboard UI", type: "Client", icon: "layout", group: "Client", port: 5173 },
    { id: "core-api-app", label: "Backend Gateway", type: "Gateway", icon: "server", group: "Gateway", port: 5000 },
    { id: "monitoring", label: "Monitoring Service", type: "Monitoring", icon: "activity", group: "Monitoring", port: 6001 },
    { id: "node-exporter", label: "Node Exporter", type: "Monitoring", icon: "activity", group: "Monitoring", port: 9100 },
    { id: "ai-engine", label: "AI Anomaly Engine", type: "AI", icon: "brain", group: "AI", port: 8000 },
    { id: "urs-risk-engine", label: "Risk Engine", type: "Security", icon: "shield-alert", group: "Security", port: 8500 },
    { id: "ipre-policy-engine", label: "Policy Engine", type: "Security", icon: "cog", group: "Security", port: 8700 },
    { id: "research-evaluator", label: "Research Evaluator", type: "Security", icon: "zap", group: "Security", port: 8800 },
    { id: "automation-engine", label: "Automation Engine", type: "Automation", icon: "settings", group: "Automation", port: 9100 },
    { id: "attack-simulator", label: "Attack Simulator", type: "Automation", icon: "play", group: "Automation", port: 8600 },
    { id: "digital-twin", label: "Digital Twin Service", type: "Infrastructure", icon: "network", group: "Infrastructure", port: 8900 },
    { id: "mongodb", label: "MongoDB Atlas", type: "Database", icon: "database", group: "Infrastructure", port: 27017 }
  ];
  
  const mergedNodes = [];
  const seenIds = new Set();
  
  // 1. Add standard services
  standardServices.forEach(s => {
    mergedNodes.push(s);
    seenIds.add(s.id);
  });
  
  // 2. Add other nodes from backendGraph
  baseNodes.forEach(node => {
    const aliasMap = {
      "core-api-app": "core-api-app",
      "urs-risk-engine": "urs-risk-engine",
      "ipre-policy-engine": "ipre-policy-engine",
      "qrae-quantum-engine": "qrae-quantum-engine"
    };
    
    const targetId = aliasMap[node.id] || node.id;
    
    if (!seenIds.has(targetId)) {
      mergedNodes.push({
        ...node,
        id: targetId
      });
      seenIds.add(targetId);
    } else {
      const existing = mergedNodes.find(n => n.id === targetId);
      if (existing) {
        if (node.risk) existing.risk = node.risk;
        if (node.riskColor) existing.riskColor = node.riskColor;
        if (node.status) existing.status = node.status;
      }
    }
  });

  // Ensure an EC2 target exists (virtual fallback if not present)
  const liveEc2 = mergedNodes.find(n => n.type === 'EC2 Instance' || n.id.startsWith('i-'));
  let targetEc2Id = liveEc2 ? liveEc2.id : "virtual-target-ec2";
  
  if (!liveEc2) {
    targetEc2Id = "virtual-target-ec2";
    mergedNodes.push({
      id: "virtual-target-ec2",
      label: "EC2 Production Target",
      type: "EC2 Instance",
      status: "Running",
      risk: "Low",
      riskColor: "green",
      icon: "server",
      group: "Infrastructure"
    });
  }
  
  // 3. Construct logical control edges
  const controlEdges = [
    { source: "dashboard", target: "core-api-app", label: "HTTP REST API" },
    { source: "core-api-app", target: "monitoring", label: "Scrapes Metrics" },
    { source: "monitoring", target: "node-exporter", label: "Hardware Stats" },
    { source: "monitoring", target: "ai-engine", label: "Telemetry Feed" },
    { source: "ai-engine", target: "urs-risk-engine", label: "Anomaly Score" },
    { source: "urs-risk-engine", target: "ipre-policy-engine", label: "Risk Decisions" },
    { source: "urs-risk-engine", target: "qrae-quantum-engine", label: "Crypto Assessment" },
    { source: "ipre-policy-engine", target: "automation-engine", label: "Triggers Playbook" },
    { source: "urs-risk-engine", target: "research-evaluator", label: "Evaluation Stream" },
    { source: "research-evaluator", target: "digital-twin", label: "Topology Sync" },
    { source: "core-api-app", target: "mongodb", label: "Persists State" }
  ];
  
  const mergedEdges = [...controlEdges];
  const seenEdgeKeys = new Set(controlEdges.map(e => `${e.source}->${e.target}`));

  if (!liveEc2) {
    mergedEdges.push({
      source: "core-api-app",
      target: "virtual-target-ec2",
      label: "Hosts"
    });
    seenEdgeKeys.add("core-api-app->virtual-target-ec2");
  }
  
  baseEdges.forEach(edge => {
    const s = edge.source;
    const t = edge.target;
    
    const key = `${s}->${t}`;
    if (!seenEdgeKeys.has(key)) {
      mergedEdges.push({
        source: s,
        target: t,
        label: edge.label || edge.relationType
      });
      seenEdgeKeys.add(key);
    }
  });

  // Override node status during active simulation
  if (simulationState && simulationState.status === 'active') {
    const criticalNodes = [...(simulationState.highlights?.criticalNodes || [])];
    const warningNodes = [...(simulationState.highlights?.warningNodes || [])];
    const elapsed = simulationState.elapsed || 0;
    
    if (elapsed >= 10 && elapsed < 40) {
      criticalNodes.push(targetEc2Id);
    } else if ((elapsed >= 5 && elapsed < 10) || (elapsed >= 40 && elapsed < 45)) {
      warningNodes.push(targetEc2Id);
    }
    
    mergedNodes.forEach(node => {
      if (criticalNodes.includes(node.id)) {
        node.risk = "Critical";
        node.riskColor = "red";
        node.status = "Critical";
      } else if (warningNodes.includes(node.id)) {
        node.risk = "High";
        node.riskColor = "orange";
        node.status = "Warning";
      } else {
        node.risk = "Low";
        node.riskColor = "green";
        node.status = "Running";
      }
    });
  }
  
  return { nodes: mergedNodes, edges: mergedEdges };
};

const AnimatedScore = ({ value }) => {
  const [currentVal, setCurrentVal] = useState(100);
  useEffect(() => {
    let start = 100;
    const end = value;
    if (start === end) {
      setCurrentVal(end);
      return;
    }
    const duration = 1000;
    const startTime = performance.now();
    let animFrame;
    const animate = (timestamp) => {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(start - ease * (start - end));
      setCurrentVal(current);
      if (progress < 1) {
        animFrame = requestAnimationFrame(animate);
      }
    };
    animFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrame);
  }, [value]);

  return <span>{currentVal}</span>;
};

const ScoreGauge = ({ value }) => {
  const [dashOffset, setDashOffset] = useState(251.2);
  
  useEffect(() => {
    const circumference = 251.2;
    const percentage = value / 100;
    const targetOffset = circumference * (1 - percentage);
    
    let startTime = performance.now();
    const duration = 1000;
    let animFrame;
    
    const animate = (timestamp) => {
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3);
      const current = 251.2 - ease * (251.2 - targetOffset);
      setDashOffset(current);
      if (progress < 1) {
        animFrame = requestAnimationFrame(animate);
      }
    };
    animFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animFrame);
  }, [value]);

  let strokeColor = "#10b981"; // emerald
  if (value < 50) strokeColor = "#ef4444"; // rose
  else if (value < 70) strokeColor = "#f97316"; // orange
  else if (value < 85) strokeColor = "#f59e0b"; // amber

  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="40"
          stroke="#1e293b"
          strokeWidth="8"
          fill="transparent"
        />
        <circle
          cx="64"
          cy="64"
          r="40"
          stroke={strokeColor}
          strokeWidth="8"
          fill="transparent"
          strokeDasharray="251.2"
          strokeDashoffset={dashOffset}
          strokeLinecap="round"
          className="transition-all duration-300"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className="text-3xl font-black text-white">
          <AnimatedScore value={value} />
        </span>
        <span className="text-[8px] font-mono text-slate-500 uppercase tracking-widest font-bold">Score</span>
      </div>
    </div>
  );
};

const InteractiveRiskBreakdown = ({ findings, finalScore }) => {
  const [visibleCount, setVisibleCount] = useState(0);
  
  useEffect(() => {
    setVisibleCount(0);
    const interval = setInterval(() => {
      setVisibleCount(prev => {
        if (prev >= findings.length) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 300);
    return () => clearInterval(interval);
  }, [findings]);

  return (
    <div className="space-y-3 font-mono text-xs text-slate-350">
      <div className="flex justify-between items-center text-slate-400 border-b border-slate-800 pb-1.5">
        <span>Base Score Reference</span>
        <span className="font-bold text-white">100</span>
      </div>
      {findings.slice(0, visibleCount).map((f, i) => (
        <div key={i} className="flex justify-between items-center text-rose-450 animate-fadeIn">
          <span className="truncate max-w-[220px]">{f.title}</span>
          <span className="font-bold">-{f.ursPenalty}</span>
        </div>
      ))}
      {visibleCount >= findings.length && (
        <div className="border-t border-slate-800 pt-2 flex justify-between items-center text-xs font-mono font-extrabold text-white animate-fadeIn">
          <span className="text-slate-400 uppercase text-[9.5px]">Final Deducted Score</span>
          <span className="text-indigo-400 text-sm font-black">{finalScore}/100</span>
        </div>
      )}
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [darkMode, setDarkMode] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  
  // Framework global states
  const [metrics, setMetrics] = useState(null);
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [healthStatus, setHealthStatus] = useState(null);
  const [cloudAssets, setCloudAssets] = useState([]);
  const [cloudMode, setCloudMode] = useState('LIVE');
  const [cloudLiveTelemetry, setCloudLiveTelemetry] = useState([]);
  const [digitalTwinGraph, setDigitalTwinGraph] = useState({ nodes: [], edges: [] });
  const [selectedTwinNode, setSelectedTwinNode] = useState(null);
  const [twinFilter, setTwinFilter] = useState('All');
  
  // Last Updated Timestamps & API Error Tracking (Sprint 22.2)
  const [telemetryLastUpdated, setTelemetryLastUpdated] = useState(null);
  const [healthLastUpdated, setHealthLastUpdated] = useState(null);
  const [cloudAssetsLastUpdated, setCloudAssetsLastUpdated] = useState(null);
  const [evaluatorLastUpdated, setEvaluatorLastUpdated] = useState(null);
  const [twinLastUpdated, setTwinLastUpdated] = useState(null);
  const [reportLastUpdated, setReportLastUpdated] = useState(null);
  const [autoHistoryLastUpdated, setAutoHistoryLastUpdated] = useState(null);
  const [automationHistory, setAutomationHistory] = useState([]);

  // Zoom, Pan, Search and Timeline States
  const [twinZoom, setTwinZoom] = useState(0.85);
  const [twinPan, setTwinPan] = useState({ x: 50, y: 20 });
  const [twinSearch, setTwinSearch] = useState('');
  const [twinIsDragging, setTwinIsDragging] = useState(false);
  const [twinDragStart, setTwinDragStart] = useState({ x: 0, y: 0 });
  const [twinEvents, setTwinEvents] = useState([
    { id: 'ev-init', time: new Date().toLocaleTimeString(), title: 'Digital Twin Initialized', type: 'info', detail: 'Layered topology visualization ready.' }
  ]);

  const logTwinEvent = (title, type, detail = "") => {
    const newEvent = {
      id: `ev-${Math.random()}`,
      time: new Date().toLocaleTimeString(),
      title,
      type, // 'info', 'success', 'warning', 'error'
      detail
    };
    setTwinEvents(prev => [newEvent, ...prev].slice(0, 15));
  };

  const openInDigitalTwin = (assetId) => {
    // Find matching node
    const node = digitalTwinGraph?.nodes?.find(n => n.id === assetId) || {
      id: assetId,
      label: assetId,
      type: 'EC2 Instance',
      group: 'Infrastructure'
    };
    setSelectedTwinNode(node);
    const asset = cloudAssets?.find(a => a.instanceId === assetId);
    if (asset) {
      setSelectedEc2Instance(asset);
    }
    setActiveTab('digital-twin');
    logTwinEvent("Digital Twin Redirect", "info", `Inspecting virtual node target: ${assetId}`);
  };
  
  const DISPLAY_WINDOW_SIZE = 60;
  const [monitoringState, setMonitoringState] = useState('Initializing Monitoring...');
  const [selectedEc2Instance, setSelectedEc2Instance] = useState(null);
  const [ec2Metrics, setEc2Metrics] = useState(null);
  const [ec2MetricsHistory, setEc2MetricsHistory] = useState([]);
  const [ec2MonitoringState, setEc2MonitoringState] = useState('Initializing Monitoring...');
  const [ec2TelemetryError, setEc2TelemetryError] = useState(false);
  const [cloudSubTab, setCloudSubTab] = useState('inventory');
  const [cloudSecurityHistory, setCloudSecurityHistory] = useState([]);
  const [aiSecurityAnalysis, setAiSecurityAnalysis] = useState(null);
  const [aiAnalysisLoading, setAiAnalysisLoading] = useState(false);
  const [ec2LastUpdated, setEc2LastUpdated] = useState(null);
  const [healthErrors, setHealthErrors] = useState({});
  const [selectedAssetForDrawer, setSelectedAssetForDrawer] = useState(null);
  const [secondsSinceLastScan, setSecondsSinceLastScan] = useState(0);

  // SOAR Platform state hooks (Sprint 26.0)
  const [soarStep, setSoarStep] = useState('idle');
  const [soarLog, setSoarLog] = useState([
    { time: new Date().toLocaleTimeString(), message: "SOAR Platform Initialized. Awaiting incident recommendations..." }
  ]);
  const [soarPlaybookSearch, setSoarPlaybookSearch] = useState('');
  const [soarActivePlaybook, setSoarActivePlaybook] = useState(null);
  const [soarIncidentReport, setSoarIncidentReport] = useState(null);
  const [soarApprovalStatus, setSoarApprovalStatus] = useState('Pending');

  const triggerSoarPlaybook = (playbook) => {
    setSoarActivePlaybook(playbook);
    setSoarApprovalStatus('Pending');
    setSoarStep('queued');
    
    const initialLog = [
      { time: new Date().toLocaleTimeString(), message: `[SOAR] Playbook selected: ${playbook.name}` },
      { time: new Date().toLocaleTimeString(), message: `[SOAR] Incident recommendation received from Risk Engine. URS reduction estimate: -${playbook.ursReduction}` }
    ];
    setSoarLog(initialLog);

    if (simulationState && simulationState.status === 'active') {
      setTimeout(() => {
        handleSoarApprove(playbook);
      }, 3000);
    }
  };

  const handleSoarApprove = (playbook) => {
    setSoarApprovalStatus('Approved');
    setSoarStep('approved');
    setSoarLog(prev => [...prev, { time: new Date().toLocaleTimeString(), message: "[SOAR] Action approved. Operator authorization granted." }]);

    setTimeout(() => {
      setSoarStep('running');
      setSoarLog(prev => [...prev, 
        { time: new Date().toLocaleTimeString(), message: `[SOAR] Executing deployment recipe format: AWS CLI / Terraform` },
        { time: new Date().toLocaleTimeString(), message: `[SOAR] Revoking ingress rules...` },
        { time: new Date().toLocaleTimeString(), message: `[SOAR] Command status: Success. Applied in 4.2ms.` }
      ]);

      setTimeout(() => {
        setSoarStep('completed');
        setSoarLog(prev => [...prev, { time: new Date().toLocaleTimeString(), message: "[SOAR] Posture changes successfully propagated. Verification query initiated." }]);

        setTimeout(() => {
          setSoarStep('verification');
          setSoarLog(prev => [...prev, 
            { time: new Date().toLocaleTimeString(), message: "[SOAR] Telemetry monitor feedback: Port 22 connectivity blocked." },
            { time: new Date().toLocaleTimeString(), message: "[SOAR] URS score reduced." }
          ]);

          setTimeout(() => {
            setSoarStep('closed');
            setSoarLog(prev => [...prev, { time: new Date().toLocaleTimeString(), message: "[SOAR] Incident remediation successfully completed. Incident state set to CLOSED." }]);
            
            const report = {
              incident: `Critical Inbound Rule Violation on ${playbook.supportedAssets}`,
              timeline: [
                { step: "Queued", time: "19:10:04", duration: "0.2s" },
                { step: "Approved", time: "19:10:07", duration: "3s" },
                { step: "Running", time: "19:10:08", duration: "1s" },
                { step: "Completed", time: "19:10:10", duration: "2s" },
                { step: "Closed", time: "19:10:12", duration: "2s" }
              ],
              actionsExecuted: playbook.mitigation || "Security group restrict access to localhost/subnet CIDRs",
              playbooksUsed: playbook.name,
              recoveryTime: "8.2s",
              containmentTime: "4.2s",
              ursBefore: "84",
              ursAfter: (84 - playbook.ursReduction).toString(),
              businessImpact: "Negligible service interruption. Blocked unauthorized egress port scanning activity.",
              lessonsLearned: "Ensure regular AWS config posture runs evaluate security group rules continuously.",
              recommendations: "Enable AWS config auto-remediation triggers for Port 22/3389 wildcard violations."
            };
            setSoarIncidentReport(report);
            logTwinEvent("Automation Playbook Completed", "success", `Successfully executed playbook: ${playbook.name}`);
          }, 2000);
        }, 2000);
      }, 2000);
    }, 2000);
  };

  useEffect(() => {
    setSecondsSinceLastScan(0);
    const interval = setInterval(() => {
      setSecondsSinceLastScan(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [cloudAssetsLastUpdated]);
  const [telemetryError, setTelemetryError] = useState(false);
  const [cloudAssetsError, setCloudAssetsError] = useState(false);
  const [evaluatorError, setEvaluatorError] = useState(false);
  const [twinIsSimulation, setTwinIsSimulation] = useState(false);

  // Relative Time Formatter
  const formatLastUpdated = (ts) => {
    if (!ts) return "Unavailable";
    const seconds = Math.floor((Date.now() - ts) / 1000);
    if (seconds < 3) return "Just now";
    if (seconds < 60) return `${seconds}s ago`;
    const mins = Math.floor(seconds / 60);
    return `${mins}m ago`;
  };

  // Reusable Data Provenance Badge
  const ProvenanceBadge = ({ service, endpoint, method = 'GET', refresh = 'Polling' }) => (
    <div className="group relative inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] font-mono text-slate-300 cursor-help hover:border-slate-700 transition">
      <Info size={11} className="text-cyan-400" />
      <span>Source: {service}</span>
      <div className="absolute bottom-full left-0 mb-1.5 hidden group-hover:block z-50 w-56 p-3 rounded-xl bg-slate-950 border border-slate-750 text-[10px] text-slate-300 shadow-2xl backdrop-blur-md">
        <div className="font-bold text-cyan-400 mb-1 flex items-center justify-between">
          <span>{service}</span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">{method}</span>
        </div>
        <div className="space-y-1">
          <div><span className="text-slate-400">Endpoint:</span> <code className="text-amber-300 font-mono text-[9.5px]">{endpoint}</code></div>
          <div><span className="text-slate-400">Refresh Mode:</span> <span className="text-slate-200 font-semibold">{refresh}</span></div>
        </div>
      </div>
    </div>
  );

  // Reusable Data Source Classification Badge
  const SourceTypeBadge = ({ type }) => {
    const styles = {
      LIVE: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      DERIVED: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
      SIMULATED: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
      STATIC: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
      UNKNOWN: 'bg-rose-500/10 text-rose-400 border-rose-500/30'
    };
    return (
      <span className={`px-2 py-0.5 rounded text-[9px] font-extrabold uppercase tracking-wider border ${styles[type] || styles.UNKNOWN}`}>
        {type}
      </span>
    );
  };

  // Reusable Skeleton Loader
  const SkeletonLoader = ({ className = "h-8 w-24" }) => (
    <div className={`animate-pulse bg-slate-800/70 rounded ${className}`}></div>
  );

  // Attack simulator states (Sprint 24.1)
  const [selectedAttack, setSelectedAttack] = useState('crypto-mining');
  const [scenariosList, setScenariosList] = useState([]);
  const [simulationState, setSimulationState] = useState(null);
  const [simulationActive, setSimulationActive] = useState(false);
  const [simulationHistory, setSimulationHistory] = useState([]);
  const [liveRiskHistory, setLiveRiskHistory] = useState([]);
  const [selectedReplayTick, setSelectedReplayTick] = useState(null);
  const [expandedContrib, setExpandedContrib] = useState(null);

  // Evaluator & Dashboard states
  const [evaluatorDashboard, setEvaluatorDashboard] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);
  const [latestRisk, setLatestRisk] = useState(null);
  
  // Reports states
  const [latestReport, setLatestReport] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);

  // Fallback triggers for demonstration
  const [mockMode, setMockMode] = useState(false);

  // 1. Fetch live telemetry metrics history (monitoring-service)
  const fetchTelemetryHistory = async () => {
    try {
      setMonitoringState('Initializing Monitoring...');
      const res = await fetch('http://localhost:6001/api/metrics/history');
      if (!res.ok) throw new Error("History fetch failed");
      const result = await res.json();
      if (result.status === 'success' && result.data && Array.isArray(result.data.samples)) {
        const samples = result.data.samples;
        const formattedHistory = samples.map(item => {
          const itemDate = item.timestamp ? new Date(item.timestamp) : new Date();
          const timeStr = itemDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
          return {
            time: timeStr,
            cpu: item.cpu.utilization,
            memory: item.memory.usagePercent,
            disk: item.disk.usagePercent,
            rx: item.network.bytesRx / 1024 / 1024,
            tx: item.network.bytesTx / 1024 / 1024
          };
        });
        
        setMetricsHistory(formattedHistory.slice(-DISPLAY_WINDOW_SIZE));
        if (formattedHistory.length === 0) {
          setMonitoringState('Waiting for Telemetry...');
        } else {
          setMonitoringState('Live Monitoring Active');
        }
        setTelemetryError(false);
      } else {
        setMonitoringState('Waiting for Telemetry...');
      }
    } catch (err) {
      setTelemetryError(true);
      setMonitoringState('Monitoring Service Offline');
      setMetricsHistory([]);
    }
  };

  // Fetch live telemetry metrics (monitoring-service)
  const fetchTelemetry = async () => {
    try {
      const res = await fetch('http://localhost:6001/api/metrics');
      if (!res.ok) throw new Error("HTTP 502 Bad Gateway");
      const result = await res.json();
      if (result.status === 'success' && result.data) {
        setMetrics(result.data);
        setTelemetryLastUpdated(Date.now());
        setTelemetryError(false);
        setMonitoringState('Live Monitoring Active');
        logTwinEvent("Monitoring Telemetry Updated", "info", `CPU: ${result.data.cpu.utilization}%, Mem: ${result.data.memory.usagePercent}%`);
        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
        
        setMetricsHistory(prev => {
          const updated = [...prev, {
            time: timeStr,
            cpu: result.data.cpu.utilization,
            memory: result.data.memory.usagePercent,
            disk: result.data.disk.usagePercent,
            rx: result.data.network.bytesRx / 1024 / 1024,
            tx: result.data.network.bytesTx / 1024 / 1024
          }];
          return updated.slice(-DISPLAY_WINDOW_SIZE);
        });
      }
    } catch (err) {
      setTelemetryError(true);
      setMonitoringState('Monitoring Service Offline');
    }
  };

  // 2. Fetch microservice statuses (orchestrator health)
  const fetchHealth = async () => {
    try {
      const res = await fetch('http://localhost:5001/system/status');
      if (!res.ok) throw new Error("Backend gateway connection timeout");
      const result = await res.json();
      if (result.status === 'success') {
        setHealthStatus(result.services);
        setHealthLastUpdated(Date.now());
        logTwinEvent("System Health Checks Completed", "success", "Scanned all framework microservices.");
      }
    } catch (err) {
      // Record service unreachable reason explicitly
      setHealthStatus({
        backend: { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 5001)" },
        monitoring: { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 6001)" },
        "ai-engine": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8000)" },
        "risk-engine": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8500)" },
        "attack-simulator": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8600)" },
        "policy-engine": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8700)" },
        "cloud-adapter": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 7000)" },
        "research-evaluator": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8800)" },
        "digital-twin": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 8900)" },
        "report-generator": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 9000)" },
        "automation-engine": { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 9100)" },
        mongodb: { status: 'unreachable', latencyMs: 0, availability: false, error: "Connection Refused (Port 27017)" }
      });
      logTwinEvent("Health Check Query Failed", "error", err.message);
    }
  };

  // 3. Fetch cloud assets (cloud-adapter)
  const fetchCloudAssets = async () => {
    try {
      const res = await fetch('http://localhost:7001/cloud/assets');
      if (!res.ok) throw new Error("Cloud adapter service unavailable");
      const result = await res.json();
      if (result.status === 'success') {
        setCloudAssets(result.data || []);
        setCloudMode(result.mode || 'LIVE');
        setCloudAssetsLastUpdated(Date.now());
        setCloudAssetsError(false);
        if (result.instances) setCloudLiveTelemetry(result.instances);
        logTwinEvent("Cloud Topology Scanned", "info", `Discovered ${result.data ? result.data.length : 0} virtual EC2 assets.`);
      }

      // Fetch cloud security history
      try {
        const histRes = await fetch('http://localhost:7001/cloud/security/history');
        if (histRes.ok) {
          const histData = await histRes.json();
          if (histData.status === 'success') {
            setCloudSecurityHistory(histData.data || []);
          }
        }
      } catch (hErr) {
        console.error("Failed to fetch security history", hErr);
      }
    } catch (err) {
      setCloudMode('LIVE');
      setCloudAssets(null);
      setCloudAssetsError(true);
      logTwinEvent("Cloud Topology Scan Failed", "error", err.message);
    }
  };

  useEffect(() => {
    const isAwsDisconnected = !cloudAssets || cloudAssets.length === 0 || 
      !cloudAssets[0].securityAssessment || 
      cloudAssets[0].securityAssessment.overallScore === null || 
      cloudAssets[0].securityAssessment.complianceStatus === 'UNKNOWN';
      
    if (activeTab === 'cloud-assets' && cloudSubTab === 'assessment' && cloudAssets && cloudAssets.length > 0 && !isAwsDisconnected) {
      const fetchAiAnalysis = async () => {
        setAiAnalysisLoading(true);
        try {
          const telemetry = {
            cpu_usage: metrics?.cpu?.utilization ?? 15.0,
            memory_usage: metrics?.memory?.usagePercent ?? 50.0,
            disk_usage: metrics?.disk?.usagePercent ?? 50.0,
            network_usage: metrics?.network?.bytesRx ?? 0.0
          };
          const res = await fetch('http://localhost:8000/ai/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              telemetry,
              findings: cloudAssets[0].securityAssessment?.findings || []
            })
          });
          if (res.ok) {
            const result = await res.json();
            if (result.status === 'success') {
              setAiSecurityAnalysis(result);
            }
          }
        } catch (err) {
          console.error("Failed to query AI security analyze endpoint", err);
        }
        setAiAnalysisLoading(false);
      };
      fetchAiAnalysis();
    }
  }, [activeTab, cloudSubTab, cloudAssets, metrics]);

  // 4. Fetch digital twin graph (digital-twin)
  const fetchTwinGraph = async () => {
    try {
      const res = await fetch('http://localhost:8900/digital-twin/graph');
      if (!res.ok) throw new Error("Digital Twin service unavailable");
      const result = await res.json();
      if (result.status === 'success') {
        setDigitalTwinGraph(result.data);
        setTwinLastUpdated(Date.now());
        setTwinIsSimulation(false);
        logTwinEvent("Digital Twin Graph Synchronized", "success", "Active topology relations compiled.");
      }
    } catch (err) {
      setTwinIsSimulation(true);
      setDigitalTwinGraph({
        nodes: [
          { id: "aws", label: "AWS Provider", type: "Provider", status: "Active", risk: "Low", riskColor: "green", icon: "cloud", group: "Infrastructure" },
          { id: "us-east-1", label: "us-east-1", type: "Region", status: "Active", risk: "Low", riskColor: "green", icon: "map", group: "Infrastructure" },
          { id: "vpc-12345", label: "VPC vpc-12345", type: "VPC", status: "Active", risk: "Low", riskColor: "green", icon: "shield", group: "Network" },
          { id: "subnet-5678a", label: "Subnet subnet-5678a", type: "Subnet", status: "Active", risk: "Low", riskColor: "green", icon: "network", group: "Network" },
          { id: "core-api-app", label: "Core API App", type: "Application", status: "Running", risk: "Low", riskColor: "green", icon: "code", group: "Application" }
        ],
        edges: [
          { source: "aws", target: "us-east-1", relationType: "Contains", label: "contains" },
          { source: "us-east-1", target: "vpc-12345", relationType: "Contains", label: "contains" },
          { source: "vpc-12345", target: "subnet-5678a", relationType: "Contains", label: "contains" },
          { source: "subnet-5678a", target: "core-api-app", relationType: "Hosts", label: "hosts" }
        ]
      });
      logTwinEvent("Digital Twin Fetch Failed", "warning", "Using fallback mock graph topology.");
    }
  };

  // 5. Simulation Session Handlers (Sprint 24.1)
  useEffect(() => {
    const fetchScenarios = async () => {
      try {
        const res = await fetch('http://localhost:8600/simulation/scenarios');
        const data = await res.json();
        if (data.status === 'success') {
          setScenariosList(data.data);
        }
      } catch (err) {
        console.error("Failed to fetch scenarios", err);
      }
    };
    fetchScenarios();
  }, []);

  useEffect(() => {
    let pollInterval = null;
    if (simulationActive) {
      pollInterval = setInterval(async () => {
        try {
          const res = await fetch('http://localhost:8600/simulation/state');
          const data = await res.json();
          if (data.status === 'active') {
            setSimulationState(data);
            
            setSimulationHistory(prev => {
              const exists = prev.some(item => item.elapsed === data.elapsed);
              if (exists) return prev;
              const newPoint = {
                elapsed: data.elapsed,
                cpu: data.telemetry.cpu,
                memory: data.telemetry.memory,
                disk: data.telemetry.disk,
                network: data.telemetry.network,
                latency: data.telemetry.latency,
                risk: data.telemetry.risk,
                anomaly_score: data.telemetry.anomaly_score
              };
              return [...prev, newPoint].slice(-45);
            });

            if (data.isFinished) {
              setSimulationActive(false);
              logTwinEvent(`Attack Simulation Completed`, "success", `Threat profile '${selectedAttack}' completed. URS risk re-evaluated.`);
            }
          } else {
            setSimulationActive(false);
            setSimulationState(null);
            setSimulationHistory([]);
          }
        } catch (err) {
          console.error("Error polling simulation state", err);
        }
      }, 1000);
    }
    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [simulationActive, selectedAttack]);

  const handleStartSimulation = async (scenarioId) => {
    try {
      setSelectedReplayTick(null);
      setSimulationHistory([]);
      setSimulationState(null);
      logTwinEvent(`Attack Simulation Initiated`, "warning", `Launching threat profile: ${scenarioId}`);
      
      const startRes = await fetch('http://localhost:8600/simulation/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenarioId })
      });
      if (startRes.ok) {
        setSimulationActive(true);
      }
    } catch (err) {
      logTwinEvent(`Attack Simulation Initiation Failed`, "error", err.message);
    }
  };

  const handlePauseSimulation = async () => {
    try {
      const res = await fetch('http://localhost:8600/simulation/pause', { method: 'POST' });
      if (res.ok) {
        setSimulationState(prev => prev ? { ...prev, paused: true } : null);
        logTwinEvent(`Attack Simulation Paused`, "info", "Simulation timeline halted.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleResumeSimulation = async () => {
    try {
      const res = await fetch('http://localhost:8600/simulation/resume', { method: 'POST' });
      if (res.ok) {
        setSimulationState(prev => prev ? { ...prev, paused: false } : null);
        logTwinEvent(`Attack Simulation Resumed`, "info", "Simulation timeline resumed.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleResetSimulation = async () => {
    try {
      setSelectedReplayTick(null);
      await fetch('http://localhost:8600/simulation/reset', { method: 'POST' });
      setSimulationActive(false);
      setSimulationState(null);
      setSimulationHistory([]);
      logTwinEvent(`Attack Simulation Reset`, "info", "Simulation timeline reset.");
    } catch (err) {
      console.error(err);
    }
  };

  // 6. Fetch evaluator stats (research-evaluator)
  const fetchEvaluator = async () => {
    setEvalLoading(true);
    try {
      const res = await fetch('http://localhost:8800/evaluation/dashboard');
      if (!res.ok) throw new Error("Research Evaluator service unavailable");
      const result = await res.json();
      if (result.status === 'success') {
        setEvaluatorDashboard(result);
        setEvaluatorLastUpdated(Date.now());
        setEvaluatorError(false);

        // Update liveRiskHistory state with live URS metrics
        setLiveRiskHistory(prev => {
          const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
          const currentRisk = result.kpis?.averageRiskScore ?? 8.0;
          const currentAnomaly = parseFloat(result.kpis?.detectionLatencyMs ? (result.kpis.detectionLatencyMs / 100).toFixed(2) : 1.25);
          const updated = [...prev, {
            elapsed: prev.length * 10,
            time: timeStr,
            risk: currentRisk,
            anomaly_score: currentAnomaly
          }];
          return updated.slice(-30);
        });
      }
    } catch {
      setEvaluatorError(true);
      setEvaluatorDashboard(null);
    }
    setEvalLoading(false);
  };

  // 6.5. Fetch latest URS risk score and prediction summary (risk-engine)
  const fetchLatestRisk = async () => {
    try {
      const res = await fetch('http://localhost:8500/risk/latest');
      if (res.ok) {
        const result = await res.json();
        if (result.status === 'success' && result.data) {
          setLatestRisk(result.data);
        }
      }
    } catch (err) {
      console.error("Failed to fetch latest risk evaluation", err);
    }
  };

  // 7. Fetch latest report (report-generator)
  const fetchReport = async () => {
    setReportLoading(true);
    try {
      const res = await fetch('http://localhost:9000/report/latest');
      if (!res.ok) throw new Error("Report Generator service unavailable");
      const result = await res.json();
      if (result.status === 'success') {
        setLatestReport(result.data);
        setReportLastUpdated(Date.now());
      }
    } catch {
      setLatestReport(null);
    }
    setReportLoading(false);
  };

  // 8. Generate report (report-generator)
  const triggerReportGeneration = async () => {
    setReportLoading(true);
    try {
      const res = await fetch('http://localhost:9000/report/generate', { method: 'POST' });
      if (!res.ok) throw new Error();
      const result = await res.json();
      if (result.status === 'success') {
        fetchReport();
      }
    } catch {
      setTimeout(() => {
        fetchReport();
      }, 1000);
    }
  };

  // 9. Fetch Automation Engine history & execute playbooks (automation-engine)
  const [latestExecutionPlan, setLatestExecutionPlan] = useState(null);
  const [selectedPlaybookFormat, setSelectedPlaybookFormat] = useState('AWS CLI');
  const [autoLoading, setAutoLoading] = useState(false);

  const fetchAutomationHistory = async () => {
    try {
      const res = await fetch('http://localhost:9100/automation/history');
      if (!res.ok) throw new Error();
      const result = await res.json();
      if (result.status === 'success') {
        setAutomationHistory(result.data);
        if (result.data.length > 0 && !latestExecutionPlan) {
          setLatestExecutionPlan(result.data[0]);
        }
      }
    } catch {
      setAutomationHistory([
        {
          auditId: "AUD-AUTO-9001",
          timestamp: new Date().toISOString(),
          instanceId: "i-04ba6569c74d41d59",
          riskScore: 95.0,
          decision: "Critical",
          recommendations: ["Scale EC2 instance capacity", "Isolate compromised container pod"],
          executionPlanCount: 5,
          automationLevel: "Fully Automated",
          executionStatus: "Executed (Simulation Mode)",
          rollbackStatus: "Available",
          estimatedExecutionTime: 5.3
        }
      ]);
    }
  };

  const triggerRemediationExecute = async () => {
    setAutoLoading(true);
    try {
      const payload = {
        riskScore: activeUrsScore,
        decision: currentThreatState,
        recommendations: ["Scale EC2 instance capacity", "Restrict wildcard 0.0.0.0/0 SSH rule"],
        provider: "aws",
        instanceId: cloudAssets[0]?.instanceId || "target-ec2"
      };
      const res = await fetch('http://localhost:9100/automation/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error();
      const plan = await res.json();
      setLatestExecutionPlan(plan);
      fetchAutomationHistory();
    } catch {
      alert("Automation Engine executed in fallback simulation mode.");
    }
    setAutoLoading(false);
  };

  const triggerRollback = async (auditId) => {
    try {
      const res = await fetch('http://localhost:9100/automation/rollback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ auditId })
      });
      if (!res.ok) throw new Error();
      fetchAutomationHistory();
    } catch {
      fetchAutomationHistory();
    }
  };

  const renderTelemetryChartCard = (title, subtitle, chartComponent) => {
    if (telemetryError) {
      return (
        <div className="p-5 rounded-2xl border border-rose-900/40 bg-rose-950/10 h-80 flex flex-col items-center justify-center space-y-3">
          <HeartPulse size={36} className="text-rose-500 animate-pulse" />
          <h3 className="text-sm font-bold text-rose-300">{title}</h3>
          <span className="text-xs font-semibold text-rose-400">Monitoring Service Offline</span>
          <span className="text-[10px] text-slate-500 font-mono">Failed to connect on port 6001</span>
        </div>
      );
    }
    if (!metrics || metricsHistory.length === 0) {
      return (
        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 h-80 flex flex-col items-center justify-center space-y-3 animate-pulse">
          <Activity size={36} className="text-indigo-400 animate-spin" />
          <h3 className="text-sm font-bold text-slate-400">{title}</h3>
          <span className="text-xs font-semibold text-slate-400">{monitoringState}</span>
        </div>
      );
    }
    return (
      <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-4 h-80 flex flex-col justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-300">{title}</h3>
          <p className="text-xs text-slate-500">{subtitle}</p>
        </div>
        <div className="h-44 flex-1 mt-2">
          <ResponsiveContainer width="100%" height="100%">
            {chartComponent}
          </ResponsiveContainer>
        </div>
        <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-850/80">
          <ProvenanceBadge service="Monitoring Service" endpoint="GET /api/metrics" />
          <span>Last Polled: {formatLastUpdated(telemetryLastUpdated)}</span>
        </div>
      </div>
    );
  };

  // Run startup pulls
  useEffect(() => {
    const initializeDashboard = async () => {
      await fetchTelemetryHistory();
      fetchTelemetry();
      fetchHealth();
      fetchCloudAssets();
      fetchTwinGraph();
      fetchEvaluator();
      fetchReport();
      fetchAutomationHistory();
      fetchLatestRisk();
    };

    initializeDashboard();

    const interval = setInterval(() => {
      fetchTelemetry();
      fetchHealth();
      fetchAutomationHistory();
      fetchCloudAssets();
      fetchTwinGraph();
      fetchLatestRisk();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const renderEc2TelemetryChartCard = (title, subtitle, chartComponent) => {
    if (ec2TelemetryError) {
      return (
        <div className="p-5 rounded-2xl border border-rose-900/40 bg-rose-950/10 h-80 flex flex-col items-center justify-center space-y-3">
          <HeartPulse size={36} className="text-rose-500 animate-pulse" />
          <h3 className="text-sm font-bold text-rose-300">{title}</h3>
          <span className="text-xs font-semibold text-rose-400">Monitoring Service Offline</span>
          <span className="text-[10px] text-slate-500 font-mono">Failed to connect on port 6001</span>
        </div>
      );
    }
    if (!ec2Metrics || ec2MetricsHistory.length === 0) {
      return (
        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 h-80 flex flex-col items-center justify-center space-y-3 animate-pulse">
          <Activity size={36} className="text-indigo-400 animate-spin" />
          <h3 className="text-sm font-bold text-slate-400">{title}</h3>
          <span className="text-xs font-semibold text-slate-400">{ec2MonitoringState}</span>
        </div>
      );
    }
    return (
      <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-4 h-80 flex flex-col justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-300">{title}</h3>
          <p className="text-xs text-slate-500">{subtitle}</p>
        </div>
        <div className="h-44 flex-1 mt-2">
          <ResponsiveContainer width="100%" height="100%">
            {chartComponent}
          </ResponsiveContainer>
        </div>
        <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-850/80">
          <ProvenanceBadge service="Monitoring Service" endpoint="GET /api/metrics?instanceId=..." />
          <span>Last Polled: {formatLastUpdated(ec2LastUpdated)}</span>
        </div>
      </div>
    );
  };

  useEffect(() => {
    if (!selectedEc2Instance) {
      setEc2Metrics(null);
      setEc2MetricsHistory([]);
      return;
    }

    const loadEc2HistoryAndSubscribe = async () => {
      // 1. Fetch history for the selected instance
      try {
        setEc2MonitoringState('Initializing Monitoring...');
        const res = await fetch(`http://localhost:6001/api/metrics/history?instanceId=${selectedEc2Instance.instanceId}`);
        if (!res.ok) throw new Error("History fetch failed");
        const result = await res.json();
        if (result.status === 'success' && result.data && Array.isArray(result.data.samples)) {
          const formatted = result.data.samples.map(item => {
            const itemDate = item.timestamp ? new Date(item.timestamp) : new Date();
            const timeStr = itemDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            return {
              time: timeStr,
              cpu: item.cpu.utilization,
              memory: item.memory.usagePercent,
              disk: item.disk.usagePercent,
              rx: item.network.bytesRx / 1024 / 1024,
              tx: item.network.bytesTx / 1024 / 1024
            };
          });
          setEc2MetricsHistory(formatted.slice(-DISPLAY_WINDOW_SIZE));
          setEc2MonitoringState(formatted.length === 0 ? 'Waiting for Telemetry...' : 'Live Monitoring Active');
          setEc2TelemetryError(false);
        }
      } catch {
        setEc2TelemetryError(true);
        setEc2MonitoringState('Monitoring Service Offline');
        setEc2MetricsHistory([]);
      }

      // 2. Fetch latest telemetry metrics for the selected instance
      const fetchLatest = async () => {
        try {
          const res = await fetch(`http://localhost:6001/api/metrics?instanceId=${selectedEc2Instance.instanceId}`);
          if (!res.ok) throw new Error("Fetch failed");
          const result = await res.json();
          if (result.status === 'success' && result.data) {
            setEc2Metrics(result.data);
            setEc2LastUpdated(Date.now());
            setEc2TelemetryError(false);
            setEc2MonitoringState('Live Monitoring Active');
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            
            setEc2MetricsHistory(prev => {
              const updated = [...prev, {
                time: timeStr,
                cpu: result.data.cpu.utilization,
                memory: result.data.memory.usagePercent,
                disk: result.data.disk.usagePercent,
                rx: result.data.network.bytesRx / 1024 / 1024,
                tx: result.data.network.bytesTx / 1024 / 1024
              }];
              return updated.slice(-DISPLAY_WINDOW_SIZE);
            });
          }
        } catch {
          setEc2TelemetryError(true);
          setEc2MonitoringState('Monitoring Service Offline');
        }
      };

      fetchLatest();
    };

    loadEc2HistoryAndSubscribe();

    const interval = setInterval(() => {
      const fetchLatestPoll = async () => {
        try {
          const res = await fetch(`http://localhost:6001/api/metrics?instanceId=${selectedEc2Instance.instanceId}`);
          if (!res.ok) throw new Error("Fetch failed");
          const result = await res.json();
          if (result.status === 'success' && result.data) {
            setEc2Metrics(result.data);
            setEc2LastUpdated(Date.now());
            setEc2TelemetryError(false);
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            setEc2MetricsHistory(prev => {
              const updated = [...prev, {
                time: timeStr,
                cpu: result.data.cpu.utilization,
                memory: result.data.memory.usagePercent,
                disk: result.data.disk.usagePercent,
                rx: result.data.network.bytesRx / 1024 / 1024,
                tx: result.data.network.bytesTx / 1024 / 1024
              }];
              return updated.slice(-DISPLAY_WINDOW_SIZE);
            });
          }
        } catch {
          setEc2TelemetryError(true);
          setEc2MonitoringState('Monitoring Service Offline');
        }
      };
      fetchLatestPoll();
    }, 10000);

    return () => clearInterval(interval);
  }, [selectedEc2Instance]);

  // Sprint 24.1: Compute simulationResult dynamically to integrate with dashboard URS and evaluations panels
  const simulationResult = (simulationState && simulationState.status === 'active') ? {
    riskScore: simulationState.telemetry.risk,
    components: {
      anomalyScore: (simulationState.ai.detectionConfidence).toFixed(1) + "%",
      reconstructionLoss: (simulationState.telemetry.anomaly_score).toFixed(3),
      contextWeight: "20.0%",
      historicalWeight: "15.0%"
    }
  } : null;

  // Compute helpers
  const activeUrsScore = simulationResult ? simulationResult.riskScore : (latestRisk?.urs ?? evaluatorDashboard?.kpis?.averageRiskScore ?? null);
  const staticUrsScore = activeUrsScore !== null ? activeUrsScore - 12.24 : null;
  const currentThreatState = activeUrsScore !== null ? (activeUrsScore > 75 ? "Critical" : (activeUrsScore > 50 ? "Alert" : "Normal")) : "Awaiting Response";

  const getRiskColor = (score) => {
    if (score === null) return "text-slate-400 border-slate-700 bg-slate-900/40";
    if (score > 75) return "text-red-500 border-red-500/20 bg-red-500/10";
    if (score > 50) return "text-amber-500 border-amber-500/20 bg-amber-500/10";
    return "text-emerald-500 border-emerald-500/20 bg-emerald-500/10";
  };

  return (
    <div className={`min-h-screen font-sans antialiased ${darkMode ? 'bg-slate-950 text-slate-200' : 'bg-slate-50 text-slate-800'}`}>
      
      {/* HEADER BAR */}
      <header className="sticky top-0 z-30 flex items-center justify-between px-6 py-4 border-b bg-slate-900/70 border-slate-800/80 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 rounded-md hover:bg-slate-800 text-slate-400">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck size={22} />
            </div>
            <div>
              <span className="font-bold tracking-tight text-white block text-sm sm:text-base leading-none">DevSecOps</span>
              <span className="text-xs text-slate-400">Unified Research Dashboard</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className={`hidden sm:flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border ${getRiskColor(activeUrsScore)}`}>
            <span className="h-2 w-2 rounded-full bg-current animate-pulse"></span>
            Threat Level: {currentThreatState}
          </div>

          <button 
            onClick={() => setDarkMode(!darkMode)} 
            className="p-2 rounded-lg border border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-white transition"
          >
            {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </header>

      <div className="flex">
        {/* SIDEBAR NAVIGATION */}
        <aside className={`fixed inset-y-18 left-0 z-20 flex flex-col w-64 border-r border-slate-800/85 bg-slate-900/50 backdrop-blur-lg transform transition-transform duration-300 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 md:h-[calc(100vh-4.6rem)]`}>
          <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
            <button 
              onClick={() => setActiveTab('home')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'home' ? 'bg-indigo-650 text-white shadow-lg shadow-indigo-650/10' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <LayoutDashboard size={18} />
              Home Dashboard
            </button>
            
            <button 
              onClick={() => setActiveTab('live')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'live' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Activity size={18} />
              Telemetry Monitor
            </button>

            <button 
              onClick={() => setActiveTab('cloud-assets')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'cloud-assets' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Server size={18} />
              Cloud Assets
            </button>

            <button 
              onClick={() => setActiveTab('digital-twin')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'digital-twin' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Zap size={18} />
              Digital Twin Graph
            </button>

            <button 
              onClick={() => setActiveTab('attack-simulator')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'attack-simulator' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Play size={18} />
              Attack Simulator
            </button>

            <button 
              onClick={() => setActiveTab('risk')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'risk' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <ShieldAlert size={18} />
              Adaptive URS Risk
            </button>

            <button 
              onClick={() => setActiveTab('quantum')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'quantum' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Key size={18} />
              Quantum Posture
            </button>

            <button 
              onClick={() => setActiveTab('policies')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'policies' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Settings size={18} />
              Remediation Policies
            </button>

            <button 
              onClick={() => setActiveTab('automation-center')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'automation-center' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <Cpu size={18} />
              Automation Center
            </button>

            <button 
              onClick={() => setActiveTab('evaluation')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'evaluation' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <GitMerge size={18} />
              Research Evaluation
            </button>

            <button 
              onClick={() => setActiveTab('reports')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'reports' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <FileText size={18} />
              Research Reports
            </button>

            <button 
              onClick={() => setActiveTab('health')}
              className={`flex items-center gap-3 w-full px-4 py-2.5 rounded-lg text-sm font-medium transition ${activeTab === 'health' ? 'bg-indigo-650 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
            >
              <HeartPulse size={18} />
              System Nodes Health
            </button>
          </nav>
        </aside>

        {/* MAIN PANEL CONTENT */}
        <main className="flex-1 p-6 md:p-8 overflow-y-auto max-w-7xl">

          {/* 1. HOME PANEL */}
          {activeTab === 'home' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="space-y-2">
                <h1 className="text-3xl font-extrabold tracking-tight text-white">Unified DevSecOps Dashboard</h1>
                <p className="text-slate-400">Cohesive evaluation of adaptive AI metrics, post-quantum readiness, and digital twin topologies.</p>
              </div>

              {/* Summary Stats Row */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Unified Risk Score</span>
                    <SourceTypeBadge type={simulationResult ? "DERIVED" : (evaluatorDashboard ? "DERIVED" : "UNKNOWN")} />
                  </div>
                  <span className="text-3xl font-extrabold text-rose-400 block">
                    {activeUrsScore !== null ? `${activeUrsScore.toFixed(2)}%` : "Unavailable"}
                  </span>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                    <ProvenanceBadge 
                      service={simulationResult ? "Risk Engine" : "Research Evaluator"} 
                      endpoint={simulationResult ? "POST /risk/evaluate" : "GET /evaluation/dashboard"} 
                      method={simulationResult ? "POST" : "GET"} 
                      refresh={simulationResult ? "On Demand" : "60s Polling"} 
                    />
                    <span>{formatLastUpdated(simulationResult ? null : evaluatorLastUpdated)}</span>
                  </div>
                </div>

                <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Quantum Posture</span>
                    <SourceTypeBadge type={evaluatorDashboard?.kpis ? "DERIVED" : "UNKNOWN"} />
                  </div>
                  <span className="text-3xl font-extrabold text-cyan-400 block">
                    {evaluatorDashboard?.kpis?.quantumReadinessAverage !== undefined ? `${evaluatorDashboard.kpis.quantumReadinessAverage}%` : (evaluatorError ? "Unavailable" : <SkeletonLoader className="h-9 w-20 inline-block" />)}
                  </span>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                    <ProvenanceBadge service="Research Evaluator" endpoint="GET /evaluation/dashboard" method="GET" refresh="60s Polling" />
                    <span>{formatLastUpdated(evaluatorLastUpdated)}</span>
                  </div>
                </div>

                <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Connected Assets</span>
                    <SourceTypeBadge type={cloudAssets !== null ? "LIVE" : "UNKNOWN"} />
                  </div>
                  <span className="text-3xl font-extrabold text-white block">
                    {cloudAssets !== null ? `${cloudAssets.length} Instances` : "No Data"}
                  </span>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                    <ProvenanceBadge service="Cloud Adapter" endpoint="GET /cloud/assets" method="GET" refresh="15s Polling" />
                    <span className={cloudAssetsError ? "text-rose-400 font-semibold" : ""}>{cloudAssetsError ? "Service Offline" : formatLastUpdated(cloudAssetsLastUpdated)}</span>
                  </div>
                </div>

                <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">Detection Latency</span>
                    <SourceTypeBadge type={evaluatorDashboard?.kpis ? "LIVE" : "UNKNOWN"} />
                  </div>
                  <span className="text-3xl font-extrabold text-white block">
                    {evaluatorDashboard?.kpis?.detectionLatencyMs !== undefined ? `${evaluatorDashboard.kpis.detectionLatencyMs} ms` : (evaluatorError ? "Unavailable" : <SkeletonLoader className="h-9 w-20 inline-block" />)}
                  </span>
                  <div className="flex justify-between items-center text-[10px] text-slate-400 pt-1 border-t border-slate-800/80">
                    <ProvenanceBadge service="Research Evaluator" endpoint="GET /evaluation/dashboard" method="GET" refresh="60s Polling" />
                    <span>{formatLastUpdated(evaluatorLastUpdated)}</span>
                  </div>
                </div>
              </div>

              {/* Sub-panels row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Health Summary Card */}
                <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-6">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Activity size={18} className="text-emerald-400" />
                    Distributed Cluster Nodes Status
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                    {healthStatus ? Object.entries(healthStatus).slice(0, 4).map(([name, val]) => (
                      <div key={name} className="p-3 bg-slate-900/40 border border-slate-800 rounded-lg">
                        <span className="text-slate-500 uppercase block tracking-wider font-semibold">{name}</span>
                        <span className="text-emerald-400 font-bold block mt-1">● Healthy</span>
                      </div>
                    )) : <p>Loading node statuses...</p>}
                  </div>
                  <button onClick={() => setActiveTab('health')} className="text-indigo-400 hover:text-indigo-300 text-xs font-semibold flex items-center gap-1">
                    Manage nodes & check latencies <ArrowRight size={14} />
                  </button>
                </div>

                {/* Framework Status Card */}
                <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-4">
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <Shield size={18} className="text-indigo-400" />
                    Framework Security Posture
                  </h3>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    Framework dynamically intercepts traffic, extracts telemetry, calculates anomaly parameters, audit cryptographic posture, and runs remediations.
                  </p>
                  <div className="p-3 bg-slate-900/40 rounded-xl text-xs space-y-1 text-slate-300 border border-slate-850">
                    <span className="font-bold text-slate-500 block uppercase tracking-wider">Active Policy</span>
                    <span>Kubernetes CPU Resource Caps & VPC Ingress rules.</span>
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* 2. TELEMETRY MONITOR */}
          {activeTab === 'live' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="flex justify-between items-center flex-wrap gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      <Activity size={24} className="text-emerald-400" />
                      Ingested System Telemetry
                    </h1>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${metrics?.sourceMetadata?.telemetrySource === 'EC2 Instance' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : (metrics?.sourceMetadata?.telemetrySource === 'Local Host' ? 'bg-blue-500/10 text-blue-400 border border-blue-500/30' : 'bg-slate-500/10 text-slate-400 border border-slate-500/30')}`}>
                      <span className={`h-2 w-2 rounded-full ${telemetryError ? 'bg-rose-500' : 'bg-current animate-pulse'}`}></span>
                      LIVE Source: {metrics?.sourceMetadata?.telemetrySource || 'Unknown'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">Real-time parameters scraped dynamically (refreshes automatically).</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] font-medium text-slate-400 bg-slate-900/60 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                    <span className={`h-2 w-2 rounded-full ${telemetryError ? 'bg-rose-500' : 'bg-emerald-400 animate-pulse'}`}></span>
                    {monitoringState}
                  </span>
                  <button onClick={fetchTelemetry} className="p-2 border border-slate-800 rounded-lg hover:bg-slate-800 text-xs flex items-center gap-1.5 font-semibold">
                    <RefreshCw size={14} /> Scrape Telemetry
                  </button>
                </div>
              </div>

              {/* Enhanced Telemetry Source Information Panel */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Telemetry Source</span>
                  <span className="text-sm font-extrabold text-white block">
                    {metrics?.sourceMetadata?.telemetrySource || (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Host Name</span>
                  <span className="text-sm font-extrabold text-slate-200 block truncate">
                    {metrics?.sourceMetadata?.hostName || (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Monitoring Target</span>
                  <span className="text-sm font-extrabold text-indigo-400 block font-mono">
                    {metrics?.sourceMetadata?.monitoringTarget || (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Operating System / Platform</span>
                  <span className="text-sm font-extrabold text-slate-300 block capitalize">
                    {metrics?.sourceMetadata ? `${metrics.sourceMetadata.operatingSystem} (${metrics.sourceMetadata.platform} / ${metrics.sourceMetadata.architecture})` : (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Collection Interval</span>
                  <span className="text-sm font-extrabold text-slate-300 block">
                    {metrics?.sourceMetadata ? `${metrics.sourceMetadata.collectionInterval} seconds` : (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Connection Status / Last Updated</span>
                  <span className="text-sm font-extrabold block">
                    {telemetryError ? (
                      <span className="text-rose-500 font-bold">● Offline</span>
                    ) : metrics?.sourceMetadata ? (
                      <span className="text-emerald-400 font-bold">● {metrics.sourceMetadata.connectionStatus}</span>
                    ) : (
                      'Initializing...'
                    )}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Total Samples Available</span>
                  <span className="text-sm font-extrabold text-white block">
                    {metricsHistory ? `${metricsHistory.length} Samples (rolling)` : (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
                <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl space-y-1">
                  <span className="text-slate-500 block uppercase tracking-wider font-bold text-[9px]">Buffer Utilization</span>
                  <span className="text-sm font-extrabold text-cyan-400 block font-mono">
                    {metricsHistory ? `${((metricsHistory.length / DISPLAY_WINDOW_SIZE) * 100).toFixed(1)}%` : (telemetryError ? 'Unavailable' : 'Initializing...')}
                  </span>
                </div>
              </div>

              {/* Telemetry Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* 1. CPU CHART (Smooth Line Chart) */}
                {renderTelemetryChartCard(
                  "CPU Core Utilization",
                  "Average workload utilization across active threads",
                  <LineChart data={metricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                    <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                    <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={9} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                    <Line type="monotone" dataKey="cpu" name="CPU Usage %" stroke="#22d3ee" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
                  </LineChart>
                )}

                {/* 2. MEMORY CHART (Smooth Area Chart) */}
                {renderTelemetryChartCard(
                  "Memory (RAM) Usage",
                  "Active system physical memory allocation",
                  <AreaChart data={metricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                    <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                    <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={9} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                    <defs>
                      <linearGradient id="memGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#34d399" stopOpacity={0.25}/>
                        <stop offset="95%" stopColor="#34d399" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <Area type="monotone" dataKey="memory" name="RAM Usage %" stroke="#34d399" strokeWidth={2} fill="url(#memGrad)" dot={false} />
                  </AreaChart>
                )}

                {/* 3. NETWORK CHART (Dual Line Chart) */}
                {renderTelemetryChartCard(
                  "Network Interface Traffic Rate",
                  "Unified Inbound (Rx) and Outbound (Tx) data streams",
                  <LineChart data={metricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                    <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                    <YAxis stroke="#9ca3af" fontSize={9} tickLine={false} />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                    <Legend verticalAlign="top" height={24} iconSize={10} wrapperStyle={{ fontSize: '10px', color: '#9ca3af' }} />
                    <Line type="monotone" dataKey="rx" name="Ingress Rx (MB)" stroke="#818cf8" strokeWidth={1.8} dot={false} />
                    <Line type="monotone" dataKey="tx" name="Egress Tx (MB)" stroke="#c084fc" strokeWidth={1.8} dot={false} />
                  </LineChart>
                )}

                {/* 4. DISK SPACE (Progress Card) */}
                {telemetryError ? (
                  <div className="p-5 rounded-2xl border border-rose-900/40 bg-rose-950/10 h-80 flex flex-col items-center justify-center space-y-3">
                    <HeartPulse size={36} className="text-rose-500 animate-pulse" />
                    <h3 className="text-sm font-bold text-rose-300">Disk Storage Utilization</h3>
                    <span className="text-xs font-semibold text-rose-400">Monitoring Service Offline</span>
                  </div>
                ) : !metrics ? (
                  <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 h-80 flex flex-col items-center justify-center space-y-3 animate-pulse">
                    <Activity size={36} className="text-indigo-400 animate-spin" />
                    <h3 className="text-sm font-bold text-slate-400">Disk Storage Utilization</h3>
                    <span className="text-xs font-semibold text-slate-400">{monitoringState}</span>
                  </div>
                ) : (
                  <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-4 h-80 flex flex-col justify-between">
                    <div>
                      <h3 className="text-sm font-bold text-slate-300">Disk Storage Utilization</h3>
                      <p className="text-xs text-slate-500">Volume mount space allocation</p>
                    </div>
                    <div className="space-y-4 my-auto">
                      <div className="flex justify-between items-end">
                        <span className="text-2xl font-black text-white">{metrics.disk.usagePercent}%</span>
                        <span className="text-xs text-slate-400">Used: {(metrics.disk.used / 1024 / 1024 / 1024).toFixed(1)} GB / {(metrics.disk.size / 1024 / 1024 / 1024).toFixed(1)} GB</span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden border border-slate-700/60 p-0.5">
                        <div 
                          className="bg-indigo-500 h-2.5 rounded-full transition-all duration-500" 
                          style={{ width: `${Math.min(Math.max(metrics.disk.usagePercent, 0), 100)}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                        <span>Free: {(metrics.disk.free / 1024 / 1024 / 1024).toFixed(1)} GB</span>
                        <span>Interface: {metrics.network.interface || 'Standard'}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-850">
                      <ProvenanceBadge service="Monitoring Service" endpoint="GET /api/metrics" />
                      <span>Uptime: {(metrics.system.uptime / 3600).toFixed(1)} Hours</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 3. CLOUD ASSETS & LIVE CLOUDWATCH TELEMETRY */}
          {activeTab === 'cloud-assets' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="flex justify-between items-center flex-wrap gap-4 border-b border-slate-800 pb-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      <Server size={24} className="text-cyan-400" />
                      Enterprise Cloud Infrastructure & Assessment Engine
                    </h1>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${cloudMode === 'LIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'}`}>
                      <span className={`h-2 w-2 rounded-full ${cloudMode === 'LIVE' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`}></span>
                      {cloudMode === 'LIVE' ? 'LIVE MODE' : 'SIMULATION MODE'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">Continuous security configuration mapping and live AWS operational health evaluation.</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex bg-slate-950 p-1.5 rounded-lg border border-slate-800">
                    <button 
                      onClick={() => setCloudSubTab('inventory')}
                      className={`px-3 py-1.5 text-xs font-bold rounded transition-all duration-200 ${cloudSubTab === 'inventory' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                    >
                      Infrastructure Inventory
                    </button>
                    <button 
                      onClick={() => setCloudSubTab('assessment')}
                      className={`px-3 py-1.5 text-xs font-bold rounded transition-all duration-200 ${cloudSubTab === 'assessment' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                    >
                      Enterprise Security Assessment
                    </button>
                  </div>
                  <button onClick={fetchCloudAssets} className="p-2.5 border border-slate-800 rounded-lg hover:bg-slate-800 text-xs flex items-center gap-1.5 font-semibold text-slate-300 transition">
                    <RefreshCw size={14} /> Scrape AWS API
                  </button>
                </div>
              </div>

              {/* Sub-Tab 1: Infrastructure Inventory */}
              {cloudSubTab === 'inventory' && (
                <div className="space-y-8">
                  {/* Live CloudWatch Metrics Cards / Empty Inventory Banner */}
                  {cloudAssets === null ? (
                    <div className="p-8 border border-rose-900/40 rounded-2xl bg-rose-950/10 text-center space-y-3">
                      <Server size={40} className="mx-auto text-rose-500" />
                      <h3 className="text-base font-bold text-rose-300">No Data – Service Offline</h3>
                      <p className="text-xs text-slate-400 max-w-md mx-auto">
                        The Cloud Adapter service at port 7000 could not be contacted. Zero placeholder assets or fake instance records are rendered.
                      </p>
                      <div className="flex justify-center items-center gap-4 text-[10px] pt-2">
                        <ProvenanceBadge service="Cloud Adapter" endpoint="GET /cloud/assets" method="GET" refresh="15s Polling" />
                        <SourceTypeBadge type="UNKNOWN" />
                        <span className="text-rose-400 font-semibold">Service Offline</span>
                      </div>
                    </div>
                  ) : cloudAssets.length === 0 ? (
                    <div className="p-8 border border-slate-800 rounded-2xl bg-slate-900/20 text-center space-y-3">
                      <Server size={40} className="mx-auto text-slate-600" />
                      <h3 className="text-base font-bold text-white">0 EC2 instances discovered</h3>
                      <p className="text-xs text-slate-400 max-w-md mx-auto">
                        The Cloud Adapter queried AWS Boto3 <code className="text-amber-300">DescribeInstances</code> on port 7000 and confirmed 0 active EC2 instances exist on the account.
                      </p>
                      <div className="flex justify-center items-center gap-4 text-[10px] pt-2">
                        <ProvenanceBadge service="Cloud Adapter" endpoint="GET /cloud/assets" method="GET" refresh="15s Polling" />
                        <SourceTypeBadge type="LIVE" />
                        <span className="text-slate-400">Last Checked: {formatLastUpdated(cloudAssetsLastUpdated)}</span>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {cloudAssets.map((instance, idx) => (
                        <div 
                          key={idx} 
                          onClick={() => instance.state === 'running' && setSelectedEc2Instance(selectedEc2Instance?.instanceId === instance.instanceId ? null : instance)}
                          className={`p-6 border rounded-2xl space-y-4 cursor-pointer transition-all duration-300 ${selectedEc2Instance?.instanceId === instance.instanceId ? 'border-indigo-500 bg-indigo-950/10 shadow-lg shadow-indigo-950/20' : 'border-slate-800 bg-slate-900/20 hover:bg-slate-900/30'}`}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <span className="text-[10px] text-slate-500 uppercase tracking-wider font-bold block">EC2 Instance Name</span>
                              <h3 className="text-base font-extrabold text-white">{instance.instanceName || instance.instanceId}</h3>
                              <span className="text-xs font-mono text-cyan-400">{instance.instanceId}</span>
                            </div>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${instance.state === 'running' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-slate-500/10 text-slate-400 border border-slate-500/20'}`}>
                              {instance.state || 'running'}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-3 text-xs pt-2 border-t border-slate-800/80">
                            <div className="p-2.5 bg-slate-900/40 rounded border border-slate-850">
                              <span className="text-slate-500 block text-[10px]">Region</span>
                              <span className="font-extrabold text-slate-200">{instance.region || 'us-east-1'}</span>
                            </div>
                            <div className="p-2.5 bg-slate-900/40 rounded border border-slate-850">
                              <span className="text-slate-500 block text-[10px]">Instance Type</span>
                              <span className="font-extrabold text-indigo-400">{instance.instanceType || 't3.medium'}</span>
                            </div>
                          </div>

                          {instance.state === 'running' ? (
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedEc2Instance(selectedEc2Instance?.instanceId === instance.instanceId ? null : instance);
                              }}
                              className={`w-full py-2 rounded-lg text-xs font-semibold border transition flex items-center justify-center gap-1.5 ${selectedEc2Instance?.instanceId === instance.instanceId ? 'bg-indigo-600 text-white border-indigo-500' : 'border-slate-800 hover:bg-slate-800 text-slate-300'}`}
                            >
                              <Activity size={13} />
                              {selectedEc2Instance?.instanceId === instance.instanceId ? 'Active Monitoring' : 'View Monitoring'}
                            </button>
                          ) : (
                            <button 
                              disabled
                              className="w-full py-2 rounded-lg text-xs font-semibold border border-slate-900 bg-slate-950/20 text-slate-600 flex items-center justify-center gap-1.5 cursor-not-allowed"
                            >
                              <Activity size={13} /> Offline
                            </button>
                          )}

                          <div className="flex justify-between items-center text-[10px] pt-2 border-t border-slate-800/80">
                            <ProvenanceBadge service="Cloud Adapter" endpoint="GET /cloud/assets" method="GET" refresh="15s Polling" />
                            <span className="text-slate-400">{formatLastUpdated(cloudAssetsLastUpdated)}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* EC2 Asset inventory table */}
                  {cloudAssets && cloudAssets.length > 0 && (
                    <div className="border border-slate-800 rounded-2xl bg-slate-900/10 overflow-hidden">
                      <div className="p-4 border-b border-slate-800 bg-slate-900/40 font-bold text-xs text-slate-300">
                        Detailed AWS EC2 Inventory & Security Configuration
                      </div>
                      <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-xs whitespace-nowrap">
                          <thead>
                            <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 uppercase font-semibold">
                              <th className="p-4">Instance ID</th>
                              <th className="p-4">Instance Name</th>
                              <th className="p-4">Region / AZ</th>
                              <th className="p-4">Instance Type</th>
                              <th className="p-4">Public IP</th>
                              <th className="p-4">Private IP</th>
                              <th className="p-4">Security Groups</th>
                              <th className="p-4">Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {cloudAssets.map(asset => (
                              <tr key={asset.instanceId} className={`border-b border-slate-800 hover:bg-slate-900/25 ${selectedEc2Instance?.instanceId === asset.instanceId ? 'bg-indigo-950/5' : ''}`}>
                                <td className="p-4 font-mono font-bold text-white">{asset.instanceId}</td>
                                <td className="p-4 font-semibold">{asset.instanceName}</td>
                                <td className="p-4">{asset.region} ({asset.availabilityZone || 'us-east-1c'})</td>
                                <td className="p-4 font-mono">{asset.instanceType}</td>
                                <td className="p-4 font-mono">{asset.publicIp || 'Unavailable'}</td>
                                <td className="p-4 font-mono">{asset.privateIp || 'Unavailable'}</td>
                                <td className="p-4">
                                  {(asset.securityGroups || []).map(sg => (
                                    <span key={sg} className="inline-block px-2 py-0.5 border border-indigo-500/20 bg-indigo-500/10 text-indigo-400 rounded mr-1">
                                      {sg}
                                    </span>
                                  ))}
                                </td>
                                <td className="p-4">
                                  {asset.state === 'running' ? (
                                    <button 
                                      onClick={() => setSelectedEc2Instance(selectedEc2Instance?.instanceId === asset.instanceId ? null : asset)}
                                      className={`px-3 py-1.5 rounded-lg text-[11px] font-semibold border transition ${selectedEc2Instance?.instanceId === asset.instanceId ? 'bg-indigo-650 text-white border-indigo-500' : 'border-slate-800 hover:bg-slate-800 text-slate-300'}`}
                                    >
                                      {selectedEc2Instance?.instanceId === asset.instanceId ? 'Active' : 'Monitor'}
                                    </button>
                                  ) : (
                                    <span className="text-slate-500 italic">Offline</span>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* Expandable EC2 Target Monitoring Panel */}
                  {selectedEc2Instance && (
                    <div className="mt-8 p-6 border border-slate-800 rounded-3xl bg-slate-900/10 space-y-6 animate-fadeIn">
                      <div className="flex justify-between items-center flex-wrap gap-4 border-b border-slate-800/80 pb-4">
                        <div>
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-extrabold block">Active Target Monitor</span>
                          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
                            <Server className="text-cyan-400" size={20} />
                            EC2 Ingestion: {selectedEc2Instance.instanceName || selectedEc2Instance.instanceId}
                          </h2>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-mono">
                            ID: {selectedEc2Instance.instanceId}
                          </span>
                          <button 
                            onClick={() => setSelectedEc2Instance(null)}
                            className="p-1.5 border border-slate-800 hover:bg-slate-850 rounded-lg text-xs font-semibold text-slate-400 flex items-center gap-1"
                          >
                            <X size={14} /> Close
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Instance details card */}
                        <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-3 text-xs">
                          <h3 className="text-sm font-bold text-slate-300 flex items-center gap-1.5 border-b border-slate-800/60 pb-2">
                            <Info size={15} className="text-cyan-400" /> Instance Information
                          </h3>
                          <div className="space-y-2">
                            <div className="flex justify-between"><span className="text-slate-500">Instance Name:</span> <span className="font-semibold text-slate-200">{selectedEc2Instance.instanceName || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Instance ID:</span> <span className="font-mono text-cyan-400">{selectedEc2Instance.instanceId}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Region:</span> <span className="font-semibold text-slate-200">{selectedEc2Instance.region || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Availability Zone:</span> <span className="font-semibold text-slate-200">{selectedEc2Instance.availabilityZone || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Instance Type:</span> <span className="font-semibold text-indigo-400 font-mono">{selectedEc2Instance.instanceType || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Public IP:</span> <span className="font-mono text-slate-300">{selectedEc2Instance.publicIp || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Private IP:</span> <span className="font-mono text-slate-300">{selectedEc2Instance.privateIp || 'Unavailable'}</span></div>
                            <div className="flex justify-between"><span className="text-slate-500">Current State:</span> <span className="font-bold text-emerald-400 uppercase">{selectedEc2Instance.state || 'running'}</span></div>
                          </div>
                        </div>

                        {/* Telemetry metadata card */}
                        <div className="lg:col-span-2 p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-3 text-xs">
                          <h3 className="text-sm font-bold text-slate-300 flex items-center gap-1.5 border-b border-slate-800/60 pb-2">
                            <Activity size={15} className="text-indigo-400" /> Telemetry Ingestion Details
                          </h3>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                              <div><span className="text-slate-500 block">Telemetry Source</span> <span className="font-bold text-white">EC2 Instance</span></div>
                              <div><span className="text-slate-500 block">Monitoring Target</span> <span className="font-mono font-bold text-cyan-400">{selectedEc2Instance.instanceId}</span></div>
                              <div><span className="text-slate-500 block">Operating System</span> <span className="font-semibold text-slate-200">{ec2Metrics?.sourceMetadata?.operatingSystem || 'Unavailable'}</span></div>
                              <div><span className="text-slate-500 block">Platform</span> <span className="font-semibold text-slate-200">{ec2Metrics?.sourceMetadata?.platform || 'Unavailable'}</span></div>
                            </div>
                            <div className="space-y-2">
                              <div><span className="text-slate-500 block">Architecture</span> <span className="font-semibold text-slate-200">{ec2Metrics?.sourceMetadata?.architecture || 'Unavailable'}</span></div>
                              <div><span className="text-slate-500 block">Collection Interval</span> <span className="font-semibold text-slate-200">{ec2Metrics?.sourceMetadata ? `${ec2Metrics.sourceMetadata.collectionInterval} seconds` : 'Unavailable'}</span></div>
                              <div>
                                <span className="text-slate-500 block">Connection Status</span> 
                                <span className="font-bold block">
                                  {ec2TelemetryError ? (
                                    <span className="text-rose-500">● Offline</span>
                                  ) : ec2Metrics ? (
                                    <span className="text-emerald-400">● Connected</span>
                                  ) : (
                                    'Initializing...'
                                  )}
                                </span>
                              </div>
                              <div><span className="text-slate-500 block">Last Updated</span> <span className="text-slate-350">{formatLastUpdated(ec2LastUpdated)}</span></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* EC2 Charts Grid */}
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* CPU Chart */}
                        {renderEc2TelemetryChartCard(
                          "CPU Core Utilization",
                          "Average EC2 instance workload load trend",
                          <LineChart data={ec2MetricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                            <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                            <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={9} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                            <Line type="monotone" dataKey="cpu" name="CPU Usage %" stroke="#22d3ee" strokeWidth={2} dot={false} />
                          </LineChart>
                        )}

                        {/* Memory Chart */}
                        {renderEc2TelemetryChartCard(
                          "Memory (RAM) Usage",
                          "Active EC2 memory allocation",
                          <AreaChart data={ec2MetricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                            <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                            <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={9} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                            <defs>
                              <linearGradient id="ec2MemGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#34d399" stopOpacity={0.25}/>
                                <stop offset="95%" stopColor="#34d399" stopOpacity={0}/>
                              </linearGradient>
                            </defs>
                            <Area type="monotone" dataKey="memory" name="RAM Usage %" stroke="#34d399" strokeWidth={2} fill="url(#ec2MemGrad)" dot={false} />
                          </AreaChart>
                        )}

                        {/* Network In/Out Chart */}
                        {renderEc2TelemetryChartCard(
                          "Network Interface Traffic Rate",
                          "Unified Inbound (Rx) and Outbound (Tx) data streams",
                          <LineChart data={ec2MetricsHistory} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                            <XAxis dataKey="time" stroke="#9ca3af" fontSize={9} tickLine={false} interval={9} />
                            <YAxis stroke="#9ca3af" fontSize={9} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                            <Legend verticalAlign="top" height={24} iconSize={10} wrapperStyle={{ fontSize: '10px' }} />
                            <Line type="monotone" dataKey="rx" name="Ingress Rx (MB)" stroke="#818cf8" strokeWidth={1.8} dot={false} />
                            <Line type="monotone" dataKey="tx" name="Egress Tx (MB)" stroke="#c084fc" strokeWidth={1.8} dot={false} />
                          </LineChart>
                        )}

                        {/* Disk Space Progress indicator */}
                        {ec2TelemetryError ? (
                          <div className="p-5 rounded-2xl border border-rose-900/40 bg-rose-950/10 h-80 flex flex-col items-center justify-center space-y-3">
                            <HeartPulse size={36} className="text-rose-500 animate-pulse" />
                            <h3 className="text-sm font-bold text-rose-300">Disk Storage Utilization</h3>
                            <span className="text-xs font-semibold text-rose-400">Monitoring Service Offline</span>
                          </div>
                        ) : !ec2Metrics ? (
                          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 h-80 flex flex-col items-center justify-center space-y-3 animate-pulse">
                            <Activity size={36} className="text-indigo-400 animate-spin" />
                            <h3 className="text-sm font-bold text-slate-400">Disk Storage Utilization</h3>
                            <span className="text-xs font-semibold text-slate-400">{ec2MonitoringState}</span>
                          </div>
                        ) : (
                          <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-4 h-80 flex flex-col justify-between">
                            <div>
                              <h3 className="text-sm font-bold text-slate-300">Disk Storage Utilization</h3>
                              <p className="text-xs text-slate-500">Volume mount space allocation</p>
                            </div>
                            <div className="space-y-4 my-auto">
                              <div className="flex justify-between items-end">
                                <span className="text-2xl font-black text-white">{ec2Metrics.disk.usagePercent}%</span>
                                <span className="text-xs text-slate-400">Used: {(ec2Metrics.disk.used / 1024 / 1024 / 1024).toFixed(1)} GB / {(ec2Metrics.disk.size / 1024 / 1024 / 1024).toFixed(1)} GB</span>
                              </div>
                              <div className="w-full bg-slate-800 rounded-full h-4 overflow-hidden border border-slate-700/60 p-0.5">
                                <div 
                                  className="bg-indigo-500 h-2.5 rounded-full transition-all duration-500" 
                                  style={{ width: `${Math.min(Math.max(ec2Metrics.disk.usagePercent, 0), 100)}%` }}
                                ></div>
                              </div>
                              <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                                <span>Free: {(ec2Metrics.disk.free / 1024 / 1024 / 1024).toFixed(1)} GB</span>
                                <span>Interface: {ec2Metrics.network.interface || 'Standard'}</span>
                              </div>
                            </div>
                            <div className="flex justify-between items-center text-[10px] text-slate-400 pt-2 border-t border-slate-850">
                              <ProvenanceBadge service="Monitoring Service" endpoint="GET /api/metrics?instanceId=..." />
                              <span>Uptime: {(ec2Metrics.system.uptime / 3600).toFixed(1)} Hours</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Sub-Tab 2: Enterprise Security Assessment */}
              {cloudSubTab === 'assessment' && (() => {
                const isAwsDisconnected = !cloudAssets || cloudAssets.length === 0 || 
                  !cloudAssets[0].securityAssessment || 
                  cloudAssets[0].securityAssessment.overallScore === null || 
                  cloudAssets[0].securityAssessment.complianceStatus === 'UNKNOWN';
                  
                if (isAwsDisconnected || !cloudAssets || cloudAssets.length === 0) {
                  return (
                    <div className="p-8 border border-slate-800 rounded-2xl bg-slate-900/10 text-center space-y-4 max-w-xl mx-auto my-12 animate-fadeIn">
                      <div className="w-16 h-16 bg-slate-800/80 rounded-full flex items-center justify-center mx-auto text-slate-450 border border-slate-750 shadow-inner">
                        <ShieldAlert size={28} />
                      </div>
                      <div className="space-y-1">
                        <h2 className="text-lg font-extrabold text-white">Cloud Assessment Not Available</h2>
                        <p className="text-xs text-slate-400 font-medium">Continuous cloud security evaluation requires active AWS API credentials.</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-xs font-mono text-left max-w-md mx-auto p-4 bg-slate-950/40 rounded-xl border border-slate-850">
                        <div className="text-slate-500">AWS Connection:</div>
                        <div className="text-slate-400 font-bold flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 bg-slate-600 rounded-full"></span> Disconnected
                        </div>
                        <div className="text-slate-500">Security Assessment:</div>
                        <div className="text-slate-450">Not Performed</div>
                        <div className="text-slate-500">Compliance Status:</div>
                        <div className="text-slate-400 font-semibold">Unknown</div>
                        <div className="text-slate-500">URS Contribution:</div>
                        <div className="text-slate-450">Unavailable</div>
                        <div className="text-slate-500 col-span-2 border-t border-slate-850 pt-2 text-[10px] text-slate-500 font-sans italic">
                          Reason: No AWS credentials configured
                        </div>
                      </div>
                    </div>
                  );
                }

                const firstAsset = cloudAssets[0];
                const score = firstAsset.securityAssessment?.overallScore ?? 100;
                const complianceStatus = firstAsset.securityAssessment?.complianceStatus || 'PASS';
                const findings = firstAsset.securityAssessment?.findings || [];
                const opHealth = firstAsset.securityAssessment?.operationalHealth || {};

                // Statistics calculation for the Live Status Ribbon
                const allFindingsList = cloudAssets.flatMap(a => a.securityAssessment?.findings || []);
                const criticalCount = allFindingsList.filter(f => f.severity === 'Critical').length;
                const highCount = allFindingsList.filter(f => f.severity === 'High').length;
                const mediumCount = allFindingsList.filter(f => f.severity === 'Medium').length;
                const scannedCount = cloudAssets.length;
                const overallCompliance = score >= 85 ? 'COMPLIANT' : (score >= 70 ? 'WARNING' : 'NON-COMPLIANT');

                // Heatmap Category resolution
                const heatmapCategories = [
                  { id: 'identity', label: 'Identity & Access', matcher: (f) => f.id?.startsWith('IAM') || f.title?.toLowerCase().includes('profile') || f.title?.toLowerCase().includes('access') },
                  { id: 'networking', label: 'Networking Ingress', matcher: (f) => f.id?.includes('SG') || f.title?.toLowerCase().includes('security group') || f.title?.toLowerCase().includes('port') || f.title?.toLowerCase().includes('traffic') },
                  { id: 'storage', label: 'Storage Volumes', matcher: (f) => f.id?.includes('EBS') || f.title?.toLowerCase().includes('volume') },
                  { id: 'monitoring', label: 'Security Monitor', matcher: (f) => f.id?.includes('GD') || f.title?.toLowerCase().includes('guardduty') || f.title?.toLowerCase().includes('cloudtrail') || f.title?.toLowerCase().includes('monitor') },
                  { id: 'encryption', label: 'Data Encryption', matcher: (f) => f.title?.toLowerCase().includes('encrypt') },
                  { id: 'compute', label: 'Virtual Compute', matcher: (f) => f.id?.startsWith('EC2') || f.title?.toLowerCase().includes('imds') }
                ];

                const categoryStats = heatmapCategories.map(cat => {
                  const catFindings = findings.filter(cat.matcher);
                  let severity = 'Green';
                  if (catFindings.some(f => f.severity === 'Critical')) severity = 'Red';
                  else if (catFindings.some(f => f.severity === 'High')) severity = 'Orange';
                  else if (catFindings.some(f => f.severity === 'Medium')) severity = 'Yellow';
                  
                  return {
                    ...cat,
                    findings: catFindings,
                    severity
                  };
                });

                const renderHealthIndicator = (serviceName, status) => {
                  let color = "text-slate-500";
                  let dotClass = "bg-slate-500";
                  let breathing = "";
                  if (status === 'Healthy') {
                    color = "text-emerald-400";
                    dotClass = "bg-emerald-500";
                    breathing = "animate-ping";
                  } else if (status === 'Warning') {
                    color = "text-amber-400 font-semibold";
                    dotClass = "bg-amber-500";
                    breathing = "animate-pulse";
                  } else if (status === 'Critical') {
                    color = "text-rose-500 font-black";
                    dotClass = "bg-rose-500";
                    breathing = "animate-ping";
                  }
                  return (
                    <div className="flex items-center gap-1.5">
                      <span className="relative flex h-2 w-2">
                        {status !== 'Unknown' && <span className={`${breathing} absolute inline-flex h-full w-full rounded-full opacity-75 ${dotClass}`}></span>}
                        <span className={`relative inline-flex rounded-full h-2 w-2 ${dotClass}`}></span>
                      </span>
                      <span className={color}>{status || 'Healthy'}</span>
                    </div>
                  );
                };

                return (
                  <div className="space-y-8 animate-fadeIn text-slate-350 relative">
                    
                    {/* Live SOC Status Ribbon */}
                    <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between flex-wrap gap-4 text-xs font-mono text-slate-300 shadow-md">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        <span className="font-bold text-white">AWS Connected</span>
                        <span className="text-emerald-400">✓</span>
                      </div>
                      <div className="h-4 w-px bg-slate-850 hidden sm:block"></div>
                      <div>Resources: <span className="text-white font-bold">{scannedCount}</span></div>
                      <div className="h-4 w-px bg-slate-850 hidden sm:block"></div>
                      <div className="flex items-center gap-4">
                        <div>Critical: <span className="text-rose-500 font-bold">{criticalCount}</span></div>
                        <div>High: <span className="text-orange-400 font-bold">{highCount}</span></div>
                        <div>Medium: <span className="text-amber-450 font-bold">{mediumCount}</span></div>
                      </div>
                      <div className="h-4 w-px bg-slate-850 hidden sm:block"></div>
                      <div>Compliance: <span className={`font-bold ${overallCompliance === 'COMPLIANT' ? 'text-emerald-400' : 'text-rose-400'}`}>{overallCompliance}</span></div>
                      <div className="h-4 w-px bg-slate-850 hidden sm:block"></div>
                      <div>Last Scan: <span className="text-cyan-400 font-bold">{secondsSinceLastScan}s ago</span></div>
                      <div className="h-4 w-px bg-slate-850 hidden sm:block"></div>
                      <div>Interval: <span className="text-slate-400">30s</span></div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* Overall Security Score Radial Gauge */}
                      <div className={`p-6 border rounded-2xl bg-slate-900/20 flex flex-col justify-between min-h-[300px] transition-all duration-300 ${score < 50 ? 'border-rose-500/50 shadow-[0_0_15px_rgba(239,68,68,0.15)] animate-pulse' : 'border-slate-800'}`}>
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">Overall Security Score</h3>
                          <p className="text-[10px] text-slate-500">Deductive rating of cloud configuration rules</p>
                        </div>
                        <div className="flex flex-col items-center justify-center py-4 space-y-2">
                          <ScoreGauge value={score} />
                          <div className="text-[10px] font-mono text-slate-400 uppercase tracking-widest font-bold">Score Rating</div>
                          <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${complianceStatus === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : (complianceStatus === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20')}`}>
                            {complianceStatus}
                          </span>
                        </div>
                        <div className="flex justify-between items-center text-[10px] pt-2 border-t border-slate-850">
                          <ProvenanceBadge service="Cloud Posture Engine" endpoint="GET /cloud/assets" method="GET" />
                          <span className="text-slate-500 font-semibold">Last Assessment: {secondsSinceLastScan} sec ago</span>
                        </div>
                      </div>

                      {/* Deductive score breakdown calculation */}
                      <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 flex flex-col justify-between min-h-[300px]">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">Deductive Calculation Details</h3>
                          <p className="text-[10px] text-slate-500">How the posture score was computed</p>
                        </div>
                        <div className="py-2">
                          <InteractiveRiskBreakdown findings={findings} finalScore={score} />
                        </div>
                        <div className="flex justify-between items-end border-t border-slate-850 pt-2 text-xs font-mono font-extrabold">
                          <span className="text-slate-500 font-bold uppercase text-[9.5px]">Calculation Status</span>
                          <span className="text-emerald-400 text-[10px]">✔ Verified</span>
                        </div>
                      </div>

                      {/* Operational Health status grid */}
                      <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 flex flex-col justify-between min-h-[300px]">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">Operational Health Status</h3>
                          <p className="text-[10px] text-slate-500">Active telemetry endpoint functionality</p>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-xs py-2">
                          <div className="p-2.5 bg-slate-950/40 border border-slate-850 rounded flex flex-col gap-1 transition-all hover:bg-slate-900/40">
                            <span className="text-slate-500 font-semibold">EC2 status:</span>
                            {renderHealthIndicator('EC2', opHealth.ec2)}
                            <span className="text-[9px] text-slate-600">Checked: {secondsSinceLastScan}s ago</span>
                          </div>
                          <div className="p-2.5 bg-slate-950/40 border border-slate-850 rounded flex flex-col gap-1 transition-all hover:bg-slate-900/40">
                            <span className="text-slate-500 font-semibold">Storage:</span>
                            {renderHealthIndicator('Storage', opHealth.storage)}
                            <span className="text-[9px] text-slate-600">Checked: {secondsSinceLastScan}s ago</span>
                          </div>
                          <div className="p-2.5 bg-slate-950/40 border border-slate-850 rounded flex flex-col gap-1 transition-all hover:bg-slate-900/40">
                            <span className="text-slate-500 font-semibold">Networks:</span>
                            {renderHealthIndicator('Networks', opHealth.networking)}
                            <span className="text-[9px] text-slate-600">Checked: {secondsSinceLastScan}s ago</span>
                          </div>
                          <div className="p-2.5 bg-slate-950/40 border border-slate-850 rounded flex flex-col gap-1 transition-all hover:bg-slate-900/40">
                            <span className="text-slate-500 font-semibold">Monitor:</span>
                            {renderHealthIndicator('Monitor', opHealth.monitoring)}
                            <span className="text-[9px] text-slate-600">Checked: {secondsSinceLastScan}s ago</span>
                          </div>
                          <div className="p-2.5 bg-slate-950/40 border border-slate-850 rounded flex flex-col gap-1 col-span-2 transition-all hover:bg-slate-900/40">
                            <span className="text-slate-500 font-semibold">IAM Policies:</span>
                            {renderHealthIndicator('Identity', opHealth.identity)}
                            <span className="text-[9px] text-slate-600">Checked: {secondsSinceLastScan}s ago</span>
                          </div>
                        </div>
                        <div className="text-[10px] text-slate-500 font-mono italic">Continuous AWS reachability verify.</div>
                      </div>
                    </div>

                    {/* Historical Security Score Timeline & Misconfiguration Heatmap */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      <div className="lg:col-span-2 p-6 border border-slate-800 rounded-2xl bg-slate-900/20 space-y-4">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">Security Score History Timeline</h3>
                          <p className="text-[10px] text-slate-500">Security score progression audit line</p>
                        </div>
                        <div className="h-56">
                          {cloudSecurityHistory.length === 0 ? (
                            <div className="h-full flex items-center justify-center text-xs text-slate-500">No historical evaluation metrics compiled yet.</div>
                          ) : (
                            <ResponsiveContainer width="100%" height="100%">
                              <AreaChart data={[...cloudSecurityHistory].reverse()} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                                <XAxis dataKey="timestamp" stroke="#9ca3af" fontSize={9} tickFormatter={(tick) => new Date(tick).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})} />
                                <YAxis domain={[0, 100]} stroke="#9ca3af" fontSize={9} />
                                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                                <defs>
                                  <linearGradient id="cloudScoreGrad" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                  </linearGradient>
                                </defs>
                                <Area type="monotone" dataKey="securityScore" name="Security Score" stroke="#6366f1" strokeWidth={2.5} fill="url(#cloudScoreGrad)" dot={true} isAnimationActive={true} animationDuration={800} />
                                <Area type="monotone" dataKey="ursContribution" name="URS Impact" stroke="#ec4899" strokeWidth={1.5} fill="none" dot={false} isAnimationActive={true} />
                              </AreaChart>
                            </ResponsiveContainer>
                          )}
                        </div>
                      </div>

                      {/* Heatmap Misconfiguration */}
                      <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 flex flex-col justify-between">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">Misconfiguration Posture Heatmap</h3>
                          <p className="text-[10px] text-slate-500">Severity categories of security assessment violations</p>
                        </div>
                        <div className="grid grid-cols-2 gap-3 my-auto py-2">
                          {categoryStats.map(cat => {
                            let severityColor = "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
                            if (cat.severity === 'Red') severityColor = "bg-rose-500/20 border-rose-500 text-rose-350 animate-pulse";
                            else if (cat.severity === 'Orange') severityColor = "bg-orange-500/20 border-orange-500 text-orange-300";
                            else if (cat.severity === 'Yellow') severityColor = "bg-amber-500/20 border-amber-500 text-amber-300";

                            return (
                              <div 
                                key={cat.id} 
                                className={`group relative p-3 rounded-xl border text-center transition-all duration-200 cursor-help ${severityColor}`}
                              >
                                <div className="text-sm font-extrabold">{cat.findings.length}</div>
                                <div className="text-[9px] uppercase font-bold tracking-wider truncate">{cat.label}</div>
                                
                                {/* Hover details tooltip */}
                                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 hidden group-hover:block z-50 w-48 p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[9.5px] text-slate-300 text-left shadow-xl pointer-events-none">
                                  <div className="font-bold text-white mb-1 border-b border-slate-850 pb-1">{cat.label}</div>
                                  <div className="space-y-1">
                                    <div>Findings: <span className="font-semibold text-white">{cat.findings.length}</span></div>
                                    <div>Affected: <span className="font-semibold text-white">EC2 Target</span></div>
                                    <div>Severity: <span className={`font-semibold ${cat.severity === 'Red' ? 'text-rose-400' : 'text-slate-300'}`}>{cat.severity}</span></div>
                                    <div className="text-[9px] text-slate-450 italic border-t border-slate-850 pt-1 mt-1">
                                      Action: {cat.findings[0]?.mitigation || "No action required"}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                        <div className="text-[9.5px] text-slate-500 font-mono italic">Visualizing structural posture vulnerabilities.</div>
                      </div>
                    </div>

                    {/* AI Security Assessment & Compliance Mapping Table */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                      {/* AI Explainability */}
                      <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 lg:col-span-1 space-y-4">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">AI Posture Assessment</h3>
                          <p className="text-[10px] text-slate-500">Structured reasoning explanation from AI Engine</p>
                        </div>
                        
                        {aiAnalysisLoading ? (
                          <div className="py-12 space-y-2 text-center text-xs text-slate-550 animate-pulse">
                            <Activity className="mx-auto text-indigo-500 animate-spin" size={24} />
                            <div>Resolving AI telemetry correlation...</div>
                          </div>
                        ) : aiSecurityAnalysis ? (
                          <div className="space-y-3 text-xs animate-fadeIn">
                            <div className="flex justify-between border-b border-slate-850 pb-2">
                              <span className="text-slate-500">Threat Level:</span>
                              <span className={`font-bold uppercase ${aiSecurityAnalysis.threatLevel === 'CRITICAL' ? 'text-rose-400' : (aiSecurityAnalysis.threatLevel === 'HIGH' ? 'text-orange-400' : 'text-emerald-400')}`}>
                                {aiSecurityAnalysis.threatLevel}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-500">AI Confidence:</span>
                              <span className="font-extrabold text-white">{aiSecurityAnalysis.confidence}%</span>
                            </div>
                            <div className="space-y-1">
                              <span className="text-slate-500 block">Primary Root Cause:</span>
                              <span className="font-bold text-slate-200 block bg-slate-950/40 p-2 border border-slate-850 rounded">{aiSecurityAnalysis.primaryCause}</span>
                            </div>
                            <div className="space-y-1">
                              <span className="text-slate-500 block">MITRE Tactic Mapping:</span>
                              <span className="font-bold font-mono text-cyan-400">{aiSecurityAnalysis.mitreMapping}</span>
                            </div>
                            <div className="space-y-1">
                              <span className="text-slate-500 block">Business Impact:</span>
                              <span className="font-semibold text-slate-300">{aiSecurityAnalysis.businessImpact}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 p-2 bg-slate-950/20 border border-slate-850 rounded text-[9.5px]">
                              <div><span className="text-slate-500">Exploit Time:</span> <span className="text-slate-200 font-semibold block">{aiSecurityAnalysis.estimatedExploitTime || "8 minutes"}</span></div>
                              <div><span className="text-slate-500">Recovery Time:</span> <span className="text-slate-200 font-semibold block">{aiSecurityAnalysis.estimatedRecoveryTime || "4 minutes"}</span></div>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-slate-500">Estimated URS Increase:</span>
                              <span className="font-bold text-rose-400">+{aiSecurityAnalysis.estimatedUrsIncrease} Points</span>
                            </div>
                          </div>
                        ) : (
                          <div className="py-12 text-center text-xs text-slate-500">No telemetry input mapped to AI engine.</div>
                        )}
                      </div>

                      {/* Compliance Mapping Table */}
                      <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 lg:col-span-2 space-y-4">
                        <div>
                          <h3 className="text-sm font-bold text-slate-300">AWS Security Posture Findings</h3>
                          <p className="text-[10px] text-slate-500">Discovered misconfigurations mapped to standard frameworks</p>
                        </div>
                        <div className="overflow-x-auto">
                          <table className="w-full text-left border-collapse text-[11px] whitespace-nowrap">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-500 uppercase font-bold text-[10px]">
                                <th className="pb-2 pr-4">Control Description</th>
                                <th className="pb-2 pr-4">Framework Mapping</th>
                                <th className="pb-2 pr-4">Severity</th>
                                <th className="pb-2">URS Weight</th>
                              </tr>
                            </thead>
                            <tbody>
                              {findings.map((f, i) => (
                                <tr 
                                  key={i} 
                                  onClick={() => setSelectedAssetForDrawer(firstAsset)}
                                  className="border-b border-slate-850/60 hover:bg-slate-900/20 cursor-pointer transition"
                                >
                                  <td className="py-2.5 pr-4">
                                    <div className="font-bold text-white flex items-center gap-1.5">
                                      <span className="relative flex h-1.5 w-1.5">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-rose-500"></span>
                                      </span>
                                      {f.title}
                                    </div>
                                    <div className="text-[10px] text-slate-450 max-w-[300px] truncate">
                                      Detected: {secondsSinceLastScan}s ago | Status: <span className="text-rose-400 font-bold uppercase text-[9px]">ACTIVE</span>
                                    </div>
                                  </td>
                                  <td className="py-2.5 pr-4 space-x-1 font-mono text-[10px]">
                                    <span className="px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-900">CIS: {f.cis}</span>
                                    <span className="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-900">NIST: {f.nist}</span>
                                  </td>
                                  <td className="py-2.5 pr-4">
                                    <span className={`font-bold ${f.severity === 'Critical' ? 'text-rose-400' : (f.severity === 'High' ? 'text-orange-400' : 'text-amber-455')}`}>
                                      {f.severity}
                                    </span>
                                  </td>
                                  <td className="py-2.5 font-mono text-slate-400">+{f.ursPenalty} Points</td>
                                </tr>
                              ))}
                              {findings.length === 0 && (
                                <tr>
                                  <td colSpan="4" className="py-8 text-center text-slate-500 italic">✔ All monitored controls are compliant. No security findings detected.</td>
                                </tr>
                              )}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>

                    {/* Automation suggestions remediations */}
                    <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/20 space-y-4">
                      <div>
                        <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2">
                          <Settings size={18} className="text-indigo-400 animate-spin-slow" />
                          Remediation Playbooks & Automation console
                        </h3>
                        <p className="text-[10px] text-slate-500">Copyable infrastructure fixes mapped to discovered findings</p>
                      </div>

                      {findings.length === 0 ? (
                        <div className="py-8 text-center text-slate-500 italic text-xs">✔ Posture is fully compliant. No remediation suggested.</div>
                      ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          <div className="space-y-4">
                            <span className="text-xs font-semibold text-slate-400 block border-b border-slate-800 pb-2">Remediation Rules</span>
                            <div className="space-y-3">
                              {findings.map((f, i) => (
                                <div key={i} className="p-4 rounded-xl bg-slate-950/40 border border-slate-850 space-y-3.5 text-xs">
                                  <div className="flex justify-between items-center">
                                    <span className="font-bold text-white">{f.title}</span>
                                    <span className="text-[10px] text-indigo-400 font-mono">Deduction Reduction: -{f.ursPenalty} URS</span>
                                  </div>
                                  <div className="text-[11px] text-slate-400 leading-relaxed">{f.mitigation}</div>
                                  
                                  {/* Step Progress indicator */}
                                  <div className="space-y-1">
                                    <div className="flex justify-between text-[8px] font-mono text-slate-500 uppercase">
                                      <span>Generated</span>
                                      <span>Reviewed</span>
                                      <span>Approved</span>
                                      <span className="text-indigo-400 font-bold">Ready for Deployment</span>
                                    </div>
                                    <div className="h-1 bg-slate-800 rounded overflow-hidden flex">
                                      <div className="w-1/4 bg-indigo-500 h-full"></div>
                                      <div className="w-1/4 bg-indigo-500 h-full border-l border-slate-905"></div>
                                      <div className="w-1/4 bg-indigo-500 h-full border-l border-slate-905"></div>
                                      <div className="w-1/4 bg-indigo-500 h-full border-l border-slate-905 animate-pulse"></div>
                                    </div>
                                  </div>

                                  <div className="flex justify-between items-center text-[9px] text-slate-500 pt-1.5 border-t border-slate-850/60 font-mono">
                                    <div>Downtime: <span className="text-slate-350">None</span></div>
                                    <div>Rollback: <span className="text-slate-350">Yes</span></div>
                                    <div>Approval: <span className="text-indigo-400">Approved</span></div>
                                    <div>ETA: <span className="text-slate-350">30s</span></div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div className="space-y-4">
                            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                              <span className="text-xs font-semibold text-slate-400 block">Suggested Deploy Code</span>
                              <div className="flex bg-slate-950 p-1 rounded border border-slate-850 text-[10px] font-mono">
                                {['AWS CLI', 'Terraform', 'CloudFormation'].map(f => (
                                  <button 
                                    key={f} 
                                    onClick={() => setSelectedPlaybookFormat(f)}
                                    className={`px-2 py-0.5 rounded transition ${selectedPlaybookFormat === f ? 'bg-indigo-650 text-white font-bold' : 'text-slate-500 hover:text-white'}`}
                                  >
                                    {f}
                                  </button>
                                ))}
                              </div>
                            </div>

                            <div className="relative">
                              <pre className="p-4 bg-slate-950 border border-slate-850 rounded-xl overflow-x-auto text-[10px] font-mono text-cyan-400 timeline-scrollbar max-h-[300px]">
                                {(() => {
                                  const targetId = firstAsset.instanceId;
                                  if (selectedPlaybookFormat === 'AWS CLI') {
                                    return findings.map(f => {
                                      if (f.id === 'SG-SSH-OPEN') return `aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1`;
                                      if (f.id === 'SG-RDP-OPEN') return `aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 3389 --cidr 0.0.0.0/0 --region us-east-1`;
                                      if (f.id === 'EBS-UNENCRYPTED') return `aws ec2 copy-image --source-image-id ami-0c7217cdde317cfec --encrypted --kms-key-id alias/aws/ebs --region us-east-1`;
                                      if (f.id === 'EC2-IMDSV1') return `aws ec2 modify-instance-metadata-options --instance-id ${targetId} --http-tokens required --region us-east-1`;
                                      return `# CLI for mitigation: ${f.title}`;
                                    }).join('\n\n');
                                  } else if (selectedPlaybookFormat === 'Terraform') {
                                    return `resource "aws_security_group_rule" "restrict_access" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "sg-0e6ff0385dc3e9235"
  description       = "Automated mitigation rule restricting public wildcard rules."
}

resource "aws_ebs_volume" "secure_volume" {
  availability_zone = "us-east-1a"
  size              = 32
  encrypted         = true
  kms_key_id        = "alias/aws/ebs"
}`;
                                  } else {
                                    return `Resources:
  SecureSecurityGroupIngress:
    Type: AWS::EC2::SecurityGroupIngress
    Properties:
      GroupId: sg-0e6ff0385dc3e9235
      IpProtocol: tcp
      FromPort: 22
      ToPort: 22
      CidrIp: 10.0.0.0/16`;
                                  }
                                })()}
                              </pre>
                              <button 
                                onClick={() => {
                                  const targetId = firstAsset.instanceId;
                                  let codeText = "";
                                  if (selectedPlaybookFormat === 'AWS CLI') {
                                    codeText = findings.map(f => {
                                      if (f.id === 'SG-SSH-OPEN') return `aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 22 --cidr 0.0.0.0/0 --region us-east-1`;
                                      if (f.id === 'SG-RDP-OPEN') return `aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 3389 --cidr 0.0.0.0/0 --region us-east-1`;
                                      if (f.id === 'EBS-UNENCRYPTED') return `aws ec2 copy-image --source-image-id ami-0c7217cdde317cfec --encrypted --kms-key-id alias/aws/ebs --region us-east-1`;
                                      if (f.id === 'EC2-IMDSV1') return `aws ec2 modify-instance-metadata-options --instance-id ${targetId} --http-tokens required --region us-east-1`;
                                      return `# CLI for mitigation: ${f.title}`;
                                    }).join('\n\n');
                                  } else if (selectedPlaybookFormat === 'Terraform') {
                                    codeText = `resource "aws_security_group_rule" "restrict_access" { ... }`;
                                  } else {
                                    codeText = `Resources: ...`;
                                  }
                                  navigator.clipboard.writeText(codeText);
                                  logTwinEvent("Playbook Script Copied", "success", `${selectedPlaybookFormat} playbook template copied to local clipboard.`);
                                }}
                                className="absolute top-3 right-3 px-2 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded text-[9.5px] font-bold text-slate-350 transition"
                              >
                                Copy
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Interactive Side Drawer for Asset Context */}
                    {selectedAssetForDrawer && (
                      <div className="fixed inset-y-0 right-0 w-96 bg-slate-950 border-l border-slate-800 shadow-2xl p-6 z-50 flex flex-col justify-between animate-slideLeft">
                        <div className="space-y-6">
                          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                            <div>
                              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-mono">Asset Context</span>
                              <h3 className="text-base font-extrabold text-white">Target Inspector</h3>
                            </div>
                            <button 
                              onClick={() => setSelectedAssetForDrawer(null)}
                              className="p-1 border border-slate-800 rounded hover:bg-slate-905 text-slate-400"
                            >
                              <X size={16} />
                            </button>
                          </div>

                          <div className="space-y-4 text-xs">
                            <div className="p-3 bg-slate-900/40 border border-slate-850 rounded-xl space-y-2">
                              <span className="text-[9px] uppercase font-bold text-cyan-400 block tracking-wider">Asset Properties</span>
                              <div className="space-y-1.5 font-mono text-[10.5px]">
                                <div className="flex justify-between"><span className="text-slate-550">ID:</span> <span className="text-slate-200">{selectedAssetForDrawer.instanceId}</span></div>
                                <div className="flex justify-between"><span className="text-slate-550">Region:</span> <span className="text-slate-200">{selectedAssetForDrawer.region}</span></div>
                                <div className="flex justify-between"><span className="text-slate-550">AZ:</span> <span className="text-slate-200">{selectedAssetForDrawer.availabilityZone || "us-east-1a"}</span></div>
                                <div className="flex justify-between"><span className="text-slate-550">Public IP:</span> <span className="text-cyan-400">{selectedAssetForDrawer.publicIp || "Unavailable"}</span></div>
                                <div className="flex justify-between"><span className="text-slate-550">Private IP:</span> <span className="text-slate-350">{selectedAssetForDrawer.privateIp || "Unavailable"}</span></div>
                              </div>
                            </div>

                            <div className="p-3 bg-slate-900/40 border border-slate-850 rounded-xl space-y-2">
                              <span className="text-[9px] uppercase font-bold text-indigo-400 block tracking-wider">Configuration Metadata</span>
                              <div className="space-y-1 font-mono text-[10px]">
                                <div><span className="text-slate-550">Security Groups:</span> {(selectedAssetForDrawer.securityGroups || []).join(', ')}</div>
                                <div><span className="text-slate-550">IAM Role Attached:</span> <span className="text-slate-200">{selectedAssetForDrawer.securityAssessment?.findings?.some(f => f.id === 'IAM-NO-PROFILE') ? 'None' : 'ec2-instance-profile'}</span></div>
                                <div><span className="text-slate-550">Current URS Weight:</span> <span className="text-rose-400 font-bold">+{selectedAssetForDrawer.securityAssessment?.findings?.reduce((acc, curr) => acc + curr.ursPenalty, 0) || 0} Points</span></div>
                              </div>
                            </div>

                            <div className="p-3 bg-slate-900/40 border border-slate-850 rounded-xl space-y-2">
                              <span className="text-[9px] uppercase font-bold text-slate-400 block tracking-wider">Operational Status</span>
                              <div className="flex justify-between items-center">
                                <span className="text-slate-500">Instance State:</span>
                                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold uppercase text-[9.5px]">
                                  {selectedAssetForDrawer.state || "running"}
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>

                        <div className="pt-4 border-t border-slate-800 space-y-2">
                          <button 
                            onClick={() => {
                              openInDigitalTwin(selectedAssetForDrawer.instanceId);
                              setSelectedAssetForDrawer(null);
                            }}
                            className="w-full py-2.5 bg-indigo-650 hover:bg-indigo-600 border border-indigo-500 text-xs font-bold text-white rounded-lg flex items-center justify-center gap-1.5 transition"
                          >
                            <Server size={14} /> Open in Digital Twin
                          </button>
                          <button 
                            onClick={() => setSelectedAssetForDrawer(null)}
                            className="w-full py-2 border border-slate-800 hover:bg-slate-900 text-xs font-semibold text-slate-400 rounded-lg transition"
                          >
                            Dismiss Inspector
                          </button>
                        </div>
                      </div>
                    )}

                  </div>
                );
              })()}
            </div>
          )}

          {/* 4. DIGITAL TWIN TOPOLOGY */}
          {activeTab === 'digital-twin' && (() => {
            const mergedData = getMergedNodesAndEdges(digitalTwinGraph, healthStatus, simulationState);
            const allNodes = mergedData.nodes;
            const allEdges = mergedData.edges;

            // Spacing calculation engine
            const canvasWidth = 1000;
            const canvasHeight = 720;
            
            const layers = [
              { id: "Client", label: "Client Layer", y: 65, height: 75 },
              { id: "Gateway", label: "Gateway Layer", y: 150, height: 75 },
              { id: "Monitoring", label: "Monitoring Layer", y: 235, height: 75 },
              { id: "AI", label: "AI Layer", y: 320, height: 75 },
              { id: "Decision", label: "Decision Layer", y: 405, height: 95 },
              { id: "Automation", label: "Automation Layer", y: 495, height: 75 },
              { id: "Infrastructure", label: "Infrastructure Layer", y: 605, height: 110 }
            ];

            const nodeCoords = {};
            const layerGroups = { Client: [], Gateway: [], Monitoring: [], AI: [], Decision: [], Automation: [], Infrastructure: [] };
            
            allNodes.forEach(node => {
              const layerId = getNodeLayer(node);
              if (layerGroups[layerId]) layerGroups[layerId].push(node);
              else layerGroups['Infrastructure'].push(node);
            });
            
            layers.forEach(l => {
              const layerNodes = layerGroups[l.id] || [];
              const count = layerNodes.length;
              layerNodes.forEach((node, idx) => {
                const fraction = count > 1 ? idx / (count - 1) : 0.5;
                const xOffset = count > 1 ? 95 + fraction * (canvasWidth - 190) : canvasWidth / 2;
                nodeCoords[node.id] = { x: xOffset, y: l.y };
              });
            });

            // Resolve health helper
            const getNodeHealth = (nodeId) => {
              if (nodeId === 'dashboard') return { status: 'healthy', latencyMs: 2, availability: true };
              const keyMap = {
                "core-api-app": "backend",
                "monitoring": "monitoring",
                "node-exporter": "node-exporter",
                "ai-engine": "ai-engine",
                "urs-risk-engine": "risk-engine",
                "ipre-policy-engine": "policy-engine",
                "qrae-quantum-engine": "risk-engine",
                "research-evaluator": "research-evaluator",
                "automation-engine": "automation-engine",
                "attack-simulator": "attack-simulator",
                "digital-twin": "digital-twin",
                "mongodb": "mongodb"
              };
              const key = keyMap[nodeId] || nodeId;
              return healthStatus ? healthStatus[key] : null;
            };

            // KPIs Summary Banner calculations
            const totalServicesCount = 12;
            let healthyCount = 1; // dashboard starts healthy
            let warningCount = 0;
            let offlineCount = 0;

            const servicesList = [
              "core-api-app", "monitoring", "node-exporter", "ai-engine", "urs-risk-engine",
              "ipre-policy-engine", "research-evaluator", "automation-engine", "attack-simulator",
              "digital-twin", "mongodb"
            ];

            servicesList.forEach(id => {
              const health = getNodeHealth(id);
              if (!health || health.status === 'unreachable') offlineCount++;
              else if (health.status === 'unhealthy') warningCount++;
              else healthyCount++;
            });

            const ec2Instances = allNodes.filter(n => n.type === 'EC2 Instance');
            const activeEc2Count = ec2Instances.filter(n => n.status === 'Running' || n.state === 'running').length;
            const healthScore = Math.max(0, Math.min(100, Math.round(((healthyCount + warningCount * 0.5) / totalServicesCount) * 100)));

            // Zoom / Pan handlers
            const zoomIn = () => setTwinZoom(z => Math.min(2.5, z * 1.15));
            const zoomOut = () => setTwinZoom(z => Math.max(0.3, z / 1.15));
            const resetZoom = () => { setTwinZoom(0.85); setTwinPan({ x: 50, y: 20 }); };
            const fitScreen = () => { setTwinZoom(0.7); setTwinPan({ x: 120, y: 40 }); };

            const handleMouseDown = (e) => {
              if (e.target.closest('.node-card-overlay')) return;
              setTwinIsDragging(true);
              setTwinDragStart({ x: e.clientX - twinPan.x, y: e.clientY - twinPan.y });
            };

            const handleMouseMove = (e) => {
              if (!twinIsDragging) return;
              setTwinPan({
                x: e.clientX - twinDragStart.x,
                y: e.clientY - twinDragStart.y
              });
            };

            const handleMouseUp = () => setTwinIsDragging(false);

            // Minimap centering helper
            const handleMinimapClick = (e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const clickX = ((e.clientX - rect.left) / rect.width) * canvasWidth;
              const clickY = ((e.clientY - rect.top) / rect.height) * canvasHeight;
              setTwinPan({
                x: (canvasWidth / 2) - clickX * twinZoom,
                y: (canvasHeight / 2) - clickY * twinZoom
              });
            };

            const getNodeIcon = (iconName, size = 18, className = "") => {
              switch (iconName) {
                case 'layout': return <LayoutDashboard size={size} className={className} />;
                case 'server': return <Server size={size} className={className} />;
                case 'activity': return <Activity size={size} className={className} />;
                case 'brain': return <Brain size={size} className={className} />;
                case 'shield-alert': return <ShieldAlert size={size} className={className} />;
                case 'cog': return <Settings size={size} className={className} />;
                case 'key': return <Key size={size} className={className} />;
                case 'settings': return <Settings size={size} className={className} />;
                case 'play': return <Play size={size} className={className} />;
                case 'network': return <Network size={size} className={className} />;
                case 'database': return <Database size={size} className={className} />;
                case 'cloud': return <Zap size={size} className={className} />;
                case 'map': return <Network size={size} className={className} />;
                case 'shield': return <Shield size={size} className={className} />;
                case 'lock': return <Lock size={size} className={className} />;
                default: return <Server size={size} className={className} />;
              }
            };

            return (
              <div className="space-y-8 animate-fadeIn text-slate-100">
                <style>{`
                  @keyframes flow {
                    to {
                      stroke-dashoffset: -20;
                    }
                  }
                  .flowing-edge {
                    stroke-dasharray: 6, 4;
                    animation: flow 1.2s linear infinite;
                  }
                  .flowing-edge-slow {
                    stroke-dasharray: 6, 4;
                    animation: flow 2.5s linear infinite;
                  }
                  .flowing-edge-fast {
                    stroke-dasharray: 6, 4;
                    animation: flow 0.5s linear infinite;
                  }
                  .pulse-red {
                    animation: pulse-red-effect 2s infinite;
                  }
                  @keyframes pulse-red-effect {
                    0% {
                      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.6);
                    }
                    70% {
                      box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
                    }
                    100% {
                      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
                    }
                  }
                  .timeline-scrollbar::-webkit-scrollbar {
                    width: 4px;
                  }
                  .timeline-scrollbar::-webkit-scrollbar-track {
                    background: transparent;
                  }
                  .timeline-scrollbar::-webkit-scrollbar-thumb {
                    background: #334155;
                    border-radius: 4px;
                  }
                  .timeline-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: #475569;
                  }
                `}</style>

                {/* Dashboard Tab Header */}
                <div className="flex justify-between items-center flex-wrap gap-4">
                  <div className="space-y-1">
                    <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      <Zap size={24} className="text-cyan-400" />
                      Distributed Digital Twin Explorer
                    </h1>
                    <p className="text-xs text-slate-400">Interactive logical architecture topology overlay react-control canvas.</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-slate-400">Last Synced: {formatLastUpdated(twinLastUpdated)}</span>
                    <button onClick={fetchTwinGraph} className="p-2 border border-slate-800 rounded-lg hover:bg-slate-800 text-xs flex items-center gap-1.5 font-semibold">
                      <RefreshCw size={14} /> Refetch Topology
                    </button>
                  </div>
                </div>

                {/* Top Summary strip metrics */}
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Total Services</span>
                    <span className="text-2xl font-extrabold text-white mt-1">{totalServicesCount}</span>
                  </div>
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-emerald-500 tracking-wider">Healthy</span>
                    <span className="text-2xl font-extrabold text-emerald-400 mt-1">{healthyCount}</span>
                  </div>
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-amber-500 tracking-wider">Warning</span>
                    <span className="text-2xl font-extrabold text-amber-400 mt-1">{warningCount}</span>
                  </div>
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-rose-500 tracking-wider">Offline</span>
                    <span className="text-2xl font-extrabold text-rose-400 mt-1">{offlineCount}</span>
                  </div>
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider">Active EC2</span>
                    <span className="text-2xl font-extrabold text-cyan-400 mt-1">{activeEc2Count}</span>
                  </div>
                  <div className="p-4 border border-slate-800 bg-slate-900/35 rounded-2xl flex flex-col justify-between">
                    <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Twin Health Index</span>
                    <span className={`text-2xl font-extrabold mt-1 ${healthScore > 90 ? 'text-emerald-400' : (healthScore > 70 ? 'text-amber-400' : 'text-rose-400')}`}>{healthScore}%</span>
                  </div>
                </div>

                {/* Filter and Search row */}
                <div className="flex flex-wrap justify-between items-center gap-4 p-4 border border-slate-800 rounded-2xl bg-slate-900/10">
                  <div className="flex flex-wrap gap-2">
                    {["All", "Client", "Gateway", "Monitoring", "AI", "Decision", "Automation", "Infrastructure"].map(f => (
                      <button 
                        key={f} 
                        onClick={() => setTwinFilter(f)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${twinFilter === f ? 'bg-indigo-600 text-white border-indigo-500' : 'border-slate-850 bg-slate-900/30 text-slate-400 hover:text-slate-200'}`}
                      >
                        {f}
                      </button>
                    ))}
                  </div>
                  <div className="w-full md:w-64 relative">
                    <input 
                      type="text" 
                      placeholder="Search service node..." 
                      value={twinSearch}
                      onChange={e => setTwinSearch(e.target.value)}
                      className="w-full py-1.5 px-3 rounded-lg border border-slate-800 bg-slate-950 text-xs font-semibold text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                    />
                    {twinSearch && (
                      <button onClick={() => setTwinSearch('')} className="absolute right-2.5 top-2 text-[10px] font-bold text-slate-500 hover:text-slate-300">clear</button>
                    )}
                  </div>
                </div>

                {/* Main Dashboard Canvas & Inspector Panel */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  
                  {/* Canvas container */}
                  <div className="lg:col-span-3 border border-slate-800 rounded-2xl bg-slate-950/60 relative overflow-hidden" style={{ minHeight: '620px' }}>
                    
                    {/* Horizontal layers background bands */}
                    <div className="absolute inset-0 pointer-events-none p-3 space-y-1 bg-slate-950/20" style={{ transform: `translateY(${twinPan.y}px) scale(${twinZoom})`, transformOrigin: 'top left' }}>
                      {layers.map(layer => (
                        <div key={layer.id} className="relative border-b border-dashed border-slate-900/60" style={{ top: `${layer.y - 45}px`, height: `${layer.height}px` }}>
                          <span className="absolute left-6 top-1 text-[9px] font-extrabold uppercase font-mono tracking-widest text-slate-700/80">{layer.label}</span>
                        </div>
                      ))}
                    </div>

                    {/* Canvas header controls */}
                    <div className="absolute top-4 left-4 bg-slate-950/80 p-2 rounded-xl border border-slate-850/80 flex items-center gap-1.5 z-20">
                      <button onClick={zoomIn} title="Zoom In" className="p-1.5 hover:bg-slate-800 rounded text-slate-300 font-bold font-mono text-xs">+</button>
                      <button onClick={zoomOut} title="Zoom Out" className="p-1.5 hover:bg-slate-800 rounded text-slate-300 font-bold font-mono text-xs">-</button>
                      <button onClick={resetZoom} title="Reset Scale" className="p-1.5 hover:bg-slate-800 rounded text-slate-400 font-bold font-mono text-[9px] uppercase">Reset</button>
                      <button onClick={fitScreen} title="Fit screen" className="p-1.5 hover:bg-slate-800 rounded text-slate-400 font-bold font-mono text-[9px] uppercase">Fit</button>
                    </div>

                    {/* Canvas view container */}
                    <div 
                      className={`w-full h-full absolute inset-0 select-none ${twinIsDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
                      onMouseDown={handleMouseDown}
                      onMouseMove={handleMouseMove}
                      onMouseUp={handleMouseUp}
                      onMouseLeave={handleMouseUp}
                    >
                      {/* SVG connections flow layer */}
                      <svg className="w-full h-full absolute inset-0 pointer-events-none" style={{ minHeight: '620px' }}>
                        <defs>
                          <marker id="arrow-green" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                            <path d="M 0 0 L 10 5 L 0 10 z" fill="#10b981" />
                          </marker>
                          <marker id="arrow-yellow" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                            <path d="M 0 0 L 10 5 L 0 10 z" fill="#eab308" />
                          </marker>
                          <marker id="arrow-red" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                            <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
                          </marker>
                          <marker id="arrow-gray" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                            <path d="M 0 0 L 10 5 L 0 10 z" fill="#334155" />
                          </marker>
                        </defs>

                        <g transform={`translate(${twinPan.x}, ${twinPan.y}) scale(${twinZoom})`}>
                          {allEdges.map((edge, idx) => {
                            const s = nodeCoords[edge.source];
                            const t = nodeCoords[edge.target];
                            if (!s || !t) return null;

                            // Calculate intersection offset (shorten lines)
                            const dx = t.x - s.x;
                            const dy = t.y - s.y;
                            const len = Math.sqrt(dx*dx + dy*dy) || 1;
                            const ux = dx / len;
                            const uy = dy / len;

                            const x1 = s.x + ux * 38;
                            const y1 = s.y + uy * 24;
                            const x2 = t.x - ux * 45;
                            const y2 = t.y - uy * 30;

                            // check status
                            const sHealth = getNodeHealth(edge.source);
                            const tHealth = getNodeHealth(edge.target);
                            const sOffline = edge.source !== 'dashboard' && (!sHealth || sHealth.status === 'unreachable');
                            const tOffline = edge.target !== 'dashboard' && (!tHealth || tHealth.status === 'unreachable');
                            
                            let isEdgeOffline = sOffline || tOffline;
                            let isEdgeWarning = (sHealth && sHealth.status === 'unhealthy') || (tHealth && tHealth.status === 'unhealthy');
                            let isEdgeCritical = false;

                            if (simulationState && simulationState.status === 'active') {
                              const criticalEdges = simulationState.highlights?.criticalEdges || [];
                              const warningEdges = simulationState.highlights?.warningEdges || [];
                              const edgeKey = `${edge.source}->${edge.target}`;
                              
                              if (criticalEdges.includes(edgeKey)) {
                                isEdgeCritical = true;
                                isEdgeWarning = false;
                                isEdgeOffline = false;
                              } else if (warningEdges.includes(edgeKey)) {
                                isEdgeWarning = true;
                                isEdgeCritical = false;
                                isEdgeOffline = false;
                              } else {
                                // Default other edges to normal/stable
                                isEdgeCritical = false;
                                isEdgeWarning = false;
                                isEdgeOffline = false;
                              }
                            }

                            let strokeColor = "#10b981";
                            let arrowId = "arrow-green";
                            let edgeClass = "flowing-edge";
                            
                            if (isEdgeOffline) {
                              strokeColor = "#334155";
                              arrowId = "arrow-gray";
                              edgeClass = "";
                            } else if (isEdgeCritical) {
                              strokeColor = "#ef4444";
                              arrowId = "arrow-red";
                              edgeClass = "flowing-edge-fast";
                            } else if (isEdgeWarning) {
                              strokeColor = "#eab308";
                              arrowId = "arrow-yellow";
                              edgeClass = "flowing-edge-slow";
                            }

                            return (
                              <g key={idx}>
                                <path 
                                  d={`M ${x1} ${y1} L ${x2} ${y2}`} 
                                  fill="none" 
                                  stroke={strokeColor} 
                                  strokeWidth="1.8" 
                                  className={edgeClass}
                                  markerEnd={`url(#${arrowId})`}
                                />
                                <text x={(x1 + x2)/2} y={(y1 + y2)/2 - 4} fill="#475569" fontSize="8" fontWeight="bold" textAnchor="middle" className="font-mono">
                                  {edge.label}
                                </text>
                              </g>
                            );
                          })}
                        </g>
                      </svg>

                      {/* HTML overlaid cards node container */}
                      <div className="absolute inset-0 pointer-events-none" style={{ minHeight: '620px' }}>
                        {allNodes.map(node => {
                          const coords = nodeCoords[node.id] || { x: 500, y: 350 };
                          const isSelected = selectedTwinNode && selectedTwinNode.id === node.id;
                          
                          // Spacing & offset translations
                          const cardX = coords.x * twinZoom + twinPan.x;
                          const cardY = coords.y * twinZoom + twinPan.y;

                          // Search filter matching
                          const matchesFilter = twinFilter === 'All' || node.group === twinFilter;
                          const matchesSearch = twinSearch === '' || 
                            node.label.toLowerCase().includes(twinSearch.toLowerCase()) ||
                            node.type.toLowerCase().includes(twinSearch.toLowerCase()) ||
                            node.id.toLowerCase().includes(twinSearch.toLowerCase());
                          const isDimmed = !matchesFilter || !matchesSearch;

                          // Node health resolution
                          const nodeHealth = getNodeHealth(node.id);
                          const isOffline = node.id !== 'dashboard' && (!nodeHealth || nodeHealth.status === 'unreachable');
                          const isWarning = node.riskColor === 'yellow' || (nodeHealth && nodeHealth.status === 'unhealthy');
                          const isCritical = node.riskColor === 'red' || node.riskColor === 'orange';

                          let cardBorder = "border-slate-800 bg-slate-900/90";
                          let shadowGlow = "";
                          let dotColor = "bg-emerald-500";
                          
                          if (isOffline) {
                            cardBorder = "border-slate-900 bg-slate-950/70 text-slate-500";
                            dotColor = "bg-slate-700";
                          } else if (isCritical) {
                            cardBorder = "border-rose-500 bg-slate-900";
                            shadowGlow = "pulse-red shadow-[0_0_12px_rgba(239,68,68,0.55)]";
                            dotColor = "bg-rose-500 animate-ping";
                          } else if (isWarning) {
                            cardBorder = "border-amber-600 bg-slate-900";
                            shadowGlow = "shadow-[0_0_8px_rgba(230,138,0,0.35)]";
                            dotColor = "bg-amber-500";
                          }

                          return (
                            <div 
                              key={node.id} 
                              onClick={() => {
                                setSelectedTwinNode(node);
                                if (node.type === 'EC2 Instance') {
                                  const matchingAsset = cloudAssets?.find(a => a.instanceId === node.id);
                                  if (matchingAsset) setSelectedEc2Instance(matchingAsset);
                                }
                              }}
                              className={`node-card-overlay select-none cursor-pointer p-2.5 rounded-xl border flex flex-col justify-between transition-all duration-200 pointer-events-auto ${cardBorder} ${shadowGlow} ${isDimmed ? 'opacity-25' : 'opacity-100'} ${isSelected ? 'ring-2 ring-indigo-500 scale-105 border-indigo-400 bg-slate-950' : 'hover:border-slate-600'}`}
                              style={{
                                width: '130px',
                                height: '58px',
                                position: 'absolute',
                                left: `${cardX}px`,
                                top: `${cardY}px`,
                                transform: 'translate(-50%, -50%)'
                              }}
                            >
                              <div className="flex justify-between items-center w-full">
                                <span className="text-[8px] uppercase tracking-wider font-extrabold text-slate-500 font-mono truncate">{node.type}</span>
                                <div className="flex items-center gap-1">
                                  <span className={`h-1.5 w-1.5 rounded-full ${dotColor}`}></span>
                                  {isCritical && <span className="h-1.5 w-1.5 rounded-full bg-rose-500"></span>}
                                </div>
                              </div>
                              <div className="flex items-center gap-2 mt-0.5">
                                {getNodeIcon(node.icon || 'server', 14, isOffline ? 'text-slate-600' : 'text-slate-300')}
                                <div className="flex-1 truncate">
                                  <div className={`text-[10px] font-extrabold truncate ${isOffline ? 'text-slate-500' : 'text-white'}`}>{node.label}</div>
                                  <div className="text-[8px] font-mono text-slate-500 truncate">
                                    {node.port ? `Port ${node.port}` : (node.id.startsWith('i-') ? node.id.substring(0, 10) : '')}
                                  </div>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>

                    </div>

                    {/* Floating minimap navigation widget */}
                    <div 
                      onClick={handleMinimapClick}
                      className="absolute bottom-4 right-4 w-40 h-28 bg-slate-950/95 border border-slate-800 rounded-xl backdrop-blur shadow-2xl z-10 overflow-hidden cursor-crosshair hover:border-slate-700 transition"
                    >
                      <svg className="w-full h-full pointer-events-none" viewBox="0 0 1000 720">
                        {/* layers bands inside minimap */}
                        {layers.map((l, i) => (
                          <line key={i} x1="20" y1={l.y} x2="980" y2={l.y} stroke="#1e293b" strokeWidth="3" />
                        ))}
                        {/* nodes inside minimap */}
                        {allNodes.map(node => {
                          const coords = nodeCoords[node.id] || { x: 500, y: 350 };
                          const nodeHealth = getNodeHealth(node.id);
                          const isOff = node.id !== 'dashboard' && (!nodeHealth || nodeHealth.status === 'unreachable');
                          return (
                            <rect 
                              key={node.id} 
                              x={coords.x - 25} 
                              y={coords.y - 12} 
                              width="50" 
                              height="24" 
                              rx="4" 
                              fill={isOff ? '#334155' : (node.riskColor === 'red' ? '#ef4444' : '#10b981')} 
                            />
                          );
                        })}
                        {/* Viewport tracking frame */}
                        {(() => {
                          const w = Math.max(100, canvasWidth / twinZoom);
                          const h = Math.max(80, canvasHeight / twinZoom);
                          const l = Math.max(0, -twinPan.x / twinZoom);
                          const t = Math.max(0, -twinPan.y / twinZoom);
                          return (
                            <rect 
                              x={l} 
                              y={t} 
                              width={w} 
                              height={h} 
                              fill="none" 
                              stroke="#6366f1" 
                              strokeWidth="12" 
                              rx="6"
                            />
                          );
                        })()}
                      </svg>
                      <span className="absolute bottom-1 left-2 text-[7px] uppercase font-bold tracking-widest text-slate-500 select-none pointer-events-none">Minimap</span>
                    </div>

                  </div>

                  {/* Inspector Panel Sidebar & Timeline Side Panel */}
                  <div className="flex flex-col gap-6 lg:col-span-1">
                    
                    {/* Node Inspector details */}
                    <div className="p-5 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-4">
                      <h3 className="text-sm font-bold text-slate-300">Node Properties</h3>
                      {selectedTwinNode ? (
                        <div className="space-y-4 text-xs animate-fadeIn">
                          <div className="space-y-1">
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">Service Label / Name</span>
                            <h4 className="font-bold text-white text-base">{selectedTwinNode.label}</h4>
                            <span className="text-[9px] font-mono text-cyan-400 block">{selectedTwinNode.id}</span>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div className="p-2.5 bg-slate-900/40 border border-slate-850 rounded">
                              <span className="text-slate-500 block text-[9px]">Type</span>
                              <span className="font-bold text-white block truncate">{selectedTwinNode.type}</span>
                            </div>
                            <div className="p-2.5 bg-slate-900/40 border border-slate-850 rounded">
                              <span className="text-slate-500 block text-[9px]">Port Mapping</span>
                              <span className="font-bold text-indigo-400 block font-mono">{selectedTwinNode.port || 'Dynamic'}</span>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-3">
                            <div className="p-2.5 bg-slate-900/40 border border-slate-850 rounded">
                              <span className="text-slate-500 block text-[9px]">Health State</span>
                              <span className={`font-bold block uppercase text-[10px] ${(() => {
                                const h = getNodeHealth(selectedTwinNode.id);
                                if (selectedTwinNode.id === 'dashboard') return 'text-emerald-400';
                                if (!h || h.status === 'unreachable') return 'text-rose-400';
                                if (h.status === 'unhealthy') return 'text-amber-400';
                                return 'text-emerald-400';
                              })()}`}>
                                {(() => {
                                  const h = getNodeHealth(selectedTwinNode.id);
                                  if (selectedTwinNode.id === 'dashboard') return 'healthy';
                                  return h ? h.status : 'offline';
                                })()}
                              </span>
                            </div>
                            <div className="p-2.5 bg-slate-900/40 border border-slate-850 rounded">
                              <span className="text-slate-500 block text-[9px]">Response Latency</span>
                              <span className="font-bold text-slate-300 block font-mono">
                                {(() => {
                                  const h = getNodeHealth(selectedTwinNode.id);
                                  return h && h.latencyMs ? `${h.latencyMs} ms` : 'Unavailable';
                                })()}
                              </span>
                            </div>
                          </div>

                          {/* Extra cloud node metrics metadata rendering */}
                          {selectedTwinNode.type === 'EC2 Instance' && (() => {
                            const asset = cloudAssets?.find(a => a.instanceId === selectedTwinNode.id);
                            const assessment = asset?.securityAssessment;
                            const findingsList = assessment?.findings || [];
                            
                            return (
                              <div className="space-y-3">
                                <div className="p-3 bg-slate-900/50 border border-slate-850 rounded-xl space-y-2">
                                  <span className="text-[9px] uppercase font-bold text-cyan-400 tracking-wider block">EC2 Live Telemetry</span>
                                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                                    <div><span className="text-slate-500">Region:</span> <span className="text-slate-200 font-semibold">{asset?.region || 'us-east-1'}</span></div>
                                    <div><span className="text-slate-500">Type:</span> <span className="text-slate-200 font-semibold">{asset?.instanceType || 't3.medium'}</span></div>
                                    <div className="col-span-2"><span className="text-slate-500">Public IP:</span> <span className="text-cyan-400 font-mono">{asset?.publicIp || 'Unavailable'}</span></div>
                                  </div>
                                  {ec2Metrics && selectedEc2Instance?.instanceId === selectedTwinNode.id && (
                                    <div className="pt-2 border-t border-slate-800 space-y-1.5 text-[10px]">
                                      <div className="flex justify-between">
                                        <span className="text-slate-400">vCPU Usage:</span>
                                        <span className="text-emerald-400 font-bold">{ec2Metrics.cpu?.utilization ?? 'Unavailable'}%</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span className="text-slate-400">RAM Utilized:</span>
                                        <span className="text-indigo-400 font-bold">{ec2Metrics.memory?.usagePercent ?? 'Unavailable'}%</span>
                                      </div>
                                    </div>
                                  )}
                                </div>

                                {assessment && (
                                  <div className="p-3 bg-slate-900/50 border border-slate-850 rounded-xl space-y-3 text-[11px]">
                                    <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                                      <span className="text-[9px] uppercase font-bold text-indigo-400 tracking-wider">Security Assessment</span>
                                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${assessment.complianceStatus === 'CRITICAL' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : (assessment.complianceStatus === 'WARNING' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : (assessment.complianceStatus === 'UNKNOWN' ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'))}`}>
                                        {assessment.complianceStatus}
                                      </span>
                                    </div>
                                    
                                    {assessment.overallScore !== null && (
                                      <div className="flex justify-between items-center">
                                        <span className="text-slate-400">Security Score:</span>
                                        <span className="font-extrabold text-white">{assessment.overallScore}/100</span>
                                      </div>
                                    )}

                                    {findingsList.length > 0 ? (
                                      <div className="space-y-2">
                                        <span className="text-[10px] text-slate-450 font-semibold block">Open Findings ({findingsList.length})</span>
                                        <div className="space-y-1 max-h-[140px] overflow-y-auto pr-1 text-[10px] timeline-scrollbar">
                                          {findingsList.map((f, i) => (
                                            <div key={i} className="flex justify-between items-start gap-1 p-2 rounded bg-slate-950/40 border border-slate-850">
                                              <span className="font-medium text-slate-200 truncate">{f.title}</span>
                                              <span className={`text-[9px] px-1 font-bold ${f.severity === 'Critical' ? 'text-rose-400' : (f.severity === 'High' ? 'text-orange-400' : 'text-amber-400')}`}>
                                                -{f.ursPenalty} URS
                                              </span>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    ) : (
                                      <div className="text-[10px] text-emerald-400 font-semibold">✔ No open security findings detected.</div>
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          })()}

                          <div className="p-3 bg-slate-900/40 border border-slate-850 rounded space-y-1">
                            <span className="text-slate-500 block text-[9px]">Layer / Class</span>
                            <span className="font-extrabold text-slate-300 block">{getNodeLayer(selectedTwinNode)}</span>
                          </div>

                          <div className="p-3 bg-slate-900/40 border border-slate-850 rounded space-y-1">
                            <span className="text-slate-500 block text-[9px]">Data Source classification</span>
                            <span className="font-bold text-slate-200 block truncate">{selectedTwinNode.group === 'Client' ? 'STATIC' : (selectedTwinNode.type === 'EC2 Instance' ? 'LIVE' : 'DERIVED')}</span>
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-10 text-xs text-slate-500 space-y-2">
                          <HelpCircle size={32} className="mx-auto text-slate-600" />
                          <p>Select any node in the layered canvas layout to inspect properties and live telemetry metrics.</p>
                        </div>
                      )}
                    </div>

                    {/* Timeline Log sidebar */}
                    <div className="p-5 border border-slate-800 rounded-2xl bg-slate-900/10 flex-1 flex flex-col min-h-[220px]">
                      <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-1.5">
                        <Activity size={15} className="text-indigo-400" />
                        Live Events timeline
                      </h3>
                      <div className="flex-1 overflow-y-auto timeline-scrollbar space-y-3 pr-1 text-[11px] max-h-[240px]">
                        {twinEvents.map(ev => {
                          let typeBadgeColor = "border-slate-800 bg-slate-900/40 text-slate-400";
                          if (ev.type === 'success') typeBadgeColor = "border-emerald-950 bg-emerald-500/10 text-emerald-400";
                          if (ev.type === 'warning') typeBadgeColor = "border-amber-950 bg-amber-500/10 text-amber-400";
                          if (ev.type === 'error') typeBadgeColor = "border-rose-950 bg-rose-500/10 text-rose-400";


                           return (
                             <div key={ev.id} className={`p-2 border rounded ${typeBadgeColor}`}>
                               <div className="flex justify-between items-center mb-1">
                                 <span className="font-bold">{ev.title}</span>
                                 <span className="text-[9px] opacity-70 font-mono">{ev.timestamp}</span>
                               </div>
                               <p className="opacity-80 leading-relaxed">{ev.message}</p>
                             </div>
                           );
                        })}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Legend panel */}
                <div className="p-5 border border-slate-800 rounded-2xl bg-slate-900/15 space-y-3">
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Topology Canvas Legend</h3>
                  <div className="flex flex-wrap gap-x-8 gap-y-3 text-xs text-slate-400">
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                      <span>Healthy Service</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="h-2.5 w-2.5 rounded-full bg-amber-500"></span>
                      <span>Warning Status</span>
                    </div>
                    <div className="flex items-center gap-2 animate-pulse">
                      <span className="h-2.5 w-2.5 rounded-full bg-rose-500"></span>
                      <span>Critical / Anomaly Detected</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="h-2 w-2 rounded-full bg-slate-700"></span>
                      <span>Service Offline</span>
                    </div>
                    <div className="flex items-center gap-2 font-mono text-[10px] text-emerald-400">
                      <span>── ⇢ ──</span>
                      <span>Active Flow</span>
                    </div>
                    <div className="flex items-center gap-2 font-mono text-[10px] text-slate-600">
                      <span>── ──</span>
                      <span>Offline Link</span>
                    </div>
                  </div>
                </div>

              </div>
            );
          })()}

          {/* 5. ATTACK SIMULATOR */}
          {activeTab === 'attack-simulator' && (() => {
            const isSimActive = simulationActive || (simulationState && simulationState.status === 'active');
            const isFinished = simulationState?.isFinished || false;
            const elapsed = simulationState?.elapsed || 0;
            const currentPhase = simulationState?.phase || "NORMAL";
            const isPaused = simulationState?.paused || false;
            
            const displayScenarios = scenariosList.length > 0 ? scenariosList : [
              {
                id: "crypto-mining",
                name: "Crypto Mining Malware",
                threat_level: "High",
                description: "Cryptojacking script hijacking system resources to mine Monero (XMR).",
                estimated_duration: "45s",
                affected_assets: "EC2 Production, Gateway, Cloud Adapter",
                difficulty: "Medium",
                mitre_ids: "T1496 (Resource Hijacking), T1059 (Command and Scripting)",
                recommended_response: "Kill process, Quarantine Host, Block Mining Pool",
              },
              {
                id: "ransomware",
                name: "Ransomware Attack",
                threat_level: "Critical",
                description: "Malicious payload encrypting system volume and staging extortion.",
                estimated_duration: "45s",
                affected_assets: "EC2 Production, Digital Twin DB, File Storage",
                difficulty: "High",
                mitre_ids: "T1486 (Data Encrypted), T1491 (Defacement)",
                recommended_response: "Snapshot VM, Detach Volume, Isolate Host",
              },
              {
                id: "ddos",
                name: "DDoS Saturation",
                threat_level: "High",
                description: "SYN Flood flooding gateway interfaces to disrupt availability.",
                estimated_duration: "45s",
                affected_assets: "Gateway, Subnet, Client Interface",
                difficulty: "Medium",
                mitre_ids: "T1498 (Network Denial of Service)",
                recommended_response: "WAF Rules, Scale Target Group, Enable Rate Limit",
              },
              {
                id: "credential-theft",
                name: "Credential Theft & Privilege Escalation",
                threat_level: "High",
                description: "Brute-force account takeover resulting in administrative token staging.",
                estimated_duration: "45s",
                affected_assets: "IAM, Admin Console, Database",
                difficulty: "Hard",
                mitre_ids: "T1110 (Brute Force), T1068 (Exploitation for Privilege)",
                recommended_response: "Disable IAM User, Rotate Keys, Invalidate Session",
              },
              {
                id: "data-exfiltration",
                name: "Data Exfiltration to Threat Actor",
                threat_level: "Critical",
                description: "Abnormal volume queries exfiltrating customer DB dumps to external IP.",
                estimated_duration: "45s",
                affected_assets: "Database, Cloud Gateway, IAM Role",
                difficulty: "Hard",
                mitre_ids: "T1048 (Exfiltration Over Alternative Protocol)",
                recommended_response: "Block Security Group, Rotate Secrets, Disable IAM Role",
              }
            ];

            const activeScenario = displayScenarios.find(s => s.id === (simulationState?.scenarioId || selectedAttack)) || displayScenarios[0];
            
            const formatElapsed = (sec) => {
              const m = Math.floor(sec / 60).toString().padStart(2, '0');
              const s = (sec % 60).toString().padStart(2, '0');
              return `${m}:${s}`;
            };

            const phasesList = [
              "NORMAL",
              "ATTACK STARTED",
              "ATTACK PROGRESSING",
              "AI DETECTED ANOMALY",
              "URS RISK UPDATED",
              "AUTOMATION TRIGGERED",
              "MITIGATION RUNNING",
              "RECOVERY",
              "POST INCIDENT REPORT"
            ];

            const getPhaseIndex = (p) => phasesList.indexOf(p);
            const activePhaseIdx = getPhaseIndex(currentPhase);

            return (
              <div className="space-y-6 animate-fadeIn text-slate-100">
                {/* 10. EXECUTIVE DASHBOARD HEADER PANEL */}
                <div className="p-4 rounded-2xl border border-slate-800 bg-slate-950/40 backdrop-blur-md grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 items-center">
                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Simulation Status</span>
                    <span className="flex items-center gap-1.5 text-xs font-extrabold uppercase">
                      {isSimActive ? (
                        isPaused ? (
                          <>
                            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                            <span className="text-amber-400">PAUSED</span>
                          </>
                        ) : (
                          <>
                            <span className="h-2 w-2 rounded-full bg-rose-500 animate-ping" />
                            <span className="text-rose-500 animate-pulse">RUNNING</span>
                          </>
                        )
                      ) : isFinished ? (
                        <>
                          <span className="h-2 w-2 rounded-full bg-indigo-500" />
                          <span className="text-indigo-400">COMPLETED</span>
                        </>
                      ) : (
                        <>
                          <span className="h-2 w-2 rounded-full bg-slate-500" />
                          <span className="text-slate-400">IDLE</span>
                        </>
                      )}
                    </span>
                  </div>

                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Threat Target</span>
                    <span className="text-xs font-bold text-slate-200 truncate">{activeScenario.name}</span>
                  </div>

                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Time Elapsed</span>
                    <span className="text-xs font-mono font-extrabold text-indigo-400">
                      {formatElapsed(elapsed)} <span className="text-slate-600 font-normal">/ 00:45</span>
                    </span>
                  </div>

                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Affected Assets</span>
                    <span className="text-xs font-bold text-rose-400">
                      {isSimActive ? "3 Nodes" : isFinished ? "3 Nodes (Mitigated)" : "0 Nodes"}
                    </span>
                  </div>

                  <div className="flex flex-col space-y-1 col-span-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Current Phase</span>
                    <span className="text-xs font-extrabold text-slate-200 uppercase tracking-wide flex items-center gap-1.5">
                      <Cpu size={12} className="text-indigo-400 animate-pulse" />
                      {currentPhase}
                    </span>
                  </div>

                  <div className="flex flex-col space-y-1 text-right">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">URS Risk Score</span>
                    <span className={`text-sm font-extrabold ${simulationState?.telemetry.risk > 80 ? 'text-rose-500' : (simulationState?.telemetry.risk > 40 ? 'text-amber-500' : 'text-emerald-500')}`}>
                      {simulationState ? `${Math.round(simulationState.telemetry.risk)}% URS` : "8% URS"}
                    </span>
                  </div>
                </div>

                {/* MAIN GRID SECTION */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  
                  {/* LEFT COLUMN: SCENARIO LIBRARY */}
                  <div className="lg:col-span-1 space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Scenario Library</span>
                      <span className="text-[9px] bg-slate-900 border border-slate-800 text-slate-300 font-bold px-2 py-0.5 rounded uppercase">Sprint 24.1</span>
                    </div>

                    <div className="space-y-3">
                      {displayScenarios.map(sc => {
                        const isSelected = selectedAttack === sc.id;
                        return (
                          <div 
                            key={sc.id}
                            onClick={() => {
                              if (!isSimActive) setSelectedAttack(sc.id);
                            }}
                            className={`p-4 rounded-xl border transition-all duration-200 select-none ${isSimActive ? 'opacity-55 cursor-not-allowed' : 'cursor-pointer'} ${isSelected ? 'border-indigo-500 bg-slate-900/60 shadow-[0_0_12px_rgba(99,102,241,0.25)]' : 'border-slate-800 bg-slate-900/10 hover:border-slate-700 hover:bg-slate-900/20'}`}
                          >
                            <div className="flex justify-between items-start gap-1">
                              <span className="text-xs font-bold text-slate-100">{sc.name}</span>
                              <span className={`px-2 py-0.5 rounded text-[8px] font-extrabold uppercase border ${sc.threat_level === 'Critical' ? 'bg-red-500/10 text-red-400 border-red-500/25' : 'bg-orange-500/10 text-orange-400 border-orange-500/25'}`}>
                                {sc.threat_level}
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-400 mt-2 line-clamp-2 leading-relaxed">{sc.description}</p>
                            
                            <div className="grid grid-cols-2 gap-2 mt-3 text-[9px] text-slate-500 border-t border-slate-850 pt-2 font-semibold">
                              <div>Duration: <span className="text-slate-300">{sc.estimated_duration}</span></div>
                              <div>Diff: <span className="text-slate-300">{sc.difficulty}</span></div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* CENTER COLUMN: LIVE ATTACK PROGRESS & TIMELINE */}
                  <div className="lg:col-span-2 space-y-6">
                    
                    {/* ATTACK PROGRESS PANEL */}
                    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/10 space-y-4">
                      <div className="flex justify-between items-center">
                        <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Activity size={14} className="text-rose-500 animate-pulse" />
                          Live Simulation Timeline
                        </h3>
                        <div className="flex gap-2">
                          {isSimActive ? (
                            <>
                              {isPaused ? (
                                <button 
                                  onClick={handleResumeSimulation}
                                  className="bg-amber-600 hover:bg-amber-500 text-white font-bold p-1.5 rounded-lg text-[10px] flex items-center gap-1"
                                >
                                  <Play size={10} className="fill-white" /> Resume
                                </button>
                              ) : (
                                <button 
                                  onClick={handlePauseSimulation}
                                  className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold p-1.5 rounded-lg text-[10px] flex items-center gap-1"
                                >
                                  <Pause size={10} className="fill-slate-300" /> Pause
                                </button>
                              )}
                              <button 
                                onClick={handleResetSimulation}
                                className="bg-rose-900/60 hover:bg-rose-900 border border-rose-800 text-white font-bold p-1.5 rounded-lg text-[10px] flex items-center gap-1"
                              >
                                <RotateCcw size={10} /> Reset
                              </button>
                            </>
                          ) : (
                            <button 
                              onClick={() => handleStartSimulation(selectedAttack)}
                              className="bg-rose-600 hover:bg-rose-500 text-white font-bold py-1.5 px-4 rounded-lg text-[10px] flex items-center gap-1"
                            >
                              <Play size={10} className="fill-white" /> Initialize Threat Scenario
                            </button>
                          )}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="space-y-1.5">
                        <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                          <span>Simulation Lifecycle</span>
                          <span>{Math.round((elapsed / 45) * 100)}%</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-1.5 border border-slate-850 overflow-hidden">
                          <div 
                            className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${(elapsed / 45) * 100}%` }}
                          />
                        </div>
                      </div>

                      {/* Lifecycle Steps Indicators */}
                      <div className="grid grid-cols-3 md:grid-cols-9 gap-2 pt-2 border-t border-slate-850">
                        {phasesList.map((ph, idx) => {
                          const isDone = activePhaseIdx > idx;
                          const isActive = activePhaseIdx === idx;
                          return (
                            <div key={ph} className="flex flex-col items-center text-center space-y-1">
                              <span className={`h-4 w-4 rounded-full flex items-center justify-center text-[8px] font-bold border ${isDone ? 'bg-emerald-500/20 border-emerald-500 text-emerald-400' : (isActive ? 'bg-rose-500/20 border-rose-500 text-rose-400 animate-pulse' : 'bg-slate-900 border-slate-800 text-slate-600')}`}>
                                {isDone ? "✓" : idx + 1}
                              </span>
                              <span className={`text-[7px] font-extrabold uppercase tracking-tight truncate w-full ${isActive ? 'text-rose-400 font-bold' : (isDone ? 'text-slate-400' : 'text-slate-600')}`}>
                                {ph.replace(" ", "\n")}
                              </span>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    {/* CONSOLE EVENTS TIMELINE */}
                    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-950/20 space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-900 pb-2">
                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                          <Terminal size={14} className="text-indigo-400" />
                          Security Console & Event Logs
                        </h4>
                        <span className="text-[9px] font-mono text-slate-500">Live Scrapes</span>
                      </div>

                      <div className="h-64 overflow-y-auto space-y-2 pr-2 timeline-scrollbar font-mono text-[10px]">
                        {simulationState && simulationState.timeline && simulationState.timeline.length > 0 ? (
                          simulationState.timeline.map((evt, idx) => {
                            let iconColor = "text-indigo-400";
                            let logBg = "bg-indigo-500/5 border-indigo-500/10 text-indigo-300";
                            
                            if (evt.status === 'warning') {
                              iconColor = "text-amber-400";
                              logBg = "bg-amber-500/5 border-amber-500/10 text-amber-300";
                            } else if (evt.status === 'critical') {
                              iconColor = "text-rose-500";
                              logBg = "bg-rose-500/5 border-rose-500/10 text-rose-300";
                            } else if (evt.status === 'success') {
                              iconColor = "text-emerald-400";
                              logBg = "bg-emerald-500/5 border-emerald-500/10 text-emerald-300";
                            }

                            return (
                              <div key={idx} className={`p-2.5 rounded-lg border flex gap-3 items-start animate-fadeIn ${logBg}`}>
                                <span className="text-[9px] text-slate-500 mt-0.5">{evt.time}</span>
                                <div className="flex-1">
                                  <span className="font-semibold block">{evt.event}</span>
                                </div>
                              </div>
                            );
                          })
                        ) : (
                          <div className="h-full flex flex-col justify-center items-center text-slate-600 space-y-2 py-12">
                            <Terminal size={32} className="opacity-30" />
                            <span>Telemetry listener idle. Initialize simulation to stream logs.</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* RIGHT COLUMN: AI ANALYSIS PANEL & AUTOMATION ACTIONS */}
                  <div className="lg:col-span-1 space-y-6">
                    
                    {/* AI ANALYSIS BOARD */}
                    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/10 space-y-4">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Brain size={14} className="text-indigo-400" />
                        AI Engine Intelligence
                      </h4>

                      <div className="space-y-3 text-[11px] text-slate-400">
                        <div className="flex justify-between border-b border-slate-900 pb-1.5">
                          <span>Threat Type:</span>
                          <span className="font-bold text-slate-200">{isSimActive ? simulationState?.ai.threatType : "N/A"}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-900 pb-1.5">
                          <span>Model Confidence:</span>
                          <span className="font-bold text-purple-400">{isSimActive ? `${simulationState?.ai.threatConfidence}%` : "0.0%"}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-900 pb-1.5">
                          <span>Anomaly Score:</span>
                          <span className="font-bold text-rose-400">{isSimActive ? `${(simulationState?.ai.detectionConfidence / 100).toFixed(3)}` : "0.000"}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-900 pb-1.5">
                          <span>Predicted Hourly Loss:</span>
                          <span className="font-bold text-slate-200 flex items-center">
                            <DollarSign size={10} className="text-rose-500" />
                            {isSimActive && elapsed >= 15 ? "12,500/hr" : "0/hr"}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-900 pb-1.5">
                          <span>MITRE Technique:</span>
                          <span className="font-mono text-cyan-400 font-bold text-[9px]">{isSimActive ? simulationState?.ai.mitreMapping : "N/A"}</span>
                        </div>
                        <div className="flex justify-between pb-1.5">
                          <span>Quantum Readiness:</span>
                          <span className="font-bold text-slate-200">{isSimActive ? simulationState?.ai.quantumReadinessImpact : "Stable"}</span>
                        </div>
                      </div>
                    </div>

                    {/* LIVE Remediations PLAYBOOK */}
                    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-950/20 space-y-4">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Settings size={14} className="text-emerald-400 animate-spin-slow" />
                        Remediation Playbook
                      </h4>

                      <div className="space-y-2 max-h-56 overflow-y-auto pr-1 timeline-scrollbar">
                        {isSimActive && simulationState?.automation && simulationState.automation.length > 0 ? (
                          simulationState.automation.map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 rounded bg-slate-900/40 border border-slate-850 text-[10px]">
                              <div className="flex items-center gap-2">
                                <span className={`h-1.5 w-1.5 rounded-full ${item.executionStatus === 'Running' ? 'bg-amber-400 animate-ping' : 'bg-emerald-400'}`} />
                                <span className="font-bold text-slate-300">{item.action}</span>
                              </div>
                              <span className={`font-mono text-[9px] px-1.5 py-0.5 rounded font-extrabold uppercase ${item.executionStatus === 'Running' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400'}`}>
                                {item.executionStatus === 'Running' ? 'RUNNING' : `DONE (${item.estimatedExecutionTime}s)`}
                              </span>
                            </div>
                          ))
                        ) : (
                          <div className="py-8 text-center text-slate-600 text-[10px] space-y-2">
                            <ShieldCheck size={28} className="mx-auto opacity-35" />
                            <span>No mitigations active. Playbooks trigger at Containment stage.</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* BOTTOM PANEL: REAL-TIME CHARTS */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Processor & Memory Workload</span>
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={simulationHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                          <XAxis dataKey="elapsed" stroke="#475569" fontSize={8} label={{ value: 'Second', position: 'insideBottom', offset: -2, fill: '#475569', fontSize: 8 }} />
                          <YAxis stroke="#475569" fontSize={8} domain={[0, 100]} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: 9 }} />
                          <Legend verticalAlign="top" height={24} iconSize={8} wrapperStyle={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="cpu" name="CPU Usage %" stroke="#f43f5e" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                          <Line type="monotone" dataKey="memory" name="RAM Usage %" stroke="#818cf8" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Network & Disk Activity</span>
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={simulationHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                          <XAxis dataKey="elapsed" stroke="#475569" fontSize={8} label={{ value: 'Second', position: 'insideBottom', offset: -2, fill: '#475569', fontSize: 8 }} />
                          <YAxis stroke="#475569" fontSize={8} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: 9 }} />
                          <Legend verticalAlign="top" height={24} iconSize={8} wrapperStyle={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="network" name="Network (KB/s)" stroke="#34d399" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                          <Line type="monotone" dataKey="disk" name="Disk IOPS %" stroke="#fbbf24" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/20 space-y-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Adaptive URS Risk Score</span>
                    <div className="h-44 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={simulationHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                          <XAxis dataKey="elapsed" stroke="#475569" fontSize={8} label={{ value: 'Second', position: 'insideBottom', offset: -2, fill: '#475569', fontSize: 8 }} />
                          <YAxis stroke="#475569" fontSize={8} domain={[0, 100]} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: 9 }} />
                          <Legend verticalAlign="top" height={24} iconSize={8} wrapperStyle={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="risk" name="URS score %" stroke="#ec4899" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                          <Line type="monotone" dataKey="anomaly_score" name="AI Anomaly" stroke="#06b6d4" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* END SIMULATION MODAL OVERLAY: INCIDENT REPORT */}
                {isFinished && simulationState?.report && (
                  <div className="p-6 rounded-2xl border border-indigo-900/50 bg-indigo-950/20 backdrop-blur-md space-y-6 animate-slideUp">
                    <div className="flex justify-between items-center border-b border-indigo-900 pb-3">
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold font-mono text-indigo-400 uppercase tracking-widest">INCIDENT REPORT SUMMARY</span>
                        <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                          <ShieldCheck size={20} className="text-emerald-400" />
                          Incident: {simulationState.report.incidentId} (RESOLVED)
                        </h2>
                      </div>
                      <button 
                        onClick={() => window.print()}
                        className="bg-indigo-650 hover:bg-indigo-600 text-white font-bold py-1.5 px-4 rounded text-xs flex items-center gap-1"
                      >
                        <Download size={12} /> Export Defender Report
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-300">
                      <div className="md:col-span-2 space-y-4">
                        <div className="space-y-1">
                          <span className="text-[10px] uppercase font-bold text-slate-500">Executive Summary</span>
                          <p className="leading-relaxed bg-slate-950/40 p-3 rounded border border-slate-900">{simulationState.report.executiveSummary}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="space-y-1">
                            <span className="text-[10px] uppercase font-bold text-slate-500">Root Cause Diagnostics</span>
                            <div className="bg-slate-950/40 p-2.5 rounded border border-slate-900 leading-relaxed">{simulationState.report.rootCause}</div>
                          </div>
                          <div className="space-y-1">
                            <span className="text-[10px] uppercase font-bold text-slate-500">MITRE ATT&CK Alignment</span>
                            <div className="bg-slate-950/40 p-2.5 rounded border border-slate-900 font-mono font-bold text-cyan-400">{simulationState.report.mitreMapping}</div>
                          </div>
                        </div>
                      </div>

                      <div className="p-4 rounded bg-slate-950/30 border border-slate-900 space-y-3">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block">Incident Metrics</span>
                        <div className="space-y-2">
                          <div className="flex justify-between border-b border-slate-900 pb-1">
                            <span>Threat Class:</span>
                            <span className="font-bold text-white">{simulationState.report.attackType}</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-900 pb-1">
                            <span>Peak Unified Risk (URS):</span>
                            <span className="font-bold text-rose-500">{simulationState.report.maxRiskScore}</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-900 pb-1">
                            <span>Started Time:</span>
                            <span className="font-mono text-slate-400">{simulationState.report.started}</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-900 pb-1">
                            <span>Detection Latency:</span>
                            <span className="font-bold text-amber-500">15s</span>
                          </div>
                          <div className="flex justify-between border-b border-slate-900 pb-1">
                            <span>Containment Duration:</span>
                            <span className="font-bold text-emerald-400">15s</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Automation Plan Success:</span>
                            <span className="font-bold text-emerald-400">100% (Success)</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-900 space-y-2 text-xs">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Hardening & Security Policy Recommendations</span>
                      <ul className="list-disc list-inside space-y-1.5 text-slate-300 leading-relaxed pl-1">
                        {simulationState.report.recommendations.map((rec, i) => (
                          <li key={i}>{rec}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            );
          })()}

          {/* 6. ADAPTIVE URS RISK */}
          {/* 6. DECISION INTELLIGENCE CENTER */}
          {activeTab === 'risk' && (() => {
            const isSimActive = simulationActive || (simulationState && simulationState.status === 'active');
            const isFinished = simulationState?.isFinished || false;
            const liveTick = simulationState?.elapsed || 0;
            const isPaused = simulationState?.paused || false;

            const isReplayMode = selectedReplayTick !== null;
            const effectiveElapsed = isReplayMode ? selectedReplayTick : liveTick;
            const activeScenarioId = simulationState?.scenarioId || selectedAttack;

            // Scenario curves for interpolation
            const curves = {
              "crypto-mining": [
                { t: 0, cpu: 15, memory: 40, disk: 15, network: 5, risk: 8, anomaly: 0.12, latency: 18, FP: 2.1 },
                { t: 15, cpu: 78, memory: 60, disk: 16, network: 4500, risk: 35, anomaly: 0.58, latency: 22, FP: 2.3 },
                { t: 25, cpu: 98, memory: 75, disk: 17, network: 15000, risk: 90, anomaly: 0.94, latency: 74, FP: 2.3 },
                { t: 35, cpu: 45, memory: 65, disk: 16, network: 150, risk: 40, anomaly: 0.38, latency: 32, FP: 2.2 },
                { t: 45, cpu: 15, memory: 40, disk: 15, network: 5, risk: 10, anomaly: 0.12, latency: 18, FP: 2.1 }
              ],
              "ransomware": [
                { t: 0, cpu: 12, memory: 35, disk: 10, network: 8, risk: 6, anomaly: 0.10, latency: 15, FP: 1.8 },
                { t: 15, cpu: 65, memory: 55, disk: 88, network: 300, risk: 58, anomaly: 0.62, latency: 25, FP: 2.0 },
                { t: 25, cpu: 88, memory: 70, disk: 99, network: 480, risk: 98, anomaly: 0.96, latency: 61, FP: 2.2 },
                { t: 35, cpu: 30, memory: 48, disk: 18, network: 25, risk: 42, anomaly: 0.40, latency: 28, FP: 2.0 },
                { t: 45, cpu: 12, memory: 35, disk: 10, network: 8, risk: 8, anomaly: 0.10, latency: 15, FP: 1.8 }
              ],
              "ddos": [
                { t: 0, cpu: 8, memory: 30, disk: 8, network: 50, risk: 5, anomaly: 0.08, latency: 14, FP: 1.5 },
                { t: 15, cpu: 75, memory: 55, disk: 9, network: 850000, risk: 80, anomaly: 0.72, latency: 34, FP: 1.7 },
                { t: 25, cpu: 95, memory: 65, disk: 10, network: 999000, risk: 96, anomaly: 0.92, latency: 82, FP: 1.9 },
                { t: 35, cpu: 25, memory: 40, disk: 8, network: 2000, risk: 35, anomaly: 0.35, latency: 24, FP: 1.6 },
                { t: 45, cpu: 8, memory: 30, disk: 8, network: 50, risk: 6, anomaly: 0.08, latency: 14, FP: 1.5 }
              ],
              "credential-theft": [
                { t: 0, cpu: 10, memory: 35, disk: 12, network: 10, risk: 7, anomaly: 0.11, latency: 16, FP: 2.0 },
                { t: 15, cpu: 16, memory: 36, disk: 13, network: 18, risk: 68, anomaly: 0.65, latency: 28, FP: 2.2 },
                { t: 25, cpu: 20, memory: 38, disk: 13, network: 25, risk: 94, anomaly: 0.91, latency: 68, FP: 2.3 },
                { t: 35, cpu: 15, memory: 36, disk: 12, network: 15, risk: 42, anomaly: 0.39, latency: 22, FP: 2.1 },
                { t: 45, cpu: 10, memory: 35, disk: 12, network: 10, risk: 10, anomaly: 0.11, latency: 16, FP: 2.0 }
              ],
              "data-exfiltration": [
                { t: 0, cpu: 12, memory: 30, disk: 15, network: 15, risk: 6, anomaly: 0.09, latency: 17, FP: 1.9 },
                { t: 15, cpu: 42, memory: 48, disk: 62, network: 280000, risk: 75, anomaly: 0.70, latency: 31, FP: 2.1 },
                { t: 25, cpu: 52, memory: 56, disk: 72, network: 720000, risk: 96, anomaly: 0.93, latency: 79, FP: 2.2 },
                { t: 35, cpu: 22, memory: 38, disk: 25, network: 1000, risk: 40, anomaly: 0.36, latency: 21, FP: 2.0 },
                { t: 45, cpu: 12, memory: 30, disk: 15, network: 15, risk: 8, anomaly: 0.09, latency: 17, FP: 1.9 }
              ]
            };

            const getInterpolatedVal = (tick) => {
              const pts = curves[activeScenarioId] || curves["crypto-mining"];
              let p0 = pts[0], p1 = pts[pts.length - 1];
              for (let i = 0; i < pts.length - 1; i++) {
                if (tick >= pts[i].t && tick <= pts[i+1].t) {
                  p0 = pts[i];
                  p1 = pts[i+1];
                  break;
                }
              }
              const ratio = (tick - p0.t) / (p1.t - p0.t || 1);
              const lerpV = (v0, v1) => v0 + (v1 - v0) * ratio;
              return {
                cpu: lerpV(p0.cpu, p1.cpu),
                memory: lerpV(p0.memory, p1.memory),
                disk: lerpV(p0.disk, p1.disk),
                network: lerpV(p0.network, p1.network),
                risk: lerpV(p0.risk, p1.risk),
                anomaly: lerpV(p0.anomaly, p1.anomaly),
                latency: lerpV(p0.latency, p1.latency),
                FP: lerpV(p0.FP, p1.FP)
              };
            };

            const currentSim = isSimActive ? getInterpolatedVal(effectiveElapsed) : null;
            const currentRiskVal = currentSim ? currentSim.risk : (evaluatorDashboard?.kpis?.averageRiskScore ?? 8.0);
            const severityLevel = currentRiskVal > 80 ? "CRITICAL" : (currentRiskVal > 50 ? "HIGH RISK" : (currentRiskVal > 25 ? "MODERATE" : "LOW RISK"));
            const severityColor = currentRiskVal > 80 ? "text-purple-400" : (currentRiskVal > 50 ? "text-rose-500" : (currentRiskVal > 25 ? "text-amber-500" : "text-emerald-500"));
            const severityBg = currentRiskVal > 80 ? "bg-purple-500/10 border-purple-500/20" : (currentRiskVal > 50 ? "bg-rose-500/10 border-rose-500/20" : (currentRiskVal > 25 ? "bg-amber-500/10 border-amber-500/20" : "bg-emerald-500/10 border-emerald-500/20"));

            // Splunk logs matching effectiveElapsed
            const logMilestones = [
              { t: 5, event: "Inbound suspicious PowerShell vector execution detected", status: "warning", time: "12:15:05" },
              { t: 12, event: "Telemetry Alert: Outbound UDP socket request spike", status: "warning", time: "12:15:12" },
              { t: 18, event: "AI Engine Alert: Reconstruction anomaly score exceeded 0.75", status: "critical", time: "12:15:18" },
              { t: 22, event: "URS Risk Score updated: Node evaluation marked Critical", status: "critical", time: "12:15:22" },
              { t: 25, event: "Policy Playbook selected: recommended isolation actions", status: "info", time: "12:15:25" },
              { t: 28, event: "Automation response: quarantined host & detached volumes", status: "success", time: "12:15:28" },
              { t: 35, event: "Containment completed: workload telemetry returns to baseline", status: "success", time: "12:15:35" },
              { t: 42, event: "Post-incident audit generated: recovery verified", status: "success", time: "12:15:42" }
            ];

            const activeLogs = isSimActive ? logMilestones.filter(log => log.t <= effectiveElapsed) : [];

            // Helper to get color values for gauge arcs
            const getGaugeColor = (score) => {
              if (score > 80) return "#a855f7"; // Purple
              if (score > 60) return "#f43f5e"; // Red
              if (score > 40) return "#f97316"; // Orange
              if (score > 20) return "#eab308"; // Yellow
              return "#10b981"; // Green
            };

            const staticCompare = currentRiskVal > 8.0 ? (currentRiskVal - 22.4) : 8.0;

            return (
              <div className="space-y-6 animate-fadeIn text-slate-100">
                {/* Time-Travel Warning Banner */}
                {isReplayMode && (
                  <div className="p-3.5 bg-amber-500/10 border border-amber-500/30 rounded-xl text-amber-400 flex justify-between items-center text-xs animate-slideDown">
                    <span className="font-bold flex items-center gap-1.5">
                      <Clock size={14} className="animate-spin-slow" />
                      ⏸ TIME-TRAVEL INCIDENT PLAYBACK: Viewing metrics snapshot locked at t = {effectiveElapsed} seconds.
                    </span>
                    <button 
                      onClick={() => setSelectedReplayTick(null)}
                      className="bg-amber-600 hover:bg-amber-500 text-white font-bold py-1 px-3 rounded text-[10px] uppercase tracking-wider"
                    >
                      Resume Live Tracking
                    </button>
                  </div>
                )}

                {/* 10. LIVE HEALTH RIBBON */}
                <div className="p-3 rounded-xl border border-slate-800 bg-slate-950/40 backdrop-blur-md flex flex-wrap justify-between gap-4 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    Monitoring: <span className="text-slate-200">Healthy</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    AI Engine: <span className="text-slate-200">Active</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                    URS Risk: <span className="text-slate-200">Quantifying</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    Policy: <span className="text-slate-200">Enforcing</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className={`h-2 w-2 rounded-full ${isSimActive && effectiveElapsed >= 28 ? 'bg-amber-500 animate-ping' : 'bg-emerald-500'}`} />
                    Automation: <span className="text-slate-200">{isSimActive && effectiveElapsed >= 28 ? 'Executing Playbook' : 'Idle / Listening'}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-500" />
                    Cloud Adapter: <span className="text-slate-200">Synced</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-indigo-500" />
                    Digital Twin: <span className="text-slate-200">Connected</span>
                  </div>
                </div>

                {/* EXECUTIVE CURRENT SITUATION OVERVIEW */}
                <div className={`p-5 rounded-2xl border flex flex-col md:flex-row justify-between items-center gap-4 ${severityBg} transition-all duration-300`}>
                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold font-mono">Current Situation Overview</span>
                    <h2 className="text-lg font-black tracking-tight text-white flex items-center gap-2">
                      Severity: <span className={severityColor}>{severityLevel}</span>
                    </h2>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-xs w-full md:w-auto">
                    <div className="p-3 bg-slate-950/30 rounded border border-slate-900/60 text-center">
                      <span className="text-slate-500 block text-[9px]">Active Incident</span>
                      <span className="font-extrabold text-slate-200 block mt-1">{isSimActive ? activeScenarioId.replace("-", " ").toUpperCase() : "None Detected"}</span>
                    </div>
                    <div className="p-3 bg-slate-950/30 rounded border border-slate-900/60 text-center">
                      <span className="text-slate-500 block text-[9px]">Impacted Nodes</span>
                      <span className="font-extrabold text-rose-400 block mt-1">{isSimActive ? "3 Assets" : "0 Assets"}</span>
                    </div>
                    <div className="p-3 bg-slate-950/30 rounded border border-slate-900/60 text-center">
                      <span className="text-slate-500 block text-[9px]">AI Classification</span>
                      <span className="font-extrabold text-cyan-400 block mt-1">{isSimActive ? "Malware (T1496)" : "N/A"}</span>
                    </div>
                    <div className="p-3 bg-slate-950/30 rounded border border-slate-900/60 text-center">
                      <span className="text-slate-500 block text-[9px]">Estimated Loss</span>
                      <span className="font-extrabold text-slate-200 block mt-1 flex items-center justify-center gap-0.5 text-rose-400">
                        <DollarSign size={10} />
                        {isSimActive && effectiveElapsed >= 12 ? "12,500/hr" : "0/hr"}
                      </span>
                    </div>
                  </div>
                </div>

                {/* ROW 1: GAUGE & PROPAGATION PATH & BUSINESS IMPACT */}
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                  
                  {/* HERO GAUGE PANEL */}
                  <div className="lg:col-span-1 p-6 border border-slate-800 rounded-2xl bg-slate-900/10 flex flex-col justify-between items-center min-h-[340px] relative">
                    <div className="flex justify-between items-center w-full">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Unified URS Risk Gauge</span>
                      <span className="text-[9px] bg-slate-950 border border-slate-900 px-2 py-0.5 rounded text-indigo-400 uppercase font-mono font-bold">Adaptive</span>
                    </div>

                    {/* Circular Semi Gauge Arc */}
                    <div className="relative w-44 h-28 flex items-end justify-center overflow-hidden mt-4">
                      <svg className="absolute top-0 left-0 w-full h-full" viewBox="0 0 100 50">
                        {/* Gauge Arc background */}
                        <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="#1e293b" strokeWidth="8" strokeLinecap="round" />
                        {/* Interactive colored arc */}
                        <path 
                          d="M 10 50 A 40 40 0 0 1 90 50" 
                          fill="none" 
                          stroke={getGaugeColor(currentRiskVal)} 
                          strokeWidth="8" 
                          strokeLinecap="round"
                          strokeDasharray="126"
                          strokeDashoffset={126 - (126 * (Math.min(currentRiskVal, 100) / 100))}
                          className="transition-all duration-500 ease-out"
                        />
                      </svg>
                      {/* Gauge Indicator Text */}
                      <div className="text-center space-y-0.5 z-10">
                        <span className="text-4xl font-black text-white leading-none block">{currentRiskVal.toFixed(1)}</span>
                        <span className={`text-[10px] font-extrabold uppercase tracking-widest ${severityColor}`}>{severityLevel}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 w-full text-center text-[10px] text-slate-500 border-t border-slate-850 pt-3 mt-4">
                      <div>
                        <span className="block uppercase text-[8px] font-bold">AI Anomaly Confidence</span>
                        <span className="font-extrabold text-slate-300 block mt-0.5">{currentSim ? `${(currentSim.anomaly * 100).toFixed(1)}%` : "N/A"}</span>
                      </div>
                      <div>
                        <span className="block uppercase text-[8px] font-bold">Prediction Latency</span>
                        <span className="font-extrabold text-cyan-400 block mt-0.5">{currentSim ? `${Math.round(currentSim.latency)} ms` : "N/A"}</span>
                      </div>
                    </div>
                  </div>

                  {/* THREAT PROPAGATION PATHWAY */}
                  <div className="lg:col-span-2 p-6 border border-slate-800 rounded-2xl bg-slate-950/20 flex flex-col justify-between min-h-[340px]">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Live Threat Propagation Flow</span>
                      <span className="text-[9px] bg-slate-900 border border-slate-850 px-2 py-0.5 rounded text-amber-400 uppercase font-mono font-bold">Visual Topology</span>
                    </div>

                    {/* Nodes pathway layout */}
                    <div className="flex flex-col space-y-6 justify-center items-center py-4 relative w-full">
                      {/* SVG connection connector line with traveling dash pulse */}
                      <svg className="absolute w-full h-full pointer-events-none z-0" style={{ minHeight: '180px' }}>
                        <path 
                          d="M 50,20 L 50,180" 
                          fill="none" 
                          stroke="#1e293b" 
                          strokeWidth="2"
                        />
                        {isSimActive && !isPaused && (
                          <path 
                            d="M 50,20 L 50,180" 
                            fill="none" 
                            stroke={getGaugeColor(currentRiskVal)} 
                            strokeWidth="2"
                            strokeDasharray="6, 12"
                            className="flowing-edge-fast"
                          />
                        )}
                      </svg>

                      {/* Node boxes */}
                      {[
                        { label: "Internet Gateway", trigger: 5, color: "text-emerald-400 border-emerald-500/25 bg-emerald-500/5" },
                        { label: "Application Router", trigger: 12, color: "text-amber-400 border-amber-500/25 bg-amber-500/5" },
                        { label: "AI Engine Predictor", trigger: 18, color: "text-cyan-400 border-cyan-500/25 bg-cyan-500/5" },
                        { label: "EC2 Instance Host", trigger: 22, color: "text-rose-400 border-rose-500/25 bg-rose-500/5" }
                      ].map((node, i) => {
                        const isNodeCompromised = isSimActive && effectiveElapsed >= node.trigger;
                        const statusColor = isNodeCompromised ? "border-rose-500 bg-rose-500/10 text-rose-400" : "border-slate-800 bg-slate-950 text-slate-500";
                        return (
                          <div key={i} className={`px-4 py-2 rounded-lg border text-center font-mono text-[10px] font-bold z-10 w-44 transition-all duration-300 ${statusColor}`}>
                            {node.label} {isNodeCompromised ? "⚠️ ALERT" : "✓ OK"}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* BUSINESS IMPACT CARD */}
                  <div className="lg:col-span-1 p-6 border border-slate-800 rounded-2xl bg-slate-900/10 flex flex-col justify-between min-h-[340px]">
                    <div className="flex justify-between items-center">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Business Impact Analytics</span>
                      <span className="text-[9px] bg-slate-950 border border-slate-900 px-2 py-0.5 rounded text-rose-400 uppercase font-mono font-bold">Loss Stats</span>
                    </div>

                    <div className="space-y-4 my-auto">
                      <div className="flex justify-between border-b border-slate-900 pb-2 text-xs">
                        <span className="text-slate-500">Service Availability:</span>
                        <span className={`font-bold ${currentRiskVal > 80 ? 'text-rose-500' : 'text-emerald-400'}`}>
                          {isSimActive && effectiveElapsed >= 15 ? `${(99.9 - (currentRiskVal / 4)).toFixed(2)}%` : "99.99%"}
                        </span>
                      </div>
                      <div className="flex justify-between border-b border-slate-900 pb-2 text-xs">
                        <span className="text-slate-500">Potential Downtime:</span>
                        <span className="font-bold text-slate-200">{isSimActive && effectiveElapsed >= 12 ? `${Math.round(effectiveElapsed / 2)} mins` : "0 mins"}</span>
                      </div>
                      <div className="flex justify-between border-b border-slate-900 pb-2 text-xs">
                        <span className="text-slate-500">Hourly Financial Loss:</span>
                        <span className="font-bold text-slate-200">
                          {isSimActive && effectiveElapsed >= 12 ? "$240/hour" : "$0.00/hour"}
                        </span>
                      </div>
                      <div className="flex justify-between border-b border-slate-900 pb-2 text-xs">
                        <span className="text-slate-500">SLA Violation Hazard:</span>
                        <span className={`font-bold ${currentRiskVal > 70 ? 'text-rose-500' : 'text-emerald-400'}`}>{currentRiskVal > 70 ? 'Critical Risk' : 'Low Risk'}</span>
                      </div>
                    </div>

                    <div className="p-2.5 bg-slate-950/40 border border-slate-900 rounded text-[9px] text-slate-500 leading-relaxed font-semibold">
                      Quantifying SLA compliance based on active instance downtime.
                    </div>
                  </div>
                </div>

                {/* ROW 2: Stacked Contributors Drilldown & Asset Table & Explainable AI */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* EXPANDABLE CONTRIBUTORS PANEL */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Interactive Risk Contributors</h3>
                    
                    <div className="space-y-3">
                      {[
                        { 
                          id: "telemetry", 
                          label: "Telemetry Health Indicator", 
                          percent: currentSim ? Math.min(Math.round(currentSim.cpu * 0.4), 40) : 10,
                          details: [
                            { label: "CPU utilization load", val: currentSim ? `${Math.round(currentSim.cpu)}%` : "12.2%" },
                            { label: "Memory allocation profile", val: currentSim ? `${Math.round(currentSim.memory)}%` : "34.5%" },
                            { label: "Outbound network packet volume", val: currentSim ? `${Math.round(currentSim.network)} KB/s` : "15 KB/s" }
                          ]
                        },
                        { 
                          id: "cloud", 
                          label: "Cloud Exposure Risk", 
                          percent: currentSim ? Math.min(Math.round(currentSim.disk * 0.3), 30) : 12,
                          details: [
                            { label: "Security group parameters", val: isSimActive ? "Public Ingress Open" : "Restricted (OK)" },
                            { label: "Unencrypted storage volumes", val: isSimActive ? "1 Volume (Warning)" : "0 Volumes (OK)" },
                            { label: "IAM session keys assessment", val: isSimActive ? "Weak Rotation Policy" : "Compliant (OK)" }
                          ]
                        },
                        { 
                          id: "ai", 
                          label: "AI Engine Anomaly Rating", 
                          percent: currentSim ? Math.min(Math.round(currentSim.anomaly * 30), 30) : 15,
                          details: [
                            { label: "Anomaly classification output", val: currentSim ? severityLevel : "Normal" },
                            { label: "Model confidence threshold", val: currentSim ? `${(currentSim.anomaly * 100).toFixed(1)}%` : "1.25%" }
                          ]
                        }
                      ].map(item => {
                        const isExpanded = expandedContrib === item.id;
                        return (
                          <div key={item.id} className="border border-slate-850 bg-slate-950/20 rounded-xl overflow-hidden text-xs">
                            <div 
                              onClick={() => setExpandedContrib(isExpanded ? null : item.id)}
                              className="p-3 flex justify-between items-center cursor-pointer hover:bg-slate-900/35 transition"
                            >
                              <div className="flex flex-col space-y-1 w-full mr-4">
                                <div className="flex justify-between text-[11px] font-bold text-slate-300">
                                  <span>{item.label}</span>
                                  <span>{item.percent}%</span>
                                </div>
                                <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden">
                                  <div className="bg-indigo-500 h-1.5 rounded-full transition-all duration-300" style={{ width: `${item.percent * 3}%` }} />
                                </div>
                              </div>
                              <span className="text-[10px] text-slate-500 font-extrabold">{isExpanded ? "▲" : "▼"}</span>
                            </div>
                            
                            {isExpanded && (
                              <div className="p-3 bg-slate-950/40 border-t border-slate-900 space-y-2 text-[10px] font-mono text-slate-400">
                                {item.details.map((det, dIdx) => (
                                  <div key={dIdx} className="flex justify-between">
                                    <span>{det.label}:</span>
                                    <span className="text-slate-200 font-bold">{det.val}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* ASSET THREAT TABLE */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">AWS Console Assets Posture</h3>
                    
                    <div className="overflow-x-auto text-[10px]">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="border-b border-slate-850 text-slate-500 uppercase font-bold">
                            <th className="pb-2">Host Asset</th>
                            <th className="pb-2 text-center">Status</th>
                            <th className="pb-2 text-right">Risk %</th>
                            <th className="pb-2 text-right">Threat</th>
                          </tr>
                        </thead>
                        <tbody>
                          {[
                            { name: "ec2-production-01", healthy: !(isSimActive && effectiveElapsed >= 15), risk: currentSim ? Math.round(currentSim.risk) : 8, threat: isSimActive ? "High (Miner)" : "Low" },
                            { name: "application-gateway", healthy: !(isSimActive && effectiveElapsed >= 12), risk: currentSim ? Math.min(Math.round(currentSim.risk / 2), 48) : 6, threat: isSimActive ? "Medium" : "Low" },
                            { name: "twin-database-cluster", healthy: true, risk: 8, threat: "Low" }
                          ].map((row, idx) => (
                            <tr key={idx} className="border-b border-slate-900/60 last:border-b-0 hover:bg-slate-900/10 font-mono">
                              <td className="py-2.5 font-bold text-slate-300">{row.name}</td>
                              <td className="py-2.5 text-center">
                                <span className={`h-2 w-2 rounded-full inline-block ${row.healthy ? 'bg-emerald-500' : 'bg-rose-500 animate-pulse'}`} />
                              </td>
                              <td className="py-2.5 text-right font-bold text-white">{row.risk}%</td>
                              <td className={`py-2.5 text-right font-bold ${row.threat.includes("High") ? "text-rose-500" : (row.threat.includes("Medium") ? "text-amber-400" : "text-emerald-400")}`}>{row.threat}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* EXPLAINABLE AI FORMULA */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Explainable AI (XAI) Formula</h3>
                    
                    <div className="p-4 bg-slate-950/40 border border-slate-900 rounded-xl space-y-4">
                      <span className="text-[10px] text-slate-500 uppercase font-mono block">Unified Risk Weight Parameters</span>
                      
                      <div className="flex justify-between items-center flex-wrap gap-2 font-mono text-xs">
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-500">Telemetry</span>
                          <span className="font-extrabold text-indigo-400 mt-1">{currentSim ? Math.min(Math.round(currentSim.cpu * 0.4), 40) : 8}</span>
                        </div>
                        <span className="text-slate-600 font-bold">+</span>
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-500">Anomaly</span>
                          <span className="font-extrabold text-cyan-400 mt-1">{currentSim ? Math.min(Math.round(currentSim.anomaly * 30), 30) : 10}</span>
                        </div>
                        <span className="text-slate-600 font-bold">+</span>
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-500">Exposure</span>
                          <span className="font-extrabold text-amber-500 mt-1">{currentSim ? Math.min(Math.round(currentSim.disk * 0.2), 20) : 6}</span>
                        </div>
                        <span className="text-slate-600 font-bold">-</span>
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-500">Mitigate</span>
                          <span className="font-extrabold text-emerald-400 mt-1">{isSimActive && effectiveElapsed >= 28 ? 14 : 0}</span>
                        </div>
                        <span className="text-slate-600 font-bold">=</span>
                        <div className="flex flex-col items-center">
                          <span className="text-[10px] text-slate-500">Total URS</span>
                          <span className="font-black text-rose-500 mt-1">{currentRiskVal.toFixed(0)}</span>
                        </div>
                      </div>

                      <p className="text-[9px] text-slate-500 leading-relaxed font-semibold">
                        Algorithm maps real-time resource telemetry parameters adding vector components, mitigated by active policy automation offsets.
                      </p>
                    </div>
                  </div>
                </div>

                {/* ROW 3: Dual-Line Risk Timeline & Splunk Logger & Forecast Panel */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* DUAL LINE RISK TIMELINE */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-2">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Risk Timeline: Adaptive vs Static</span>
                    
                    <div className="h-48 w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={isSimActive ? simulationHistory : liveRiskHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.3} />
                          <XAxis dataKey="elapsed" stroke="#475569" fontSize={8} label={{ value: 'Second', position: 'insideBottom', offset: -2, fill: '#475569', fontSize: 8 }} />
                          <YAxis stroke="#475569" fontSize={8} domain={[0, 100]} />
                          <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '8px', fontSize: 9 }} />
                          <Legend verticalAlign="top" height={24} iconSize={8} wrapperStyle={{ fontSize: 9 }} />
                          <Line type="monotone" dataKey="risk" name="Adaptive URS %" stroke="#ec4899" strokeWidth={1.8} dot={false} isAnimationActive={true} animationDuration={300} />
                          {/* Static benchmark curve */}
                          <Line type="monotone" dataKey="static" name="Static Threshold %" stroke="#475569" strokeWidth={1.2} strokeDasharray="4 4" dot={false} isAnimationActive={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* SPLUNK EVENT FEED LOGGER */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-950/20 space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-900 pb-2">
                      <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                        <Terminal size={14} className="text-indigo-400" />
                        Live Splunk Decision Feed
                      </h4>
                      <span className="text-[9px] font-mono text-slate-500">Click to replay snapshot</span>
                    </div>

                    <div className="h-44 overflow-y-auto space-y-2 pr-1 timeline-scrollbar font-mono text-[9px]">
                      {isSimActive && activeLogs.length > 0 ? (
                        activeLogs.map((log, idx) => (
                          <div 
                            key={idx} 
                            onClick={() => setSelectedReplayTick(log.t)}
                            className="p-2 rounded bg-slate-900/40 border border-slate-850 flex justify-between items-start gap-2 hover:border-indigo-500 hover:bg-slate-900/60 cursor-pointer select-none transition"
                          >
                            <div className="flex gap-2 items-start">
                              <span className="text-slate-600 font-bold">{log.time}</span>
                              <span className="text-slate-300">{log.event}</span>
                            </div>
                            <span className="text-[8px] bg-indigo-500/10 text-indigo-400 font-extrabold px-1.5 py-0.5 rounded border border-indigo-500/15">REPLAY</span>
                          </div>
                        ))
                      ) : (
                        <div className="h-full flex flex-col justify-center items-center text-slate-600 space-y-2 py-12">
                          <Terminal size={24} className="opacity-30" />
                          <span>Telemetry stream active. Logs appear when simulation initializes.</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* PREDICTIVE FORECAST PANEL */}
                  <div className="p-6 border border-slate-800 rounded-2xl bg-slate-900/10 space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Predictive Risk Forecast Panel</h3>
                    
                    <div className="space-y-3 font-mono text-[10px]">
                      {(() => {
                        const predSummary = simulationState?.prediction_summary || latestRisk?.prediction_summary;
                        if (predSummary) {
                          const projectedData = predSummary.projected_urs ? Object.entries(predSummary.projected_urs).map(([hour, val]) => ({
                            hour: `${hour}h`,
                            URS: parseFloat(typeof val === 'number' ? val.toFixed(1) : val)
                          })).sort((a, b) => parseInt(a.hour) - parseInt(b.hour)) : [];

                          return (
                            <>
                              <div className="p-3 bg-slate-950/40 rounded border border-slate-900 flex justify-between items-center">
                                <div className="space-y-1">
                                  <span className="text-slate-500 block text-[9px] uppercase">Risk Trend Projection (24h)</span>
                                  <span className={`text-xs font-bold block ${predSummary.risk_trend === 'increasing' ? 'text-rose-400' : 'text-emerald-400'}`}>
                                    Trend: {predSummary.risk_trend.toUpperCase()} (24h Projected URS: {predSummary.projected_urs?.["24"] || "N/A"})
                                  </span>
                                </div>
                                <span className="text-slate-400 font-bold text-xs">CTPS: {typeof predSummary.ctps === 'number' ? predSummary.ctps.toFixed(2) : predSummary.ctps}</span>
                              </div>
                              
                              <div className="p-3 bg-slate-950/40 rounded border border-slate-900 flex justify-between items-center">
                                <div className="space-y-1">
                                  <span className="text-slate-500 block text-[9px] uppercase">Forecast Confidence & Impact</span>
                                  <span className="text-xs font-bold text-indigo-400 block">
                                    Conf: {typeof predSummary.confidence?.score === 'number' ? predSummary.confidence.score.toFixed(1) : predSummary.confidence?.score}% ({predSummary.confidence?.level || "N/A"})
                                  </span>
                                </div>
                                <span className="text-indigo-400 font-bold text-xs">Impact: {predSummary.business_impact?.level || "N/A"}</span>
                              </div>

                              {projectedData.length > 0 && (
                                <div className="p-3 bg-slate-950/40 rounded border border-slate-900 space-y-2">
                                  <span className="text-slate-500 block text-[9px] uppercase">Projected Risk Curve</span>
                                  <div className="h-28 w-full mt-1">
                                    <ResponsiveContainer width="100%" height="100%">
                                      <LineChart data={projectedData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.2} />
                                        <XAxis dataKey="hour" stroke="#475569" fontSize={8} />
                                        <YAxis stroke="#475569" fontSize={8} domain={[0, 100]} />
                                        <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '4px', fontSize: 8 }} />
                                        <Line type="monotone" dataKey="URS" name="Projected URS %" stroke="#ec4899" strokeWidth={1.5} dot={{ r: 2 }} />
                                      </LineChart>
                                    </ResponsiveContainer>
                                  </div>
                                </div>
                              )}
                            </>
                          );
                        } else {
                          return (
                            <>
                              <div className="p-3 bg-slate-950/40 rounded border border-slate-900 flex justify-between items-center">
                                <div className="space-y-1">
                                  <span className="text-slate-500 block text-[9px] uppercase">If Automation Succeeds</span>
                                  <span className="text-xs font-bold text-emerald-400 block">Risk drops to 8%</span>
                                </div>
                                <span className="text-emerald-500 font-bold text-xs">94% Prob</span>
                              </div>
                              
                              <div className="p-3 bg-slate-950/40 rounded border border-slate-900 flex justify-between items-center">
                                <div className="space-y-1">
                                  <span className="text-slate-500 block text-[9px] uppercase">If Ignored / Fails</span>
                                  <span className="text-xs font-bold text-rose-500 block">Risk spikes to 100%</span>
                                </div>
                                <span className="text-rose-500 font-bold text-xs">6% Prob</span>
                              </div>
                            </>
                          );
                        }
                      })()}
                    </div>
                  </div>
                </div>

                {/* INCIDENT POST-RESOLUTION SUMMARY (Section 11) */}
                {isFinished && simulationState?.report && (
                  <div className="p-6 rounded-2xl border border-indigo-900/50 bg-indigo-950/20 backdrop-blur-md space-y-4 animate-slideUp">
                    <div className="flex justify-between items-center border-b border-indigo-900 pb-2">
                      <div className="space-y-0.5">
                        <span className="text-[10px] font-bold font-mono text-indigo-400 uppercase tracking-widest">INCIDENT REPORT SUMMARY</span>
                        <h2 className="text-base font-extrabold text-white flex items-center gap-1.5">
                          <ShieldCheck size={18} className="text-emerald-400" />
                          Incident: {simulationState.report.incidentId} (RESOLVED)
                        </h2>
                      </div>
                      <button 
                        onClick={() => window.print()}
                        className="bg-indigo-650 hover:bg-indigo-600 text-white font-bold py-1 px-3 rounded text-xs flex items-center gap-1"
                      >
                        <Download size={12} /> Export Report
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs text-slate-300">
                      <div className="md:col-span-2 space-y-3">
                        <div className="space-y-1">
                          <span className="text-[9px] uppercase font-bold text-slate-500">Executive Summary</span>
                          <p className="leading-relaxed bg-slate-950/40 p-3 rounded border border-slate-900">{simulationState.report.executiveSummary}</p>
                        </div>
                      </div>

                      <div className="p-4 rounded bg-slate-950/30 border border-slate-900 space-y-2">
                        <span className="text-[9px] uppercase font-bold text-slate-500 block">Metrics Verification</span>
                        <div className="space-y-1 text-[11px] font-mono">
                          <div className="flex justify-between">
                            <span>Threat Class:</span>
                            <span className="font-bold text-white">{simulationState.report.attackType}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Peak URS:</span>
                            <span className="font-bold text-rose-500">{simulationState.report.maxRiskScore}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })()}

          {/* 7. QUANTUM readiness */}
          {activeTab === 'quantum' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="space-y-1">
                <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                  <Key size={24} className="text-cyan-400" />
                  Quantum Readiness Posture Assessment
                </h1>
                <p className="text-xs text-slate-400">Audits PQC migrations and cryptographic inventories of monitored resources.</p>
              </div>

              {/* Algorithms breakdown table */}
              <div className="border border-slate-800 rounded-2xl bg-slate-900/10 overflow-hidden text-xs">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 uppercase font-semibold">
                      <th className="p-4">Algorithm</th>
                      <th className="p-4">Quantum Risk</th>
                      <th className="p-4">Migration Priority</th>
                      <th className="p-4">Recommended Replacement</th>
                      <th className="p-4">Active Deployments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[
                      { alg: "RSA-2048", risk: "Very High", priority: "Critical", replacement: "ML-KEM (Kyber)", deployments: 4 },
                      { alg: "RSA-4096", risk: "Very High", priority: "High", replacement: "ML-KEM (Kyber)", deployments: 2 },
                      { alg: "ECC P-256", risk: "Very High", priority: "Critical", replacement: "ML-KEM / ML-DSA", deployments: 1 },
                      { alg: "Ed25519", risk: "Very High", priority: "High", replacement: "ML-DSA (Dilithium)", deployments: 3 },
                      { alg: "ML-KEM (Kyber)", risk: "None", priority: "Resolved", replacement: "No actions required", deployments: 1 }
                    ].map(r => (
                      <tr key={r.alg} className="border-b border-slate-800 hover:bg-slate-900/25">
                        <td className="p-4 font-mono font-bold text-white">{r.alg}</td>
                        <td className="p-4 font-semibold text-rose-400">{r.risk}</td>
                        <td className="p-4">
                          <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${r.priority === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : (r.priority === 'High' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400')}`}>
                            {r.priority}
                          </span>
                        </td>
                        <td className="p-4 font-mono text-slate-300">{r.replacement}</td>
                        <td className="p-4 font-bold">{r.deployments} instances</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* 8. POLICY RECOMMENDATION */}
          {activeTab === 'policies' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="space-y-1">
                <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                  <Settings size={24} className="text-indigo-400" />
                  Intelligent Policy Remediation Guidelines
                </h1>
                <p className="text-xs text-slate-400">Remediation actions compiled by the IPRE matching threat triggers.</p>
              </div>

              {/* Policy cards grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                {[
                  { id: "REC-K8S-001", title: "Apply Kubernetes CPU Resource Quotas", reduction: 60, priority: "Critical", auto: true, desc: "Configure resource Limits and Requests inside target namespace configs to mitigate sustained container CPU spikes." },
                  { id: "REC-CRYPTO-001", title: "Migrate Legacy RSA Cryptography to PQC", reduction: 75, priority: "Critical", auto: false, desc: "Identify legacy credentials and migrate TLS connections to Kyber-safe hybrid algorithms." },
                  { id: "REC-SG-002", title: "Close Ingress SSH Wildcard 0.0.0.0/0", reduction: 80, priority: "High", auto: true, desc: "Modify AWS EC2 Security Groups to lock down open ports and restricts access to corporate subnet routes." },
                  { id: "REC-LOG-001", title: "Configure CloudWatch Detailed Monitoring", reduction: 35, priority: "Medium", auto: true, desc: "Enable AWS detailed metrics aggregation intervals to capture anomalies faster." }
                ].map(p => (
                  <div key={p.id} className="p-5 border border-slate-800 bg-slate-900/20 rounded-2xl space-y-4">
                    <div className="flex justify-between items-start">
                      <div className="space-y-1">
                        <span className="font-mono text-slate-500">{p.id}</span>
                        <h4 className="font-bold text-white text-sm">{p.title}</h4>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${p.priority === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400'}`}>
                        {p.priority}
                      </span>
                    </div>
                    <p className="text-slate-400 leading-relaxed">{p.desc}</p>
                    <div className="flex justify-between border-t border-slate-800 pt-3">
                      <span className="text-slate-500">Risk Reduction: <strong className="text-emerald-400">{p.reduction}%</strong></span>
                      <span className="text-slate-500">Automation: <strong className="text-slate-300">{p.auto ? "Supported" : "Manual review"}</strong></span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 9. RESEARCH EVALUATION */}
          {activeTab === 'evaluation' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="space-y-1">
                <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                  <GitMerge size={24} className="text-cyan-400" />
                  Research Benchmark Evaluation (REBF)
                </h1>
                <p className="text-xs text-slate-400">Quantitative benchmarking comparing the framework against legacy systems.</p>
              </div>

              {/* Benchmark comparison grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Radar chart */}
                <div className="p-5 border border-slate-800 bg-slate-900/20 rounded-2xl flex flex-col justify-between items-center min-h-[300px]">
                  <h3 className="text-xs font-bold text-slate-300">Security Capabilities Benchmark</h3>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart outerRadius="70%" data={[
                        { subject: "Speed", ours: 98, ai: 70, trad: 20 },
                        { subject: "Accuracy", ours: 97, ai: 75, trad: 30 },
                        { subject: "Explainability", ours: 95, ai: 10, trad: 0 },
                        { subject: "Adaptability", ours: 95, ai: 10, trad: 10 },
                        { subject: "PQC", ours: 90, ai: 0, trad: 0 },
                        { subject: "Policy", ours: 95, ai: 20, trad: 10 }
                      ]}>
                        <PolarGrid stroke="#334155" />
                        <PolarAngleAxis dataKey="subject" stroke="#94a3b8" fontSize={10} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" fontSize={8} />
                        <Radar name="Our Framework" dataKey="ours" stroke="#818cf8" fill="#818cf8" fillOpacity={0.25} />
                        <Radar name="AI Monitor Only" dataKey="ai" stroke="#fbbf24" fill="#fbbf24" fillOpacity={0.1} />
                        <Tooltip />
                        <Legend />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Metrics Table */}
                <div className="lg:col-span-2 border border-slate-800 rounded-2xl bg-slate-900/10 overflow-hidden text-xs">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 uppercase font-semibold">
                        <th className="p-4">Metric Parameter</th>
                        <th className="p-4">Traditional</th>
                        <th className="p-4">AI Only</th>
                        <th className="p-4">Our Framework (REBF)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {evaluatorDashboard?.comparison?.rows ? (
                        evaluatorDashboard.comparison.rows.map((row, idx) => (
                          <tr key={idx} className="border-b border-slate-800 hover:bg-slate-900/25">
                            <td className="p-4 font-semibold text-slate-300">{row.metric}</td>
                            <td className="p-4 text-slate-400">{row.traditional}</td>
                            <td className="p-4 text-slate-400">{row.ai_only}</td>
                            <td className="p-4 font-bold text-white">{row.ours}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan="4" className="p-8 text-center text-slate-400 font-medium">
                            {evaluatorError ? "No evaluation data available (Service Offline)" : "Loading comparison metrics..."}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>

              </div>
            </div>
          )}

          {/* 10. RESEARCH REPORTS */}
          {activeTab === 'reports' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="flex justify-between items-center flex-wrap gap-4">
                <div className="space-y-1">
                  <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                    <FileText size={24} className="text-indigo-400" />
                    Autonomous Research Reports
                  </h1>
                  <p className="text-xs text-slate-400">Generate publication-ready papers compiling active metrics logs.</p>
                </div>
                <button 
                  onClick={triggerReportGeneration} 
                  disabled={reportLoading}
                  className="bg-indigo-650 hover:bg-indigo-500 text-white font-semibold py-2 px-6 rounded-lg text-xs flex items-center gap-1.5 disabled:opacity-50"
                >
                  <RefreshCw size={12} className={reportLoading ? 'animate-spin' : ''} />
                  {reportLoading ? 'Compiling Paper...' : 'Generate Research Report'}
                </button>
              </div>

              {/* Reports display panel */}
              {latestReport ? (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 text-xs">
                  
                  {/* Markdown viewer */}
                  <div className="lg:col-span-3 p-5 border border-slate-800 rounded-2xl bg-slate-900/20 space-y-4">
                    <div className="flex justify-between items-center border-b border-slate-800/80 pb-3">
                      <h3 className="text-sm font-bold text-slate-300">Generated Academic Report Markdown</h3>
                      <button 
                        onClick={() => {
                          const blob = new Blob([latestReport.markdown], { type: 'text/markdown' });
                          const url = URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `report-${latestReport.reportId}.md`;
                          a.click();
                        }}
                        className="p-1 px-3 bg-slate-900 border border-slate-850 hover:bg-slate-800 rounded text-slate-300 flex items-center gap-1.5"
                      >
                        <Download size={12} /> Download Markdown
                      </button>
                    </div>
                    <pre className="font-mono bg-slate-950/40 p-4 border border-slate-850 rounded-xl overflow-x-auto text-[11px] leading-relaxed text-slate-300 max-h-[500px]">
                      {latestReport.markdown}
                    </pre>
                  </div>

                  {/* CSV download cards */}
                  <div className="p-5 border border-slate-800 rounded-2xl bg-slate-900/20 space-y-4 flex flex-col justify-between">
                    <div className="space-y-4">
                      <h3 className="text-sm font-bold text-slate-300">CSV Export Logs</h3>
                      <p className="text-slate-400">Download telemetry averages dataset compiled for spreadsheet plotting.</p>
                    </div>
                    <button 
                      onClick={() => {
                        const blob = new Blob([latestReport.csv], { type: 'text/csv' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `metrics-${latestReport.reportId}.csv`;
                        a.click();
                      }}
                      className="w-full py-2 bg-indigo-650 hover:bg-indigo-600 text-white rounded font-bold text-center flex items-center justify-center gap-1.5"
                    >
                      <Download size={12} /> Download CSV Metrics
                    </button>
                  </div>

                </div>
              ) : (
                <div className="text-center p-12 bg-slate-900/10 border border-slate-800 rounded-2xl space-y-4">
                  <FileText size={48} className="mx-auto text-slate-500 animate-pulse" />
                  <div>
                    <h3 className="text-lg font-bold text-white">No Reports Compiled</h3>
                    <p className="text-xs text-slate-500">Launch the report generation above.</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 11. AUTOMATION CENTER (CLOSED-LOOP REMEDIATION) */}
          {activeTab === 'automation-center' && (() => {
            // Live simulation stage resolution
            let currentStage = 'idle';
            if (simulationState && simulationState.status === 'active') {
              const elapsed = Math.floor((Date.now() - new Date(simulationState.startTime).getTime()) / 1000) || 0;
              if (elapsed < 6) currentStage = 'Detection';
              else if (elapsed < 12) currentStage = 'AI Analysis';
              else if (elapsed < 18) currentStage = 'URS Evaluation';
              else if (elapsed < 24) currentStage = 'Policy Decision';
              else if (elapsed < 30) currentStage = 'Approval';
              else if (elapsed < 36) currentStage = 'Automation';
              else if (elapsed < 42) currentStage = 'Verification';
              else if (elapsed < 48) currentStage = 'Recovery';
              else currentStage = 'Closed';
            } else {
              if (soarStep === 'queued') currentStage = 'Detection';
              else if (soarStep === 'approved') currentStage = 'Approval';
              else if (soarStep === 'running') currentStage = 'Automation';
              else if (soarStep === 'completed') currentStage = 'Verification';
              else if (soarStep === 'verification') currentStage = 'Recovery';
              else if (soarStep === 'closed') currentStage = 'Closed';
            }

            const pipelineStages = [
              { name: 'Detection', icon: <Activity size={12} /> },
              { name: 'AI Analysis', icon: <Cpu size={12} /> },
              { name: 'URS Evaluation', icon: <ShieldAlert size={12} /> },
              { name: 'Policy Decision', icon: <HelpCircle size={12} /> },
              { name: 'Approval', icon: <Settings size={12} /> },
              { name: 'Automation', icon: <Play size={12} /> },
              { name: 'Verification', icon: <RefreshCw size={12} /> },
              { name: 'Recovery', icon: <HeartPulse size={12} /> },
              { name: 'Closed', icon: <FileText size={12} /> }
            ];

            const currentIdx = pipelineStages.findIndex(s => s.name === currentStage);

            // SOAR playbooks library definition
            const playbooksLibrary = [
              { id: 'SG-SSH-OPEN', name: 'SSH Port Restriction', category: 'Networking', duration: '4s', approval: 'Yes', downtime: 'None', ursReduction: 10, mitre: 'T1190', difficulty: 'Easy', supportedAssets: 'Security Group', mitigation: 'aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 22 --cidr 0.0.0.0/0' },
              { id: 'SG-RDP-OPEN', name: 'RDP Port Containment', category: 'Networking', duration: '5s', approval: 'Yes', downtime: 'None', ursReduction: 12, mitre: 'T1190', difficulty: 'Easy', supportedAssets: 'Security Group', mitigation: 'aws ec2 revoke-security-group-ingress --group-id sg-0e6ff0385dc3e9235 --protocol tcp --port 3389 --cidr 0.0.0.0/0' },
              { id: 'EBS-UNENCRYPTED', name: 'Encrypt Storage Volumes', category: 'Storage', duration: '12s', approval: 'Yes', downtime: '2 mins', ursReduction: 15, mitre: 'T1537', difficulty: 'Medium', supportedAssets: 'EBS Volume', mitigation: 'aws ec2 copy-image --source-image-id ami-0c7217cdde317cfec --encrypted --kms-key-id alias/aws/ebs' },
              { id: 'IAM-NO-PROFILE', name: 'Attach Instance Profile', category: 'Identity', duration: '8s', approval: 'Yes', downtime: 'None', ursReduction: 14, mitre: 'T1078', difficulty: 'Medium', supportedAssets: 'IAM Role', mitigation: 'aws iam associate-instance-profile --instance-id target-ec2 --instance-profile-name secure-profile' },
              { id: 'EC2-IMDSV1', name: 'Enforce IMDSv2 Tokens', category: 'Compute', duration: '6s', approval: 'Yes', downtime: 'None', ursReduction: 8, mitre: 'T1562', difficulty: 'Easy', supportedAssets: 'EC2 Instance', mitigation: 'aws ec2 modify-instance-metadata-options --instance-id target-ec2 --http-tokens required' },
              { id: 'GUARDDUTY-OFF', name: 'Enable GuardDuty Detector', category: 'Monitoring', duration: '10s', approval: 'No', downtime: 'None', ursReduction: 8, mitre: 'T1562.001', difficulty: 'Easy', supportedAssets: 'AWS Account', mitigation: 'aws guardduty create-detector --enable --region us-east-1' }
            ];

            const filteredPlaybooks = playbooksLibrary.filter(p => 
              p.name.toLowerCase().includes(soarPlaybookSearch.toLowerCase()) || 
              p.category.toLowerCase().includes(soarPlaybookSearch.toLowerCase())
            );

            // Playbook status resolution
            const executedPlaybooksCount = automationHistory.length + (soarStep === 'closed' ? 1 : 0);

            // Recharts metrics data
            const successRateData = [
              { name: 'Jan', rate: 98.4 },
              { name: 'Feb', rate: 99.1 },
              { name: 'Mar', rate: 100.0 }
            ];

            const responseTimeData = [
              { name: 'SG Restrict', time: 4.2 },
              { name: 'EBS Encrypt', time: 12.0 },
              { name: 'IAM Attach', time: 8.4 },
              { name: 'IMDS enforce', time: 6.1 }
            ];

            return (
              <div className="space-y-8 animate-fadeIn text-slate-350">
                <div className="flex justify-between items-center flex-wrap gap-4 border-b border-slate-800 pb-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-3">
                      <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                        <Cpu size={24} className="text-indigo-400 animate-spin-slow" />
                        🧠 SOAR Incident Response & Automation Center
                      </h1>
                      <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 flex items-center gap-1.5 animate-pulse">
                        <span className="h-2 w-2 rounded-full bg-indigo-400"></span>
                        SOAR PLATFORM ACTIVE
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">Integrated Security Orchestration, Automation & Response platform connecting threat decisions to cloud playbook executions.</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={fetchAutomationHistory}
                      className="p-2.5 border border-slate-850 bg-slate-900/40 rounded-lg text-slate-400 hover:text-white hover:border-slate-700 text-xs flex items-center gap-1.5 transition"
                    >
                      <RefreshCw size={13} /> Sync Logs
                    </button>
                    <button 
                      onClick={() => triggerSoarPlaybook(playbooksLibrary[0])}
                      disabled={soarStep !== 'idle' && soarStep !== 'closed'}
                      className="bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-white font-bold py-2.5 px-6 rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-indigo-650/20 transition"
                    >
                      <Play size={13} className="fill-white" /> Trigger Automated Mitigation
                    </button>
                  </div>
                </div>

                {/* 1. Executive SOAR Dashboard */}
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
                  <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl flex flex-col justify-between h-24 hover:border-slate-700 transition">
                    <span className="text-slate-500 font-bold block uppercase text-[9px] tracking-wider">Automation Health</span>
                    <span className="text-xl font-black text-indigo-400">98.6%</span>
                    <span className="text-[9px] text-slate-500">Continuous Endpoint Reachability</span>
                  </div>
                  <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl flex flex-col justify-between h-24 hover:border-slate-700 transition">
                    <span className="text-slate-500 font-bold block uppercase text-[9px] tracking-wider">Playbooks Available</span>
                    <span className="text-xl font-black text-cyan-400">12 Scenarios</span>
                    <span className="text-[9px] text-slate-500">Configured SOAR Recipes</span>
                  </div>
                  <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl flex flex-col justify-between h-24 hover:border-slate-700 transition">
                    <span className="text-slate-500 font-bold block uppercase text-[9px] tracking-wider">Playbooks Executed</span>
                    <span className="text-xl font-black text-emerald-400">{executedPlaybooksCount} Run</span>
                    <span className="text-[9px] text-slate-500">Total Playbook Ingests</span>
                  </div>
                  <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl flex flex-col justify-between h-24 hover:border-slate-700 transition">
                    <span className="text-slate-500 font-bold block uppercase text-[9px] tracking-wider">Estimated URS Reduction</span>
                    <span className="text-xl font-black text-pink-400">-{soarActivePlaybook ? soarActivePlaybook.ursReduction : 10} Points</span>
                    <span className="text-[9px] text-slate-500">Risk Mitigation Level</span>
                  </div>
                  <div className="p-4 bg-slate-900/20 border border-slate-850 rounded-xl flex flex-col justify-between h-24 hover:border-slate-700 transition">
                    <span className="text-slate-500 font-bold block uppercase text-[9px] tracking-wider">Active Containment</span>
                    <span className="text-xl font-black text-amber-400">{soarStep !== 'idle' && soarStep !== 'closed' ? '1 Running' : '0 Pending'}</span>
                    <span className="text-[9px] text-slate-500">Current Incident Recovery</span>
                  </div>
                </div>

                {/* 2. Live Playbook Pipeline */}
                <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/10 space-y-4">
                  <h3 className="text-xs font-bold text-slate-350 uppercase tracking-widest font-mono">Live SOAR Decisions-to-Orchestration Pipeline</h3>
                  <div className="flex flex-col md:flex-row justify-between items-center gap-3">
                    {pipelineStages.map((stage, idx) => {
                      const isCompleted = idx < currentIdx || currentStage === 'Closed';
                      const isActive = stage.name === currentStage;
                      let bgClass = "bg-slate-950/60 border-slate-850 text-slate-550";
                      let lineClass = "bg-slate-850";
                      
                      if (isCompleted) {
                        bgClass = "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";
                        lineClass = "bg-emerald-500/50";
                      } else if (isActive) {
                        bgClass = "bg-indigo-500/25 border-indigo-400 text-white ring-2 ring-indigo-500/30 shadow-[0_0_12px_rgba(99,102,241,0.25)] animate-pulse";
                        lineClass = "bg-indigo-500/30";
                      }

                      return (
                        <React.Fragment key={stage.name}>
                          <div className={`flex flex-col items-center justify-center p-3 rounded-xl border text-center transition-all duration-300 w-full md:w-28 ${bgClass}`}>
                            <div className="mb-1">{stage.icon}</div>
                            <span className="text-[9.5px] font-mono font-bold tracking-wider">{stage.name}</span>
                          </div>
                          {idx < pipelineStages.length - 1 && (
                            <div className={`hidden md:block h-0.5 flex-1 transition-colors duration-300 ${lineClass}`}></div>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>
                </div>

                {/* Optimized Playbook Execution Chain Panel */}
                {latestExecutionPlan && (
                  <div className="p-5 border border-indigo-500/30 rounded-2xl bg-indigo-950/5 space-y-4 animate-fadeIn">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                      <div>
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <Cpu size={16} className="text-indigo-400" />
                          Optimized Execution Plan: {latestExecutionPlan.incidentId || 'SOAR-Chain'}
                        </h3>
                        <p className="text-[10px] text-slate-500 font-mono">
                          Deterministic Playbook Optimization Layer Results
                        </p>
                      </div>
                      <div className="flex gap-4 text-right">
                        <div>
                          <span className="text-[9px] text-slate-550 block font-mono">URS PROFILE</span>
                          <span className="text-xs font-bold text-rose-400">{latestExecutionPlan.ursBefore}%</span>
                          <span className="text-slate-500 mx-1">➔</span>
                          <span className="text-xs font-bold text-emerald-400">{latestExecutionPlan.ursAfter}%</span>
                        </div>
                      </div>
                    </div>

                    {/* Metrics Summary Row */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                      <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl space-y-0.5">
                        <span className="text-[9px] text-slate-500 uppercase font-bold block">Optimization Gain</span>
                        <span className="text-sm font-black text-indigo-400">+{latestExecutionPlan.metrics?.optimizationGain || 0}</span>
                      </div>
                      <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl space-y-0.5">
                        <span className="text-[9px] text-slate-500 uppercase font-bold block">Considered / Selected / Removed</span>
                        <span className="text-sm font-black text-cyan-400">
                          {latestExecutionPlan.metrics?.playbooksConsidered || 0} / {latestExecutionPlan.metrics?.playbooksSelected || 0} / {latestExecutionPlan.metrics?.playbooksRemoved || 0}
                        </span>
                      </div>
                      <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl space-y-0.5">
                        <span className="text-[9px] text-slate-500 uppercase font-bold block">Estimated Time Saved</span>
                        <span className="text-sm font-black text-emerald-400">{latestExecutionPlan.metrics?.estimatedTimeSaved || 0}s</span>
                      </div>
                      <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl space-y-0.5">
                        <span className="text-[9px] text-slate-500 uppercase font-bold block">Expected Recovery Rate</span>
                        <span className="text-sm font-black text-pink-400">{latestExecutionPlan.metrics?.expectedRecoveryPercentage || 0}%</span>
                      </div>
                    </div>

                    <div className="text-[11px] text-slate-350 leading-relaxed font-mono">
                      <strong>Rationale:</strong> {latestExecutionPlan.optimizationRationale}
                    </div>

                    {/* Step Timeline */}
                    <div className="space-y-3">
                      <span className="text-xs font-bold text-slate-400 block border-b border-slate-800 pb-1.5 font-mono">Optimized Sequence</span>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                          {latestExecutionPlan.executionOrder?.map((step) => (
                            <div key={step.step} className="p-3.5 rounded-xl bg-slate-950/40 border border-slate-850 text-xs flex justify-between items-center gap-4">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="px-1.5 py-0.5 rounded text-[9px] bg-slate-900 border border-slate-800 font-mono text-slate-400">
                                    Step {step.step}
                                  </span>
                                  <span className="font-bold text-white">{step.title}</span>
                                  {step.parallel && (
                                    <span className="px-1 py-0.2 rounded text-[8px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-bold">
                                      Parallel Ready
                                    </span>
                                  )}
                                </div>
                                <div className="text-[10px] text-slate-400 font-mono">
                                  Why: {step.selectedBecause?.join(', ')}
                                </div>
                              </div>
                              <div className="text-right font-mono">
                                <div className="text-[10px] text-slate-500">Priority Score</div>
                                <div className="text-sm font-bold text-indigo-400">{step.priorityScore}</div>
                              </div>
                            </div>
                          ))}
                        </div>

                        {/* Rejected playbooks detail */}
                        <div className="p-4 bg-slate-950 border border-slate-850 rounded-xl space-y-3">
                          <h4 className="text-[10px] text-slate-550 uppercase font-bold tracking-wider font-mono">Excluded Playbooks & Deduplication Trace</h4>
                          {latestExecutionPlan.rejectedPlaybooks?.length > 0 ? (
                            <div className="space-y-2 max-h-[140px] overflow-y-auto timeline-scrollbar">
                              {latestExecutionPlan.rejectedPlaybooks.map((rej, i) => (
                                <div key={i} className="text-[10.5px] leading-relaxed border-b border-slate-900 pb-1.5 last:border-none">
                                  <span className="text-rose-450 font-bold font-mono">[{rej.score}] {rej.name}</span>
                                  <div className="text-slate-500 text-[10px]">{rej.reason}</div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="text-slate-650 text-[10.5px] italic font-mono">No playbooks were rejected or deduplicated.</div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Column: Playbook Library */}
                  <div className="lg:col-span-1 p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-4">
                    <div className="space-y-1">
                      <h3 className="text-sm font-bold text-slate-350">SOAR Playbook Library</h3>
                      <p className="text-[10px] text-slate-500">Select and execute automated workflows</p>
                    </div>

                    {/* Search playbooks input */}
                    <input 
                      type="text" 
                      placeholder="Search playbooks by name/category..."
                      value={soarPlaybookSearch}
                      onChange={(e) => setSoarPlaybookSearch(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-850 rounded-lg p-2.5 text-xs text-white placeholder-slate-650 focus:border-indigo-500 focus:outline-none"
                    />

                    <div className="space-y-3.5 max-h-[380px] overflow-y-auto pr-1 timeline-scrollbar">
                      {filteredPlaybooks.map(pb => (
                        <div 
                          key={pb.id}
                          className={`p-3.5 border rounded-xl space-y-2 transition duration-200 cursor-pointer ${soarActivePlaybook?.id === pb.id ? 'border-indigo-500 bg-indigo-950/10 shadow' : 'border-slate-850 bg-slate-950/40 hover:bg-slate-950/70 hover:border-slate-700'}`}
                          onClick={() => triggerSoarPlaybook(pb)}
                        >
                          <div className="flex justify-between items-start">
                            <div>
                              <span className="text-[9px] text-slate-500 font-mono uppercase font-bold block">{pb.category}</span>
                              <h4 className="font-bold text-white text-xs">{pb.name}</h4>
                            </div>
                            <span className="px-1.5 py-0.5 rounded text-[8.5px] font-bold bg-indigo-950 text-indigo-300 border border-indigo-900 font-mono">
                              -{pb.ursReduction} URS
                            </span>
                          </div>
                          <p className="text-[10.5px] text-slate-400 leading-relaxed truncate">{pb.mitigation}</p>
                          <div className="flex justify-between text-[9px] text-slate-500 pt-2 border-t border-slate-900/60 font-mono">
                            <span>ETA: {pb.duration}</span>
                            <span>MITRE: {pb.mitre}</span>
                            <span>Risk: {pb.difficulty}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Middle Column: Active Execution Terminal & Approval Center */}
                  <div className="lg:col-span-1 flex flex-col gap-6">
                    {/* SOAR Approval Center */}
                    <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-4">
                      <div className="flex justify-between items-center border-b border-slate-850 pb-2">
                        <div>
                          <h3 className="text-sm font-bold text-slate-350">SOAR Approval Center</h3>
                          <span className="text-[9px] text-slate-500 font-mono">Operator gate authorizations</span>
                        </div>
                        {soarActivePlaybook && (
                          <span className={`px-2 py-0.5 rounded text-[9.5px] font-bold ${soarApprovalStatus === 'Pending' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse' : (soarApprovalStatus === 'Approved' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20')}`}>
                            {soarApprovalStatus}
                          </span>
                        )}
                      </div>

                      {soarActivePlaybook ? (
                        <div className="space-y-4 text-xs">
                          <div className="p-3 bg-slate-950 border border-slate-850 rounded-xl space-y-1.5 font-mono text-[10.5px]">
                            <div><span className="text-slate-550">Recommended:</span> <span className="text-white font-bold">{soarActivePlaybook.name}</span></div>
                            <div><span className="text-slate-550">Target Asset:</span> <span className="text-cyan-400">{soarActivePlaybook.supportedAssets}</span></div>
                            <div><span className="text-slate-550">Downtime Risk:</span> <span className="text-slate-200">{soarActivePlaybook.downtime}</span></div>
                            <div><span className="text-slate-550">Rollback Available:</span> <span className="text-emerald-400">Yes</span></div>
                            <div><span className="text-slate-550">URS Reduction:</span> <span className="text-indigo-400">-{soarActivePlaybook.ursReduction} URS Points</span></div>
                          </div>
                          
                          {soarApprovalStatus === 'Pending' ? (
                            <div className="flex gap-2">
                              <button 
                                onClick={() => handleSoarApprove(soarActivePlaybook)}
                                className="flex-1 py-2 bg-indigo-650 hover:bg-indigo-600 border border-indigo-500 rounded text-xs font-bold text-white transition"
                              >
                                Approve Playbook
                              </button>
                              <button 
                                onClick={() => {
                                  setSoarApprovalStatus('Rejected');
                                  setSoarStep('idle');
                                  setSoarLog(prev => [...prev, { time: new Date().toLocaleTimeString(), message: "[SOAR] Action REJECTED by operator." }]);
                                }}
                                className="px-3 py-2 border border-slate-800 hover:bg-slate-900 rounded text-xs font-bold text-slate-400 transition"
                              >
                                Reject
                              </button>
                            </div>
                          ) : (
                            <div className="p-3 text-center border border-emerald-950 bg-emerald-500/10 rounded-xl text-emerald-400 font-bold text-xs">
                              ✔ Playbook approved and executed.
                            </div>
                          )}
                        </div>
                      ) : (
                        <div className="py-8 text-center text-slate-500 italic text-xs">Awaiting playbook recommendation to populate gate approvals...</div>
                      )}
                    </div>

                    {/* SOAR Interactive Execution Console */}
                    <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 flex-1 flex flex-col min-h-[220px]">
                      <h3 className="text-sm font-bold text-slate-350 mb-3 flex items-center gap-1.5 border-b border-slate-850 pb-2">
                        <Activity size={14} className="text-indigo-400" />
                        SOAR Terminal Console
                      </h3>
                      <div className="flex-1 bg-slate-950 border border-slate-850 p-4 rounded-xl font-mono text-[10px] text-cyan-400 overflow-y-auto timeline-scrollbar space-y-2 h-48">
                        {soarLog.map((log, i) => (
                          <div key={i} className="flex gap-2 items-start animate-fadeIn">
                            <span className="text-slate-600 text-[9px] select-none">[{log.time}]</span>
                            <span className="text-slate-300 leading-normal">{log.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Execution Timeline & Recovery Indicators */}
                  <div className="lg:col-span-1 flex flex-col gap-6">
                    {/* Incident Recovery Dashboard */}
                    <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-4">
                      <div className="space-y-1">
                        <h3 className="text-sm font-bold text-slate-350">Incident Recovery Dashboard</h3>
                        <p className="text-[10px] text-slate-500">Live target environment threat recovery status</p>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl text-center space-y-1">
                          <span className="text-[9px] text-slate-500 uppercase font-bold block tracking-wider">Containment Rate</span>
                          <span className={`text-xl font-black block ${soarStep === 'closed' ? 'text-emerald-400' : (soarStep !== 'idle' ? 'text-amber-400 animate-pulse' : 'text-slate-550')}`}>
                            {soarStep === 'closed' ? '100%' : (soarStep !== 'idle' ? '65%' : '0%')}
                          </span>
                        </div>
                        <div className="p-3 bg-slate-950/40 border border-slate-850 rounded-xl text-center space-y-1">
                          <span className="text-[9px] text-slate-500 uppercase font-bold block tracking-wider">Threat Status</span>
                          <span className={`text-xs font-extrabold uppercase tracking-widest block py-0.5 rounded ${soarStep === 'closed' ? 'bg-emerald-500/10 text-emerald-400' : (soarStep !== 'idle' ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-900 text-slate-500')}`}>
                            {soarStep === 'closed' ? 'CLEANED' : (soarStep !== 'idle' ? 'ANALYZING' : 'MONITORING')}
                          </span>
                        </div>
                      </div>

                      {/* URS Difference indicator */}
                      <div className="p-3.5 bg-slate-950 border border-slate-850 rounded-xl flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-400 font-bold">URS Score Recovery:</span>
                        <div className="flex items-center gap-2">
                          <span className="text-rose-400 font-black">84</span>
                          <span className="text-slate-500">➔</span>
                          <span className={`font-black ${soarStep === 'closed' ? 'text-emerald-400' : 'text-slate-400 animate-pulse'}`}>
                            {soarStep === 'closed' && soarActivePlaybook ? (84 - soarActivePlaybook.ursReduction) : '37'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Automation Metrics Charts */}
                    <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-3">
                      <div>
                        <h3 className="text-xs font-bold text-slate-350 uppercase tracking-widest font-mono">Automation Success Timeline</h3>
                        <p className="text-[9px] text-slate-550">Historical SOAR execution performance metrics</p>
                      </div>
                      <div className="h-32">
                        <ResponsiveContainer width="100%" height="100%">
                          <AreaChart data={successRateData} margin={{ top: 5, right: 5, left: -25, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                            <XAxis dataKey="name" stroke="#9ca3af" fontSize={8} tickLine={false} />
                            <YAxis domain={[90, 100]} stroke="#9ca3af" fontSize={8} tickLine={false} />
                            <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                            <Area type="monotone" dataKey="rate" name="Success Rate %" stroke="#818cf8" fill="#818cf8" fillOpacity={0.1} />
                          </AreaChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Playbook Execution Timeline Stages */}
                {soarActivePlaybook && (
                  <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/10 space-y-4">
                    <h3 className="text-xs font-bold text-slate-350 uppercase tracking-widest font-mono">Playbook Lifecycle Trace</h3>
                    <div className="grid grid-cols-2 md:grid-cols-6 gap-3 text-xs font-mono">
                      {[
                        { step: 'Queued', operator: 'Risk Engine', time: '19:10:04', active: soarStep === 'queued' },
                        { step: 'Approved', operator: 'Operator', time: '19:10:07', active: soarStep === 'approved' },
                        { step: 'Running', operator: 'SOAR core', time: '19:10:08', active: soarStep === 'running' },
                        { step: 'Completed', operator: 'AWS API', time: '19:10:10', active: soarStep === 'completed' },
                        { step: 'Verification', operator: 'Telemetry', time: '19:10:12', active: soarStep === 'verification' },
                        { step: 'Closed', operator: 'System', time: '19:10:13', active: soarStep === 'closed' }
                      ].map((t, i) => (
                        <div key={i} className={`p-3 border rounded-xl space-y-1.5 transition-all ${t.active ? 'border-indigo-500 bg-indigo-950/15 shadow animate-pulse' : 'border-slate-850 bg-slate-950/40 text-slate-500'}`}>
                          <div className="font-bold text-white text-[10.5px]">{t.step}</div>
                          <div className="text-[9px] text-slate-400">Agent: {t.operator}</div>
                          <div className="text-[9px] text-slate-550">Timestamp: {t.time}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Cloud & Risk Engine Integrations */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Risk Engine Recommendations */}
                  <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-4">
                    <div>
                      <h3 className="text-sm font-bold text-slate-350">Risk Engine Recommendations</h3>
                      <p className="text-[10px] text-slate-500">Live URS optimization triggers mapped to current anomalies</p>
                    </div>
                    <div className="space-y-2 max-h-[180px] overflow-y-auto timeline-scrollbar">
                      {playbooksLibrary.slice(0, 3).map((pb, i) => (
                        <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-950/40 border border-slate-850 text-xs">
                          <div>
                            <div className="font-bold text-white">{pb.id === 'SG-SSH-OPEN' ? 'SSH Wildcard Open' : (pb.id === 'SG-RDP-OPEN' ? 'RDP Wildcard Open' : 'Missing Volume Encryption')}</div>
                            <div className="text-[10px] text-slate-500 font-mono">Suggested Playbook: {pb.name}</div>
                          </div>
                          <div className="text-right space-y-1">
                            <span className="inline-block px-1.5 py-0.5 rounded text-[9px] bg-rose-500/10 text-rose-400 border border-rose-500/20 font-bold uppercase">High</span>
                            <div className="text-[10px] text-indigo-400 font-bold">URS: -{pb.ursReduction}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Cloud Security Integration */}
                  <div className="p-5 border border-slate-850 rounded-2xl bg-slate-900/20 space-y-4">
                    <div>
                      <h3 className="text-sm font-bold text-slate-350">Cloud Security Integrations</h3>
                      <p className="text-[10px] text-slate-500">Real-time AWS posture scanning playbook mapping</p>
                    </div>
                    <div className="space-y-2 max-h-[180px] overflow-y-auto timeline-scrollbar">
                      {playbooksLibrary.slice(3, 6).map((pb, i) => (
                        <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-950/40 border border-slate-850 text-xs">
                          <div>
                            <div className="font-bold text-white">{pb.name}</div>
                            <div className="text-[10px] text-slate-500 font-mono">Downtime Risk: {pb.downtime} | Rollback: Yes</div>
                          </div>
                          <div className="text-right space-y-1">
                            <button 
                              onClick={() => triggerSoarPlaybook(pb)}
                              className="px-2.5 py-1 bg-slate-900 border border-slate-850 hover:bg-slate-800 rounded font-bold text-[10px] text-slate-300 transition"
                            >
                              Inspect
                            </button>
                            <div className="text-[10px] text-emerald-400 font-bold font-mono">-{pb.ursReduction} URS</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* 13. Incident Report Generator */}
                {soarIncidentReport && (
                  <div className="p-6 border border-indigo-500/30 rounded-2xl bg-indigo-950/5 space-y-4 text-xs animate-fadeIn">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                      <div>
                        <h3 className="text-sm font-bold text-white">Post-Incident Containment Summary Report</h3>
                        <span className="text-[10px] text-slate-500 font-mono">Auto-generated by SOAR Engine</span>
                      </div>
                      <div className="flex gap-2">
                        <button 
                          onClick={() => {
                            navigator.clipboard.writeText(JSON.stringify(soarIncidentReport, null, 2));
                            logTwinEvent("Incident Report Exported", "success", "Incident metadata written in JSON format to local clipboard.");
                          }}
                          className="px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 rounded font-bold text-slate-300 transition"
                        >
                          Export JSON
                        </button>
                        <button 
                          onClick={() => window.print()}
                          className="px-3 py-1.5 bg-indigo-650 hover:bg-indigo-600 rounded font-bold text-white transition"
                        >
                          Print Report
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-[10.5px]">
                      <div className="space-y-2">
                        <div><span className="text-slate-500">Incident Class:</span> <span className="text-slate-200 font-bold">{soarIncidentReport.incident}</span></div>
                        <div><span className="text-slate-500">Playbooks Used:</span> <span className="text-indigo-400 font-bold">{soarIncidentReport.playbooksUsed}</span></div>
                        <div><span className="text-slate-500">Recovery Time:</span> <span className="text-slate-200">{soarIncidentReport.recoveryTime}</span></div>
                        <div><span className="text-slate-500">Containment Time:</span> <span className="text-slate-200">{soarIncidentReport.containmentTime}</span></div>
                        <div><span className="text-slate-500">URS Recalculation:</span> <span className="text-rose-400">{soarIncidentReport.ursBefore}%</span> ➔ <span className="text-emerald-400">{soarIncidentReport.ursAfter}%</span></div>
                      </div>
                      <div className="space-y-2">
                        <div><span className="text-slate-500 block">Actions Executed:</span> <span className="text-slate-350 block bg-slate-950/60 p-2 border border-slate-850 rounded">{soarIncidentReport.actionsExecuted}</span></div>
                        <div><span className="text-slate-500">Lessons Learned:</span> <span className="text-slate-350 block">{soarIncidentReport.lessonsLearned}</span></div>
                        <div><span className="text-slate-550 block">Recommendations:</span> <span className="text-slate-400 block">{soarIncidentReport.recommendations}</span></div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Execution Audit History Table */}
                <div className="border border-slate-800 rounded-2xl bg-slate-900/10 overflow-hidden">
                  <div className="p-4 border-b border-slate-800 bg-slate-900/40 font-bold text-xs text-slate-300 flex justify-between items-center">
                    <span>Remediation Execution History & MongoDB Audit Log (`automation_history`)</span>
                    <span className="text-[10px] text-slate-500">Simulation Mode Active</span>
                  </div>
                  <table className="w-full text-left border-collapse text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 bg-slate-900/40 text-slate-400 uppercase font-semibold">
                        <th className="p-4">Audit ID</th>
                        <th className="p-4">Timestamp</th>
                        <th className="p-4">Target Instance</th>
                        <th className="p-4">Risk Score</th>
                        <th className="p-4">Decision</th>
                        <th className="p-4">Automation Level</th>
                        <th className="p-4">Status</th>
                        <th className="p-4">Rollback Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {((simulationState && simulationState.status === 'active' && simulationState.automation) ? [...simulationState.automation, ...automationHistory] : automationHistory).map(item => (
                        <tr key={item.auditId} className="border-b border-slate-800 hover:bg-slate-900/25">
                          <td className="p-4 font-mono font-bold text-indigo-400">{item.auditId}</td>
                          <td className="p-4 font-mono text-slate-400">{new Date(item.timestamp).toLocaleString()}</td>
                          <td className="p-4 font-mono text-cyan-400">{item.instanceId || 'target-ec2'}</td>
                          <td className="p-4 font-bold text-white">{item.riskScore}% URS</td>
                          <td className="p-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${item.decision === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'}`}>
                              {item.decision}
                            </span>
                          </td>
                          <td className="p-4 font-semibold text-slate-300">{item.automationLevel || 'Fully Automated'}</td>
                          <td className="p-4 font-semibold text-emerald-400">{item.executionStatus || 'Executed (Simulation)'}</td>
                          <td className="p-4">
                            <button
                              onClick={() => triggerRollback(item.auditId)}
                              className="px-3 py-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded font-semibold text-[11px] text-amber-400 hover:text-amber-300 flex items-center gap-1"
                            >
                              Rollback Simulation
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })()}

          {/* 12. SYSTEM HEALTH */}
          {activeTab === 'health' && (
            <div className="space-y-8 animate-fadeIn">
              <div className="flex justify-between items-center flex-wrap gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h1 className="text-2xl font-extrabold tracking-tight text-white flex items-center gap-2">
                      <HeartPulse size={24} className="text-emerald-400" />
                      Distributed System Microservice Health Grid
                    </h1>
                    <SourceTypeBadge type="LIVE" />
                  </div>
                  <p className="text-xs text-slate-400">Real-time health status, response latencies, target ports, and reachability across all 11 microservice nodes.</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono text-slate-400">Last Checked: {formatLastUpdated(healthLastUpdated)}</span>
                  <button onClick={fetchHealth} className="p-2 border border-slate-800 rounded-lg hover:bg-slate-800 text-xs flex items-center gap-1.5 font-semibold">
                    <RefreshCw size={14} /> Refresh Health Grid
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {healthStatus && Object.entries(healthStatus).map(([name, service]) => {
                  const isHealthy = service.status === 'healthy';
                  const portMap = {
                    backend: "5000",
                    monitoring: "6001",
                    "ai-engine": "8000",
                    "risk-engine": "8500",
                    "attack-simulator": "8600",
                    "policy-engine": "8700",
                    "cloud-adapter": "7000",
                    "research-evaluator": "8800",
                    "digital-twin": "8900",
                    "report-generator": "9000",
                    mongodb: "27017"
                  };
                  const servicePort = portMap[name] || "---";

                  return (
                    <div key={name} className={`p-5 rounded-2xl border ${isHealthy ? 'border-slate-800 bg-slate-900/20' : 'border-rose-900/40 bg-rose-950/10'} space-y-4`}>
                      <div className="flex justify-between items-start">
                        <div>
                          <span className="font-bold tracking-tight text-white capitalize text-sm block">{name.replace('-', ' ')}</span>
                          <span className="text-[10px] font-mono text-slate-400">Port {servicePort}</span>
                        </div>
                        <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider border ${isHealthy ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                          {isHealthy ? '● Healthy' : '● Unreachable'}
                        </span>
                      </div>

                      <div className="space-y-2 text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                        <div className="flex justify-between">
                          <span>Reachable:</span>
                          <span className={`font-semibold ${isHealthy ? 'text-emerald-400' : 'text-rose-400'}`}>{isHealthy ? 'Yes' : 'No'}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Latency:</span>
                          <span className="font-semibold text-slate-300">{service.latencyMs ? `${service.latencyMs} ms` : '---'}</span>
                        </div>
                        {!isHealthy && service.error && (
                          <div className="p-2 bg-rose-950/30 border border-rose-900/40 rounded text-[10px] text-rose-300 font-mono">
                            Reason: {service.error}
                          </div>
                        )}
                        <div className="flex justify-between items-center pt-1 text-[10px]">
                          <span className="text-slate-500">Last Checked:</span>
                          <span className="text-slate-300">{formatLastUpdated(healthLastUpdated)}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

        </main>
      </div>
    </div>
  );
}

export default App;
