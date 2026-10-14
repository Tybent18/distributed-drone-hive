import {inject,restore,start,type State} from './model';
export type DemoId='overview'|'bridge'|'multi'|'comms'|'energy'|'recovery';
export const demos:{id:DemoId;title:string;detail:string;selection:string}[]=[
 {id:'overview',title:'01 / COLONY WEB',detail:'Bee crews, foldable hives, staged eggs and independent Queens.',selection:'A:N1'},
 {id:'bridge',title:'02 / EGG BRIDGE',detail:'N2 fails; midpoint micro-nests activate a temporary bridge.',selection:'A:E1'},
 {id:'multi',title:'03 / MULTI-FAILURE',detail:'Separate physical failures affect more than one colony.',selection:'A:N2'},
 {id:'comms',title:'04 / COMMS DIAGNOSIS',detail:'N2 is silent but not physically destroyed.',selection:'B:N2'},
 {id:'energy',title:'05 / ROOT POWER',detail:'Energy root outage; reserve operation remains hypothetical.',selection:'C:N0'},
 {id:'recovery',title:'06 / REPAIR',detail:'Retriever restores N2 and eggs return to standby.',selection:'A:N2'}
];
export function scenario(id:DemoId):State {
 const initial=start();
 if(id==='bridge')return inject(initial,['A:N2'],'hardware');
 if(id==='multi')return inject(initial,['A:N2','B:N2'],'destroyed');
 if(id==='comms')return inject(initial,['B:N2'],'communications');
 if(id==='energy')return inject(initial,['C:N0'],'energy');
 if(id==='recovery') {
  const failed=inject(initial,['A:N2'],'hardware');
  return {...restore(failed,'A:N2'),
   events:[...failed.events,'RETRIEVER SERVICE COMPLETE · N2 recommissioned','EGG MICRO-NESTS RETURN TO STANDBY']};
 }
 return initial;
}
