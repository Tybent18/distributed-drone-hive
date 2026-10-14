import {useEffect,useState} from 'react';
import {Scene} from './Scene';
import {hives,eggs,hivesById,eggsById,colonies,State,Failure,start,inject,restore,activeEggs,bridge} from './model';
import './styles.css';
const failureTypes:Failure[]=['hardware','communications','energy','destroyed','blocked'];
function App(){
 const [state,setState]=useState<State>(start);const [selected,setSelected]=useState('A:N2');
 const [kind,setKind]=useState<Failure>('hardware');const [multi,setMulti]=useState(false);const [dialog,setDialog]=useState(false);
 useEffect(()=>{if(location.search.includes('demo=bridge'))setState(s=>inject(s,['A:N2'],'hardware'))},[]);
 useEffect(()=>{const timer=setInterval(()=>setState(s=>s.run?{...s,tick:s.tick+1}:s),850);return ()=>clearInterval(timer)},[]);
 const node=hivesById[selected],egg=eggsById[selected],active=activeEggs(state),paths=bridge(state);
 const target=node?.id??'A:N2';
 const perform=(ids:string[],f:Failure)=>{setState(s=>inject(s,ids,f));setSelected(ids[0]);setDialog(false)};
 return <div className="app">
 <header className="header"><div className="brand"><span>⬡</span><div><h1>DRONE HIVE <em>/ COLONY OPS</em></h1><small>HAZARDOUS TERRAIN RECON · FEDERATED EXPANSION NETWORK</small></div></div>
 <div className="expedition">◈ &nbsp;<b>GÖBEKLI TEPE–INSPIRED EXPEDITION</b><small>PROCEDURAL 3D TERRAIN · NON-INVASIVE RESEARCH CONCEPT</small></div>
 <div className="indicator"><b>● 3D LIVE VIEW</b><small>CONCEPT SIMULATION</small></div></header>
 <div className="layout"><aside className="left panel"><h2>⬡ COLONY HIERARCHY</h2><div className="trees">
 {colonies.map(c=><div key={c} className="colony"><h3><i style={{color:c==='A'?'#ffd074':c==='B'?'#68dbf5':'#60e7aa'}}>⬡</i> COLONY {c}<small>{Object.keys(state.failure).some(id=>id.startsWith(c+':'))?'INCIDENT':'ONLINE'}</small></h3>
 {hives.filter(n=>n.colony===c).map(n=><button key={n.id} onClick={()=>setSelected(n.id)} className={'treeitem '+(selected===n.id?'chosen':'')+(state.failure[n.id]?' failed':'')}><span>{n.level===0?'☀':n.level===1?'♛':'⬡'}</span><b>N{n.level}</b> {n.level===0?'Energy Root':n.level===1?'Queen Hive':'Expansion Hive'} {state.failure[n.id]&&<i>!</i>}</button>)}
 {eggs.filter(e=>e.colony===c).map(e=><button key={e.id} onClick={()=>setSelected(e.id)} className={'treeitem eggitem '+(selected===e.id?'chosen':'')}><span>◈</span><b>{e.id.split(':')[1]}</b> {active.includes(e.id)?'BRIDGING':'Midpoint Egg'}</button>)}
 </div>)}</div><section className="role-index"><h2>✦ BEE FUNCTIONS</h2><p><b>♛ Queen</b><small>One N1 coordinator per independent colony</small></p><p><b>✥ Relay Handler</b><small>Mandatory N2+ communications</small></p><p><b>✥ Retriever</b><small>Mandatory N2+ repairs, eggs, assembly</small></p><p><b>✦ Workers</b><small>Mission-dependent survey and recording</small></p></section></aside>
 <section className="middle"><div className="stage"><Scene state={state} selected={selected} choose={setSelected}/>
 <div className="overlay top"><small>TACTICAL CAMERA / 3D WEB</small><strong>ARCHAEOLOGICAL EXPEDITION</strong><span>Orbit • zoom • inspect nodes and contingency eggs</span></div>
 <div className="overlay legend"><p><i className="key green"/> Normal colony link</p><p><i className="key yellow"/> Cross-colony assistance</p><p><i className="key purple"/> Egg emergency bridge</p><p><i className="key red"/> Failed infrastructure</p></div>
 <div className={'overlay mission '+(paths?'danger':'')}><strong>{paths?'✦ EMERGENCY EGG BRIDGE ACTIVE':Object.keys(state.failure).length?'⚠ INCIDENT RESPONSE':'◈ MULTI-COLONY WEB ONLINE'}</strong><span>{paths?'N1 ↔ E1 ↔ E2 ↔ N3 · limited temporary corridor':Object.keys(state.failure).length?'Contain faults · select a node to inspect':'Independent Queens · shared communication / rescue only'}</span></div>
 </div><div className="toolbar"><h2>MISSION CONTROLS <small>/ {state.run?'RUNNING':'PAUSED'}</small></h2><div className="buttons">
 <button className="btn play" onClick={()=>setState(s=>({...s,run:!s.run}))}>{state.run?'Ⅱ PAUSE':'▶ RESUME'}</button>
 <button className="btn violet" onClick={()=>perform(['A:N2'],'hardware')}>◈ DEMO: N2 BRIDGE</button>
 <button className="btn red" onClick={()=>setDialog(true)}>⚠ INJECT FAILURE</button>
 <button className="btn amber" onClick={()=>setState(s=>({...s,events:[...s.events,'COLONY '+(node?.colony??egg?.colony??'A')+': RECALL TO SAFE NEST / EGG']}))}>↶ RECALL COLONY</button>
 <button className="btn" onClick={()=>setState(s=>restore(s,target))}>↻ RESTORE</button><button className="btn" onClick={()=>{setState(start());setSelected('A:N2')}}>RESET</button>
 </div></div></section>
 <aside className="right panel"><h2>⌕ NODE INSPECTOR</h2><select className="picker" value={selected} onChange={e=>setSelected(e.target.value)}>{hives.map(n=><option key={n.id} value={n.id}>{n.id} · {n.level===0?'Energy Root':n.level===1?'Queen Hive':'Forward Nest'}</option>)}{eggs.map(e=><option key={e.id} value={e.id}>{e.id} · Midpoint Egg</option>)}</select>
 {node?<><div className={'selection '+(state.failure[node.id]?'down':'')}><span className="hex">⬡</span><div><b>{node.id} · {node.level===0?'ENERGY ROOT':node.level===1?'QUEEN HIVE':'FORWARD NEST'}</b><small>{state.failure[node.id]?'FAULT: '+state.failure[node.id].toUpperCase():'NOMINAL OPERATIONS'}</small></div></div>
 <div className="facts"><p><span>COLONY</span><b>{node.colony}</b></p><p><span>PARENT</span><b>{node.parent??'Independent root'}</b></p><p><span>COMMAND</span><b>{node.level===1?'ONE QUEEN':node.level===0?'Energy management':'Local delegated safety'}</b></p><p><span>STATUS</span><b className={state.failure[node.id]?'bad':'good'}>{state.failure[node.id]??'Operational'}</b></p><p><span>POWER</span><b>Finite, abstract model</b></p></div>
 <h2>✥ ASSIGNED DRONES</h2><div className="counts"><div><strong>{node.level===1?1:0}</strong><small>QUEEN</small></div><div><strong>{node.level===1?3:node.level>=2?1:0}</strong><small>RELAY / N1</small></div><div><strong>{node.level>=2?1:node.level===1?2:0}</strong><small>RETRIEVER</small></div><div><strong>{node.workers.length}</strong><small>WORKERS</small></div></div>
 <h2>◉ SENSOR ALLOCATION</h2><div className="sensors">{node.workers.map((role,i)=><p key={i}><span>◈ {role.replace('_',' ')}</span><small>WORKER {i+1}</small></p>)}<p><span>◎ Telemetry & diagnostics</span><small>SIMULATED</small></p></div>
 <h2>⌁ NEXT DEPLOYMENT</h2><p className="detail">Hybrid foldable chassis + modular energy, communication, docking and recording subsystems. Midpoint eggs stage after commissioning.</p></>:egg?<><div className="selection"><span className="hex violet-hex">◈</span><div><b>{egg.id} · MICRO-NEST</b><small>{active.includes(egg.id)?'EMERGENCY BRIDGING':'RESERVE STANDBY'}</small></div></div><div className="facts"><p><span>COLONY</span><b>{egg.colony}</b></p><p><span>PARENT</span><b>{egg.left}</b></p><p><span>CHILD</span><b>{egg.right}</b></p><p><span>POSITION</span><b>Midpoint</b></p></div><p className="detail">Temporary nest: finite energy, data buffering, limited refuge and emergency communications. No Queen.</p></>:null}
 <section className="safety"><h2>⛨ COMMAND SOVEREIGNTY</h2><p>One Queen at Node 1 per colony. Cross-colony links support rescue and communication but never transfer control.</p></section>
 </aside></div>
 <footer className="bottom"><div className="telemetry"><h2>▥ SYSTEM TELEMETRY <small>ILLUSTRATIVE ONLY</small></h2><div className="stats">{[['NODES ONLINE',String(hives.length-Object.keys(state.failure).length)+'/'+hives.length],['BRIDGE EGGS',active.length+'/'+eggs.length],['COLONIES','3'],['MISSION TICK',String(state.tick).padStart(3,'0')],['FAILURES',String(Object.keys(state.failure).length)]].map(([label,value])=><div key={label}><small>{label}</small><strong>{value}</strong><i/></div>)}</div></div>
 <div className="logs"><h2>⌗ MISSION EVENT LOG <small>LOCAL STATE / NO LIVE DRONE DATA</small></h2>{state.events.slice(-5).reverse().map((e,i)=><p key={i}><span>T{String(state.tick).padStart(3,'0')}</span>{e}</p>)}</div></footer>
 <div className="footnote"><b>DRONE HIVE · CONCEPT PROTOTYPE</b><span>React + Three.js visual state · Python live integration pending</span><span>NO HARDWARE-VALIDATED RANGE OR ENERGY CLAIMS</span></div>
 {dialog&&<div className="backdrop" role="dialog" aria-label="Failure controls" aria-modal="true"><div className="modal"><div className="modalhead"><h2>FAILURE INJECTION</h2><button onClick={()=>setDialog(false)} aria-label="Close">×</button></div><p>Select a failure mechanism and inject it into one or more permanent nests.</p><label>FAULT CLASS<select value={kind} onChange={e=>setKind(e.target.value as Failure)}>{failureTypes.map(k=><option key={k} value={k}>{k.toUpperCase()}</option>)}</select></label><label>TARGET<select value={multi?'multi':'single'} onChange={e=>setMulti(e.target.value==='multi')}><option value="single">Selected node: {target}</option><option value="multi">Simultaneous A:N2 + B:N2</option></select></label><p className="caution">Communications faults initiate diagnosis. Physical faults trigger local recall and safety activation of eligible midpoint micro-nests.</p><button className="btn red wide" onClick={()=>perform(multi?['A:N2','B:N2']:[target],kind)}>INJECT SIMULATED FAULT</button></div></div>}
 </div>
}
export {App};
