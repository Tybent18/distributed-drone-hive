import {inject,restore,start,type Failure,type State} from './model';

export type DemoId='overview'|'bridge'|'multi'|'comms'|'energy'|'recovery';
export type Safety = 'nominal'|'investigate'|'recall'|'bridging'|'repair'|'recovered';
export type Stage = {
  title: string;
  detail: string;
  select: string;
  safety: Safety;
  fault?: { ids: string[]; kind: Failure };
  restore?: string;
  holdEggs?: boolean;
};
export type DemoFrame = Stage & { state: State; step: number; total: number };

export const demos:{id:DemoId;title:string;detail:string;selection:string}[]=[
 {id:'overview',title:'01 / COLONY WEB',detail:'Bee crews, foldable hives, staged eggs and independent Queens.',selection:'A:N1'},
 {id:'bridge',title:'02 / EGG BRIDGE',detail:'N2 fails; midpoint micro-nests activate a temporary bridge.',selection:'A:N2'},
 {id:'multi',title:'03 / MULTI-FAILURE',detail:'Separate physical failures affect more than one colony.',selection:'A:N2'},
 {id:'comms',title:'04 / COMMS DIAGNOSIS',detail:'N2 is silent but not physically destroyed.',selection:'B:N2'},
 {id:'energy',title:'05 / ROOT POWER',detail:'Energy root outage; reserve operation remains hypothetical.',selection:'C:N0'},
 {id:'recovery',title:'06 / REPAIR',detail:'Retriever restores N2 and eggs return to standby.',selection:'A:N2'}
];

const T:Record<DemoId,Stage[]>={
 overview:[
  {title:'Colony foundations',detail:'Three independent N0 energy roots seed a branching exploration web.',select:'A:N0',safety:'nominal'},
  {title:'Queen command',detail:'One Queen and three multifunction Handlers operate at each Node 1.',select:'A:N1',safety:'nominal'},
  {title:'Forward hive crews',detail:'N2+ hives carry Relay + Retriever Handlers and mission-assigned Workers.',select:'A:N2',safety:'nominal'},
  {title:'Staged egg pods',detail:'Distinct egg-shaped micro-nests wait midway between commissioned stations.',select:'A:E1',safety:'nominal'},
  {title:'Cross-colony assistance',detail:'B can relay data or assist rescue without taking authority from A.',select:'B:N1',safety:'nominal'},
  {title:'Non-contact reconnaissance',detail:'Scout, mapping, imaging and environment Workers perform proposed surveys.',select:'C:N3',safety:'nominal'}
 ],
 bridge:[
  {title:'Normal corridor',detail:'N1 — E1 — N2 — E2 — N3; both egg pods are dormant.',select:'A:N2',safety:'nominal'},
  {title:'N2 hardware failure',detail:'The forward hive turns red. Adjacent egg units begin safety checks.',select:'A:N2',safety:'recall',fault:{ids:['A:N2'],kind:'hardware'},holdEggs:true},
  {title:'E1 activation',detail:'Midpoint E1 unfolds as a temporary communications and refuge unit.',select:'A:E1',safety:'bridging'},
  {title:'E1 + E2 bridge',detail:'Temporary corridor: N1 ↔ E1 ↔ E2 ↔ N3, subject to range and reserves.',select:'A:E2',safety:'bridging'},
  {title:'Safe refuge',detail:'Affected colony drones retreat; eggs provide limited support, not unlimited charging.',select:'A:E1',safety:'recall'},
  {title:'Repair corridor',detail:'Retriever support is proposed while temporary egg relays remain operational.',select:'A:N2',safety:'repair'}
 ],
 multi:[
  {title:'Independent colonies',detail:'Colonies A and B have distinct Queens and energy roots.',select:'A:N1',safety:'nominal'},
  {title:'First infrastructure loss',detail:'Colony A N2 is destroyed; neighboring eggs enter recovery service.',select:'A:N2',safety:'recall',fault:{ids:['A:N2'],kind:'destroyed'}},
  {title:'Second node destroyed',detail:'Colony B N2 fails separately; its own Queen retains command.',select:'B:N2',safety:'recall',fault:{ids:['B:N2'],kind:'destroyed'}},
  {title:'Two recovery corridors',detail:'The web checks local egg bridges and avoids promising universal resilience.',select:'A:E2',safety:'bridging'},
  {title:'Colony-scoped recall',detail:'Affected drones shelter while unaffected infrastructure remains autonomous.',select:'B:E1',safety:'recall'},
  {title:'Assistance, not takeover',detail:'Cross-colony support transmits information and rescue requests only.',select:'C:N1',safety:'investigate'}
 ],
 comms:[
  {title:'Telemetry nominal',detail:'B:N2 is powered, structurally healthy and connected.',select:'B:N2',safety:'nominal'},
  {title:'Missing heartbeat',detail:'B:N2 stops reporting, but physical destruction is NOT inferred.',select:'B:N2',safety:'investigate',fault:{ids:['B:N2'],kind:'communications'}},
  {title:'Relay diagnostics',detail:'Neighboring Relay Handlers check alternate telemetry and mesh paths.',select:'B:N1',safety:'investigate'},
  {title:'Local bounded autonomy',detail:'Previously authorized safe tasks can continue only within a timeout.',select:'B:N3',safety:'investigate'},
  {title:'Conservative fallback',detail:'Persistent uncertainty triggers return or shelter; no unsafe blind repair.',select:'B:N2',safety:'recall'},
  {title:'Link restoration',detail:'Communications resume without treating the node as physically damaged.',select:'B:N2',safety:'recovered',restore:'B:N2'}
 ],
 energy:[
  {title:'Root solar and battery',detail:'Colony C:N0 supplies a finite modeled energy budget.',select:'C:N0',safety:'nominal'},
  {title:'Energy fault detected',detail:'C:N0 energy stops; a radio connection alone cannot supply power.',select:'C:N0',safety:'recall',fault:{ids:['C:N0'],kind:'energy'}},
  {title:'Exploration suspended',detail:'Nonessential missions halt and affected drones prioritize safety.',select:'C:N1',safety:'recall'},
  {title:'Local reserves',detail:'Battery-backed hives and egg pods have limited operating endurance.',select:'C:E1',safety:'recall'},
  {title:'Cross-colony coordination',detail:'Neighboring colonies may assist with communications and rescue logistics.',select:'B:N3',safety:'investigate'},
  {title:'Root recommissioned',detail:'A repaired root can resume its simulated supply after approval.',select:'C:N0',safety:'recovered',restore:'C:N0'}
 ],
 recovery:[
  {title:'N2 commissioned',detail:'The permanent hive is online; both midpoint reserve eggs are dormant.',select:'A:N2',safety:'nominal'},
  {title:'Hardware fault',detail:'N2 becomes unsafe and triggers colony protective retreat.',select:'A:N2',safety:'recall',fault:{ids:['A:N2'],kind:'hardware'},holdEggs:true},
  {title:'Bridge established',detail:'Both egg pods provide a temporary communications path around N2.',select:'A:E1',safety:'bridging'},
  {title:'Retriever intervention',detail:'A designated Retriever Handler conducts authorized modular service.',select:'A:N2',safety:'repair'},
  {title:'N2 recommissioned',detail:'The repaired nest returns to service following safety checks.',select:'A:N2',safety:'recovered',restore:'A:N2'},
  {title:'Egg pods on standby',detail:'Temporary infrastructure closes down until another emergency.',select:'A:E2',safety:'nominal'}
 ]
};

export function demoLength(id:DemoId):number{return T[id].length}
export function getDemoFrame(id:DemoId,index:number):DemoFrame{
  const stages=T[id];
  const step=Math.min(Math.max(0,index),stages.length-1);
  let state=start();
  for(let i=0;i<=step;i++){
    const stage=stages[i];
    if(stage.fault)state=inject(state,stage.fault.ids,stage.fault.kind);
    if(stage.restore)state=restore(state,stage.restore);
    state={...state,eggOverride:stage.holdEggs?'standby':undefined,
      demoSafety:stage.safety,phase:stage.title,tick:i*12,
      events:[...state.events,stage.title.toUpperCase()+' · '+stage.detail]};
  }
  return {...stages[step],state,step,total:stages.length}
}
export function scenario(id:DemoId):State{return getDemoFrame(id,demoLength(id)-1).state}
