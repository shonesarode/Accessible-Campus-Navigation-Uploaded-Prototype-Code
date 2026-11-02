import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

type Node = { id: string; label: string; x: number; y: number };
type Edge = { id: string; source: string; target: string; meters: number; slope_percent: number; stairs: boolean; surface: string };
type Network = { nodes: Node[]; edges: Edge[]; notice: string };
type Route = { node_ids: string[]; edge_ids: string[]; distance_meters: number; weighted_cost: number; note: string };
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, options);
  const body: unknown = await response.json();
  if (!response.ok) {
    const detail = (body as { detail?: string }).detail;
    throw new Error(typeof detail === 'string' ? detail : `Request failed: ${response.status}`);
  }
  return body as T;
}

function App() {
  const [network, setNetwork] = useState<Network | null>(null);
  const [origin, setOrigin] = useState('west');
  const [destination, setDestination] = useState('science');
  const [wheelchair, setWheelchair] = useState(true);
  const [avoidUnpaved, setAvoidUnpaved] = useState(false);
  const [maxSlope, setMaxSlope] = useState(6);
  const [blockedEdges, setBlockedEdges] = useState<string[]>([]);
  const [route, setRoute] = useState<Route | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [reportEdge, setReportEdge] = useState('');
  const [reportMessage, setReportMessage] = useState('');
  const [reportStatus, setReportStatus] = useState('');

  useEffect(() => {
    api<Network>('/api/network')
      .then(value => { setNetwork(value); setReportEdge(value.edges[0]?.id || ''); })
      .catch(err => setError(`Unable to load demo network: ${String(err)}`));
  }, []);

  const nodeMap = useMemo(() => new Map(network?.nodes.map(n => [n.id, n]) || []), [network]);
  const routeEdges = useMemo(() => new Set(route?.edge_ids || []), [route]);
  const routeNodes = useMemo(() => new Set(route?.node_ids || []), [route]);
  const blockedSet = useMemo(() => new Set(blockedEdges), [blockedEdges]);

  async function findRoute(event: React.FormEvent) {
    event.preventDefault(); setBusy(true); setError(''); setRoute(null);
    try {
      const result = await api<Route>('/api/route', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start: origin, destination, wheelchair, avoid_unpaved: avoidUnpaved, max_slope_percent: maxSlope, blocked_edges: blockedEdges }),
      });
      setRoute(result);
    } catch (err) { setError(err instanceof Error ? err.message : String(err)); }
    finally { setBusy(false); }
  }

  async function sendReport(event: React.FormEvent) {
    event.preventDefault(); setReportStatus('');
    try {
      await api('/api/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ edge_id: reportEdge, description: reportMessage }) });
      setReportStatus('Report queued for review. It does not automatically affect route planning.');
      setReportMessage('');
    } catch (err) { setReportStatus(err instanceof Error ? err.message : String(err)); }
  }

  return <div className="shell">
    <header className="topbar"><div className="brand"><span className="brand-mark">↗</span><span>pathways<span className="brand-dot">.</span></span></div><span className="top-tag">OPEN-SOURCE PORTFOLIO DEMO</span></header>
    <main>
      <section className="intro"><span className="eyebrow">ACCESSIBLE ROUTING · DEMONSTRATION</span><h1>Find a path that <em>works for you.</em></h1><p>Explore how routes can account for stairs, slopes, surfaces and temporary obstructions—not just distance.</p></section>
      <div className="layout">
        <aside className="panel controls"><div className="section-number">01 / PLAN</div><h2>Route preferences</h2><form onSubmit={findRoute}>
          <label htmlFor="start">Starting point</label><select id="start" value={origin} onChange={e => setOrigin(e.target.value)}>{network?.nodes.map(n => <option key={n.id} value={n.id}>{n.label}</option>)}</select>
          <label htmlFor="end">Destination</label><select id="end" value={destination} onChange={e => setDestination(e.target.value)}>{network?.nodes.map(n => <option key={n.id} value={n.id}>{n.label}</option>)}</select>
          <label className="check"><input type="checkbox" checked={wheelchair} onChange={e => setWheelchair(e.target.checked)}/> Stair-free routing</label>
          <label className="check"><input type="checkbox" checked={avoidUnpaved} onChange={e => setAvoidUnpaved(e.target.checked)}/> Paved paths only</label>
          <label htmlFor="slope">Max route slope <strong>{maxSlope}%</strong></label><input id="slope" type="range" min="0" max="12" value={maxSlope} onChange={e => setMaxSlope(Number(e.target.value))} disabled={!wheelchair}/>
          <button className="primary" type="submit" disabled={!network || busy}>{busy ? 'Finding route…' : 'Find accessible route →'}</button>
        </form>
        {route && <div className="route-summary"><span>YOUR DEMO ROUTE</span><strong>{Math.round(route.distance_meters)} m</strong><small>{route.node_ids.map(id => nodeMap.get(id)?.label ?? id).join(' → ')}</small></div>}
        {error && <p className="error" role="alert">{error}</p>}
        </aside>
        <section className="panel map-panel"><div className="map-header"><div><span className="section-number">02 / EXPLORE</span><h2>Illustrative campus network</h2></div><span className="demo-chip">Schematic, not geographic</span></div>
          <div className="map-wrap"><svg viewBox="0 0 1000 650" role="img" aria-label="Demo network diagram with highlighted selected route" preserveAspectRatio="xMidYMid meet">
            <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#dbe8e2" strokeWidth="1"/></pattern></defs>
            <rect width="1000" height="650" fill="#f4f8f4"/><rect width="1000" height="650" fill="url(#grid)"/>
            {network?.edges.map(e => { const a = nodeMap.get(e.source), b = nodeMap.get(e.target); if (!a || !b) return null; const active = routeEdges.has(e.id); const blocked = blockedSet.has(e.id); return <line key={e.id} x1={a.x*10} y1={a.y*6.5} x2={b.x*10} y2={b.y*6.5} stroke={blocked ? '#df7e67' : active ? '#087f6e' : '#b4c9bc'} strokeWidth={active ? 12 : 6} strokeLinecap="round" strokeDasharray={blocked ? '11 10' : e.stairs ? '2 11' : undefined}><title>{e.id}: {e.meters} m{e.stairs ? ', stairs' : ''}</title></line>; })}
            {network?.nodes.map(n => <g key={n.id} transform={`translate(${n.x*10},${n.y*6.5})`}><circle r={routeNodes.has(n.id) ? 13 : 10} fill={routeNodes.has(n.id) ? '#087f6e' : '#fff'} stroke="#144f4b" strokeWidth="3"/><text x="0" y="-22" textAnchor="middle" fontSize="18" fontWeight="600" fill="#193f38">{n.label}</text></g>)}
          </svg></div>
          <div className="legend"><span><i className="line selected"/> Selected route</span><span><i className="line ordinary"/> Walkway</span><span><i className="line blocked"/> Simulated closure</span></div>
          <div className="simulation"><label htmlFor="closure">Test a closure (simulation only)</label><select id="closure" value={blockedEdges[0] || ''} onChange={e => { setBlockedEdges(e.target.value ? [e.target.value] : []); setRoute(null); }}><option value="">No simulated closure</option>{network?.edges.map(e => <option key={e.id} value={e.id}>{e.id}</option>)}</select></div>
        </section>
      </div>
      <section className="panel report"><div><span className="section-number">03 / CONTRIBUTE</span><h2>Report a path concern</h2><p>Reports enter a pending-review queue. This prototype never treats unverified reports as confirmed facts.</p></div><form onSubmit={sendReport}><label htmlFor="report-edge">Path segment</label><select id="report-edge" value={reportEdge} onChange={e => setReportEdge(e.target.value)}>{network?.edges.map(e => <option key={e.id} value={e.id}>{e.id}</option>)}</select><label htmlFor="report-description">What changed?</label><textarea id="report-description" required minLength={5} maxLength={500} placeholder="Describe the obstruction or access issue..." value={reportMessage} onChange={e => setReportMessage(e.target.value)}/><button className="secondary" type="submit" disabled={!network}>Submit demo report</button>{reportStatus && <p role="status" className="report-status">{reportStatus}</p>}</form></section>
      <p className="disclaimer"><strong>Safety notice:</strong> Fictional network and demonstration data only. Not suitable for real-world mobility decisions or emergency access.</p>
    </main><footer>Pathways · Software engineering portfolio demonstration · No live accessibility claims</footer>
  </div>;
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
