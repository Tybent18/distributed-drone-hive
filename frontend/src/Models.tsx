/** Procedural, visibly recognizable bee drones, modular beehive nests, and egg-shaped reserve micro-nests.
 * These are 3-D art assets for the scripted research visualization, not physical design drawings.
 */
import { useFrame } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';
import { Line } from '@react-three/drei';

type BeeKind = 'queen' | 'handler' | 'worker';
const metals = { queen: '#f9c74e', handler: '#bda0ec', worker: '#e5b84f' };
const glows = { queen: '#ffd76b', handler: '#ad83ff', worker: '#48dcf5' };

function JointRod({ from, to, color = '#403f43', radius = 0.025 }: {
  from: [number, number, number]; to: [number, number, number];
  color?: string; radius?: number;
}) {
  const start = new THREE.Vector3(...from);
  const end = new THREE.Vector3(...to);
  const delta = end.clone().sub(start);
  const midpoint = start.clone().add(end).multiplyScalar(0.5);
  const quaternion = new THREE.Quaternion().setFromUnitVectors(
    new THREE.Vector3(0, 1, 0), delta.clone().normalize(),
  );
  return <mesh position={midpoint.toArray()} quaternion={quaternion}>
    <cylinderGeometry args={[radius, radius, delta.length(), 7]} />
    <meshStandardMaterial color={color} metalness={0.8} roughness={0.32} />
  </mesh>;
}

export function BeeDrone({ x, z, index, kind, scale = 0.5, patrol = true }: {
  x: number; z: number; index: number; kind: BeeKind; scale?: number; patrol?: boolean;
}) {
  const body = useRef<THREE.Group>(null);
  const wings = useRef<THREE.Group>(null);
  const accent = glows[kind];
  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    if (body.current) {
      body.current.position.y = 1.25 + Math.sin(t * 2.5 + index * 1.3) * 0.17;
      if (patrol) {
        body.current.position.x = x + Math.sin(t * 0.39 + index * 1.8) * 0.34;
        body.current.position.z = z + Math.cos(t * 0.43 + index) * 0.32;
      }
      body.current.rotation.y = Math.sin(t * 0.44 + index) * 0.47;
    }
    if (wings.current) wings.current.rotation.x = Math.sin(t * 26 + index) * 0.16;
  });
  return <group ref={body} position={[x, 1.25, z]} scale={scale}>
    {/* Long striped abdomen, separate thorax, unmistakable head and compound eyes */}
    <mesh position={[-0.52, 0, 0]} scale={[1.13, .74, .73]} castShadow>
      <sphereGeometry args={[.51, 20, 14]} />
      <meshStandardMaterial color="#f2b731" metalness={.33} roughness={.42} />
    </mesh>
    {[-.89, -.57, -.25].map((v, i) =>
      <mesh key={i} position={[v, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
        <torusGeometry args={[i === 0 ? .29 : .35, .095, 10, 26]} />
        <meshStandardMaterial color="#24242d" metalness={.4} roughness={.43} />
      </mesh>
    )}
    <mesh position={[.07, .02, 0]} scale={[.7, .75, .73]} castShadow>
      <sphereGeometry args={[.52, 18, 14]} />
      <meshStandardMaterial color={metals[kind]} metalness={.46} roughness={.35} />
    </mesh>
    <mesh position={[.56, .02, 0]} scale={[.68, .68, .72]} castShadow>
      <sphereGeometry args={[.47, 18, 14]} />
      <meshStandardMaterial color="#2c2e35" metalness={.55} roughness={.31} />
    </mesh>
    {[-1, 1].map(sign => <group key={sign}>
      <mesh position={[.74, .15, sign * .255]} scale={[.27, .31, .19]}>
        <sphereGeometry args={[.45, 12, 12]} />
        <meshStandardMaterial color={accent} emissive={accent} emissiveIntensity={.65}
          roughness={.15} metalness={.18} />
      </mesh>
      <JointRod from={[.72, .31, sign * .12]} to={[.83, .64, sign * .25]} color="#1c2631" />
      <mesh position={[.83, .64, sign * .25]}>
        <sphereGeometry args={[.068, 9, 8]} />
        <meshStandardMaterial color="#ffc75c" />
      </mesh>
      {/* Three jointed bee legs per side */}
      {[-.48, -.03, .35].map((lx, li) => <group key={li}>
        <JointRod from={[lx, -.23, sign * .24]} to={[lx + .06, -.62, sign * .48]} />
        <JointRod from={[lx + .06, -.62, sign * .48]}
          to={[lx + .26, -.84, sign * .54]} />
      </group>)}
    </group>)}
    <group ref={wings}>
      {[-1, 1].map(sign => <group key={sign}>
        <mesh position={[-.16, .41, sign * .63]}
          rotation={[-sign * .20, sign * .36, sign * .04]}
          scale={[1.02, .09, .66]}>
          <sphereGeometry args={[.76, 24, 16]} />
          <meshStandardMaterial color="#b9efff" emissive="#65d8f2"
            emissiveIntensity={.17} transparent opacity={.62} side={THREE.DoubleSide}
            depthWrite={false} roughness={.08} metalness={.09} />
        </mesh>
        <mesh position={[-.62, .37, sign * .52]}
          rotation={[0, sign * .43, 0]} scale={[.56, .065, .44]}>
          <sphereGeometry args={[.65, 18, 12]} />
          <meshStandardMaterial color="#d4f5fc" transparent opacity={.48}
            depthWrite={false} side={THREE.DoubleSide} />
        </mesh>
      </group>)}
    </group>
    {kind === 'queen' && <group position={[.29, .5, 0]}>
      {[-.23, 0, .23].map((v, i) => <mesh key={i} position={[0, i === 1 ? .16 : 0, v]}>
        <coneGeometry args={[.16, .35, 5]} />
        <meshStandardMaterial color="#ffe69b" emissive="#f6c25e" emissiveIntensity={.3} />
      </mesh>)}
    </group>}
    {kind === 'handler' && <group position={[-.65, -.3, 0]}>
      <mesh><boxGeometry args={[.52, .25, .72]} />
        <meshStandardMaterial color="#5a4a76" metalness={.66} /></mesh>
      <mesh position={[0, -.02, .38]}>
        <boxGeometry args={[.17, .17, .1]} />
        <meshStandardMaterial color="#d9b1ff" emissive="#a575ef" /></mesh>
    </group>}
    {kind === 'worker' && <mesh position={[.96, -.11, 0]}>
      <sphereGeometry args={[.13, 12, 10]} />
      <meshStandardMaterial color="#b8eaff" emissive="#4abfee" emissiveIntensity={.65}/>
    </mesh>}
    <pointLight position={[.2,.38,0]} color={accent} intensity={.65} distance={3}/>
  </group>;
}

function HexCell({ x, y, z, lit }: { x: number; y: number; z: number; lit: boolean }) {
  return <group position={[x, y, z]} rotation={[Math.PI / 2, 0, 0]}>
    <mesh><cylinderGeometry args={[.18,.18,.055,6]}/>
      <meshStandardMaterial color="#5d4529" metalness={.37} roughness={.42}/></mesh>
    <mesh position={[0,.045,0]}>
      <cylinderGeometry args={[.135,.135,.035,6]}/>
      <meshStandardMaterial color={lit?'#fed973':'#d49d48'}
        emissive={lit?'#dca73d':'#3a2614'} emissiveIntensity={lit?.8:.15}/></mesh>
  </group>;
}

export function HiveStructure({ level, tint, failed }: {
  level: number; tint: string; failed: boolean;
}) {
  const root = level === 0;
  const radius = root ? .94 : level === 1 ? 1.04 : .79;
  return <group>
    {/* Hexagonal physical platform and recognizable layered beehive body */}
    <mesh position={[0,.16,0]} receiveShadow castShadow>
      <cylinderGeometry args={[radius+.27,radius+.34,.31,6]}/>
      <meshStandardMaterial color="#3b4750" metalness={.65} roughness={.35}/>
    </mesh>
    {root ? <group>
      <mesh position={[0,.87,0]} castShadow>
        <cylinderGeometry args={[.68,.84,1.2,6]}/>
        <meshStandardMaterial color="#263b43" metalness={.61}/>
      </mesh>
      <mesh position={[0,1.5,0]} rotation={[.32,0,.1]}>
        <boxGeometry args={[2.3,.075,1.0]}/>
        <meshStandardMaterial color="#2d5f7d" emissive="#16446d" emissiveIntensity={.4}/>
      </mesh>
      {[-.8,-.26,.26,.8].map(z=><Line key={z} points={[[-1.05,1.56,z],[1.05,1.56,z]]} color="#78cad8" lineWidth={1}/>)}
      <mesh position={[0,1.89,0]}>
        <sphereGeometry args={[.16,12,10]}/>
        <meshStandardMaterial color="#92f9e1" emissive="#64e6c0" emissiveIntensity={1}/>
      </mesh>
    </group> : <group>
      <mesh position={[0,.64,0]} castShadow>
        <cylinderGeometry args={[radius*.9,radius, .82, 6]}/>
        <meshStandardMaterial color={failed?'#5a3339':'#bb8b42'} metalness={.27} roughness={.64}/>
      </mesh>
      <mesh position={[0,1.08,0]} castShadow>
        <cylinderGeometry args={[radius*.72,radius*.89,.20,6]}/>
        <meshStandardMaterial color="#f1c667" metalness={.34} roughness={.38}/>
      </mesh>
      <mesh position={[0,1.24,0]} castShadow>
        <cylinderGeometry args={[radius*.48,radius*.73,.21,6]}/>
        <meshStandardMaterial color="#ad7a38" metalness={.32}/>
      </mesh>
      <mesh position={[0,1.39,0]} castShadow>
        <cylinderGeometry args={[.13,radius*.47,.25,6]}/>
        <meshStandardMaterial color="#d8ad55" metalness={.4}/>
      </mesh>
      {Array.from({length:6},(_,i)=> <group key={i} rotation={[0,i*Math.PI/3,0]}>
        <mesh position={[0,.65,radius*.89]}>
          <boxGeometry args={[radius*.55,.55,.09]}/>
          <meshStandardMaterial color="#3a3031" metalness={.55}/>
        </mesh>
        <HexCell x={-.22} y={.7} z={radius*.95} lit={!failed} />
        <HexCell x={.22} y={.7} z={radius*.95} lit={!failed} />
      </group>)}
      <mesh position={[0,.53,radius+.04]}>
        <boxGeometry args={[.58,.38,.07]}/>
        <meshStandardMaterial color="#152936" emissive={tint} emissiveIntensity={failed?0:.36}/>
      </mesh>
      <mesh position={[0,1.63,0]}>
        <sphereGeometry args={[.14,14,12]}/>
        <meshStandardMaterial color={failed?'#ff4b69':tint} emissive={failed?'#ff4b69':tint}
          emissiveIntensity={1.5}/>
      </mesh>
      {level === 1 && <mesh position={[0,1.86,0]}>
        <coneGeometry args={[.15,.33,6]}/>
        <meshStandardMaterial color="#ffe38e" emissive="#ffce63" emissiveIntensity={.5}/>
      </mesh>}
    </group>}
    <mesh rotation={[-Math.PI/2,0,0]} position={[0,.016,0]}>
      <ringGeometry args={[radius+0.38,radius+.46,48]}/>
      <meshBasicMaterial color={failed?'#fa6675':tint} side={THREE.DoubleSide}/>
    </mesh>
    <pointLight position={[0,1,0]} color={failed?'#ff5d77':tint}
      intensity={failed?.4:1.15} distance={4}/>
  </group>;
}

export function EggPod({ active }: { active: boolean }) {
  const pulse = useRef<THREE.Group>(null);
  useFrame(({ clock }) => {
    if (pulse.current && active) pulse.current.rotation.y = clock.elapsedTime * .43;
  });
  return <group>
    <mesh position={[0,.1,0]}>
      <cylinderGeometry args={[.38,.43,.18,6]}/>
      <meshStandardMaterial color="#53515c" metalness={.6}/>
    </mesh>
    {/* True egg silhouette: broad base tapering toward a smaller top */}
    <mesh position={[0,.52,0]} scale={[.48,.78,.48]} castShadow>
      <sphereGeometry args={[.74,24,20]}/>
      <meshStandardMaterial color={active?'#f9d4a6':'#f1cd87'}
        metalness={.5} roughness={.28} emissive={active?'#8f49ba':'#4d3718'}
        emissiveIntensity={active?.45:.11}/>
    </mesh>
    <mesh position={[0,.28,0]} rotation={[Math.PI/2,0,0]}>
      <torusGeometry args={[.36,.045,9,36]}/>
      <meshStandardMaterial color="#60577a" metalness={.71}/>
    </mesh>
    <group ref={pulse}>
      {[0,Math.PI*2/3,Math.PI*4/3].map((angle,i)=><group key={i}
        rotation={[0,angle,0]}>
        <mesh position={[0,.56,.365]} rotation={[-.12,0,0]}>
          <boxGeometry args={[.055,.65,.068]}/>
          <meshStandardMaterial color={active?'#b98afd':'#c78e41'}
            emissive={active?'#9f64e8':'#4f3517'} emissiveIntensity={.55}/>
        </mesh>
        {active&&<mesh position={[0,1.12,.28]}>
          <sphereGeometry args={[.065,9,9]}/>
          <meshStandardMaterial color="#e5bcff" emissive="#ba89ff" emissiveIntensity={1.3}/>
        </mesh>}
      </group>)}
    </group>
    {active&&<>
      <mesh position={[0,1.25,0]}>
        <cylinderGeometry args={[.035,.035,.55,7]}/>
        <meshStandardMaterial color="#a892b8" metalness={.6}/>
      </mesh>
      <mesh position={[0,1.56,0]}>
        <icosahedronGeometry args={[.12,1]}/>
        <meshStandardMaterial color="#ecceff" emissive="#b785fe" emissiveIntensity={1.7}/>
      </mesh>
      <pointLight position={[0,.9,0]} color="#b77bfa" intensity={2.6} distance={3.6}/>
    </>}
  </group>;
}
