export type Failure = 'hardware'|'energy'|'communications'|'destroyed'|'blocked';
export type Colony = 'A'|'B'|'C';
export type Hive = {id:string; colony:Colony; level:number; x:number; z:number; parent?:string; workers:string[]};
export type Egg = {id:string;colony:Colony;left:string;right:string;x:number;z:number};
export type State={failure:Record<string,Failure>;tick:number;run:boolean;events:string[]};
export const colonies:Colony[]=['A','B','C'];
const specs:Record<Colony,[number,number][]>={A:[[-14,5],[-9,3],[-4,1],[3,-1],[0,8]],B:[[14,-9],[9,-6],[5,-9],[0,-10]],C:[[-16,-9],[-12,-7],[-8,-10],[-3,-12]]};
export const hives:Hive[]=colonies.flatMap(c=>specs[c].map(([x,z],level)=>({id:c+':N'+level,colony:c,level,x,z,parent:level?c+':N'+(level===4?2:level-1):undefined,workers:level===0?[]:level===1?['scout','mapping','structure']:level===2?['scout','mapping']:['mapping','environment']})));
export const hivesById:Record<string,Hive>=Object.fromEntries(hives.map(n=>[n.id,n]));
export const eggs:Egg[]=hives.filter(n=>n.level>=2).map(n=>{const p=hivesById[n.parent!];return {id:n.colony+':E'+(n.level===4?'3':n.level-1),colony:n.colony,left:p.id,right:n.id,x:(p.x+n.x)/2,z:(p.z+n.z)/2}});
export const eggsById:Record<string,Egg>=Object.fromEntries(eggs.map(e=>[e.id,e]));
export const start=():State=>({failure:{},tick:0,run:true,events:['MISSION INITIALIZED: three autonomous colonies','N1: one Queen and three Handlers per colony','N2+: Relay Handler, Retriever Handler, mission-specific Workers']});
export const activeEggs=(s:State)=>eggs.filter(e=>[e.left,e.right].some(id=>s.failure[id]&&s.failure[id]!=='communications')).map(e=>e.id);
export const bridge=(s:State,c:Colony='A')=>s.failure[c+':N2'] && s.failure[c+':N2']!=='communications'&&!s.failure[c+':N1']&&!s.failure[c+':N3']&&activeEggs(s).includes(c+':E1')&&activeEggs(s).includes(c+':E2');
export function inject(s:State,ids:string[],kind:Failure):State{const failure={...s.failure};for(const id of ids)failure[id]=kind;const next={...s,failure,events:[...s.events,...ids.map(id=>id+' '+kind.toUpperCase()+(kind==='communications'?' · DIAGNOSTICS':' · RECALL + EGG SAFETY ACTIVATION'))]};if(bridge(next))next.events.push('A: BRIDGE MODE · N1 ↔ E1 ↔ E2 ↔ N3');return next}
export function restore(s:State,id:string):State{const failure={...s.failure};delete failure[id];return {...s,failure,events:[...s.events,id+' RECOMMISSIONED · reserve eggs on standby']}}
