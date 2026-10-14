import {Canvas,useFrame} from '@react-three/fiber';
import {OrbitControls,Line,Html,Sparkles} from '@react-three/drei';
import {useMemo,useRef} from 'react';
import * as THREE from 'three';
import {hives,eggs,hivesById,eggsById,activeEggs,bridge,State,Hive} from './model';
const palette:Record<string,string>={A:'#ffce69',B:'#4de7ef',C:'#4de9a7'};
function Terrain(){
 const ground=useMemo(()=>{const g=new THREE.PlaneGeometry(43,38,60,60);g.rotateX(-Math.PI/2);const p=g.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i);p.setY(i,Math.sin(x*.6)*Math.cos(z*.48)*.15-.16)}g.computeVertexNormals();return g},[]);
 return <group><mesh geometry={ground} receiveShadow><meshStandardMaterial color="#997753" roughness={1}/></mesh>
 <gridHelper args={[42,42,'#5d888c','#6a6256']} position={[0,.01,0]}/>
 {[[6,4,4],[-2,-4,3.2],[10,-2,2.4]].map(([x,z,r],j)=><group key={j}>
 <mesh rotation={[-Math.PI/2,0,0]} position={[x,.04,z]}><ringGeometry args={[r-.3,r+.22,48]}/><meshStandardMaterial color="#d4b68c" side={THREE.DoubleSide}/></mesh>
 {Array.from({length:12},(_,i)=>{const a=i*Math.PI/6;return <group key={i} position={[x+Math.cos(a)*r,0,z+Math.sin(a)*r]} rotation={[0,-a,0]}>
 <mesh position={[0,.65,0]} castShadow><boxGeometry args={[.33,1.3,.3]}/><meshStandardMaterial color="#d0ba92" roughness={1}/></mesh>
 <mesh position={[0,1.32,0]} castShadow><boxGeometry args={[.74,.25,.43]}/><meshStandardMaterial color="#d5bb91"/></mesh></group>})}</group>)}
 <mesh rotation={[-Math.PI/2,0,-.2]} position={[15,.035,5]}><planeGeometry args={[8,5]}/><meshBasicMaterial color="#e83150" transparent opacity={.22}/></mesh>
 <Sparkles count={48} scale={[40,3,32]} size={1.2} speed={.2} color="#ffdb91" opacity={.25}/></group>
}
function Bee({x,z,i,type}:{x:number;z:number;i:number;type:'queen'|'handler'|'worker'}){
 const ref=useRef<THREE.Group>(null);useFrame(({clock})=>{if(ref.current){ref.current.position.y=1.35+Math.sin(clock.elapsedTime*2+i)*.15;ref.current.rotation.y=clock.elapsedTime*.24+i}});
 const color=type==='queen'?'#ffd465':type==='handler'?'#d490fc':'#57e7f9';
 return <group ref={ref} position={[x,1.35,z]} scale={type==='queen'?.65:.38}>
 <mesh rotation={[0,0,Math.PI/2]}><capsuleGeometry args={[.27,.6,5,9]}/><meshStandardMaterial color="#202e36" metalness={.65}/></mesh>
 {[-.3,0,.3].map((v,j)=><mesh key={j} position={[.04,0,v]} rotation={[0,0,Math.PI/2]}><torusGeometry args={[.31,.06,8,20]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.4}/></mesh>)}
 {[-1,1].map(d=><mesh key={d} position={[d*.4,.24,.05]}><sphereGeometry args={[.34,12,10]}/><meshStandardMaterial color="#bbf5ff" transparent opacity={.61} emissive="#5ce0ff" emissiveIntensity={.3}/></mesh>)}</group>
}
function Node({n,s,selected,choose}:{n:Hive;s:State;selected:boolean;choose:(v:string)=>void}){
 const fault=s.failure[n.id],physical=fault&&fault!=='communications';const color=physical?'#ff6274':n.level<=1?'#ffca61':palette[n.colony];
 return <group position={[n.x,0,n.z]} onClick={e=>{e.stopPropagation();choose(n.id)}}>
 <mesh position={[0,.15,0]} castShadow><cylinderGeometry args={[n.level<=1?.95:.72,1,.33,6]}/><meshStandardMaterial color="#162c3b" metalness={.8} roughness={.25}/></mesh>
 <mesh position={[0,.38,0]}><cylinderGeometry args={[.53,.65,.3,6]}/><meshStandardMaterial color={physical?'#6b2639':'#326278'} emissive={color} emissiveIntensity={.1}/></mesh>
 {n.level<=1&&<mesh position={[0,1.1,0]}><cylinderGeometry args={[.08,.08,1.15,8]}/><meshStandardMaterial color={color} emissive={color} emissiveIntensity={.75}/></mesh>}
 <mesh position={[0,.04,0]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[1,1.05,48]}/><meshBasicMaterial color={selected?'white':color} side={THREE.DoubleSide}/></mesh>
 <pointLight color={color} intensity={selected?2.4:1} distance={4}/>
 {n.level>0&&Array.from({length:Math.min(4,n.workers.length+(n.level===1?2:2))},(_,i)=>{const a=i*Math.PI*2/4;return <Bee key={i} x={Math.cos(a)*1.5} z={Math.sin(a)*1.5} i={i+n.level} type={n.level===1&&i===0?'queen':i<2?'handler':'worker'}/>})}
 <Html position={[0,2.3,0]} center distanceFactor={15} style={{pointerEvents:'none'}}><div className={'object-label '+(physical?'danger':'')}><b>{n.id}</b><span>{physical?'FAILED':fault==='communications'?'LINK ANOMALY':n.level===0?'ENERGY ROOT':n.level===1?'QUEEN HIVE':'FORWARD NEST'}</span></div></Html>
 </group>
}
function Egg({id,x,z,active,choose}:{id:string;x:number;z:number;active:boolean;choose:(v:string)=>void}){
 return <group position={[x,.08,z]} onClick={e=>{e.stopPropagation();choose(id)}}>
 <mesh position={[0,.5,0]}><icosahedronGeometry args={[.42,1]}/><meshStandardMaterial color={active?'#e9b4ff':'#7963a3'} emissive={active?'#bc66ff':'#413363'} emissiveIntensity={active?1.1:.3}/></mesh>
 <mesh position={[0,.02,0]} rotation={[-Math.PI/2,0,0]}><ringGeometry args={[.6,.66,32]}/><meshBasicMaterial color={active?'#d994ff':'#665477'} side={THREE.DoubleSide}/></mesh>
 {active&&<pointLight color="#d28bff" intensity={2.7} distance={4}/>}
 <Html position={[0,1.15,0]} center distanceFactor={17} style={{pointerEvents:'none'}}><div className={'egg-label '+(active?'active':'')}><b>{id}</b><span>{active?'BRIDGE':'STANDBY'}</span></div></Html>
 </group>
}
function Links({s}:{s:State}){
 const active=activeEggs(s);const lines:{a:[number,number];b:[number,number];kind:'normal'|'bridge'|'assist'}[]=[];
 for(const n of hives){if(!n.parent||s.failure[n.id]||s.failure[n.parent])continue;const p=hivesById[n.parent];lines.push({a:[n.x,n.z],b:[p.x,p.z],kind:'normal'})}
 if(bridge(s)){for(const [l,r] of [['A:N1','A:E1'],['A:E1','A:E2'],['A:E2','A:N3']]){const a=hivesById[l]??eggsById[l],b=hivesById[r]??eggsById[r];lines.push({a:[a.x,a.z],b:[b.x,b.z],kind:'bridge'})}}
 for(const [l,r] of [['A:N3','B:N2'],['B:N3','C:N3']]){const a=hivesById[l],b=hivesById[r];lines.push({a:[a.x,a.z],b:[b.x,b.z],kind:'assist'})}
 return <>{lines.map(({a,b,kind},i)=><Line key={i} points={[[a[0],.41,a[1]],[b[0],.41,b[1]]]} color={kind==='bridge'?'#d99aff':kind==='assist'?'#ffc95f':'#6deab5'} lineWidth={kind==='bridge'?4:2} dashed={kind==='assist'} dashSize={.4} gapSize={.2}/>)}
 {eggs.filter(e=>!active.includes(e.id)).map(e=><Line key={e.id} points={[[e.x,.2,e.z],[hivesById[e.right].x,.2,hivesById[e.right].z]]} color="#80748c" lineWidth={1} dashed dashSize={.25} gapSize={.3}/>)}</>
}
export function Scene({state,selected,choose}:{state:State;selected:string;choose:(v:string)=>void}){
 return <Canvas shadows dpr={[1,1.5]} camera={{position:[-5,25,32],fov:44,near:.2,far:150}} gl={{antialias:true,powerPreference:'high-performance'}}>
 <color attach="background" args={['#20343b']}/><fog attach="fog" args={['#284047',26,82]}/>
 <hemisphereLight args={['#b9eaff','#6a4d2e',2}/><ambientLight intensity={.5}/>
 <directionalLight position={[-10,19,-9]} color="#ffe3a9" intensity={3} castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-25} shadow-camera-right={25} shadow-camera-top={25} shadow-camera-bottom={-25}/>
 <Terrain/><Links s={state}/>
 {hives.map(n=><Node key={n.id} n={n} s={state} selected={selected===n.id} choose={choose}/>)}
 {eggs.map(e=><Egg key={e.id} {...e} active={activeEggs(state).includes(e.id)} choose={choose}/>)}
 <OrbitControls makeDefault target={[0,0,0]} minDistance={12} maxDistance={60} maxPolarAngle={1.5} enableDamping/>
 </Canvas>
}
