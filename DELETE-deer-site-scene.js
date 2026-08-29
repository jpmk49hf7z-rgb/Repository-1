/* deer + almond — scroll-driven watercolour wilderness
 *
 * A slightly-off bird's-eye camera tracks a deer walking north through a
 * Manitoba boreal/prairie landscape. Scroll says where the deer *should* be;
 * the deer then walks there at an animal's pace, so a flick of the wheel reads
 * as the animal picking up into a trot rather than as a smear.
 *
 * Look: the landscape is a loose posterised wash. The deer is the only drawn
 * *character* on screen and is treated the way the foreground of a painted
 * animation is — hard-stepped cel shading and an ink contour the backgrounds
 * never get. Everything then goes through a paper pass: pigment granulation,
 * halftone in the shadows, chromatic offset and a paper-white wash on the
 * left/right thirds so the ink-dark type in the gutters keeps its contrast.
 */

import * as THREE from 'three';

/* ------------------------------------------------------------------ setup */

const canvas = document.getElementById('scene');
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
} catch (e) {
  document.body.classList.add('no-webgl');
  canvas.style.display = 'none';
  throw e;
}
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.setSize(innerWidth, innerHeight, false);
renderer.setClearColor(0xe9e3d4, 1);

const PAPER = new THREE.Color('#efe8d8');
const TAU = Math.PI * 2;

const clamp = (v, a, b) => (v < a ? a : v > b ? b : v);
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const hash1 = (n) => { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); };

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(PAPER.getHex(), 0.0044);

const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.5, 400);

/* Flat, graphic light — a warm key and a cool sky fill. No shadow maps:
   the posterise step supplies all the form we want.
   Intensities are scaled for three's physical lighting units (diffuse is
   divided by PI), which is what keeps the washes light instead of muddy. */
scene.add(new THREE.HemisphereLight(0xf4f0e4, 0x8d9a80, 2.5));
const key = new THREE.DirectionalLight(0xffeed2, 1.6);
key.position.set(-6, 12, 5);
scene.add(key);

/* A soft fill from the camera side, so tree flanks turned away from the key
   read as deep green rather than as black cut-outs. */
const fill = new THREE.DirectionalLight(0xdfe8ea, 0.9);
fill.position.set(7, 6, 14);
scene.add(fill);

/* ---------------------------------------------------- watercolour material */

const NOISE_GLSL = /* glsl */`
  float wc_hash(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123); }
  float wc_noise(vec2 p){
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(wc_hash(i), wc_hash(i + vec2(1,0)), u.x),
               mix(wc_hash(i + vec2(0,1)), wc_hash(i + vec2(1,1)), u.x), u.y);
  }
  float wc_fbm(vec2 p){
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 4; i++){ v += a * wc_noise(p); p *= 2.03; a *= 0.5; }
    return v;
  }
`;

/* Cel ramp for the deer: three hard steps, so light on the animal breaks into
   flat shapes with a crisp terminator instead of a smooth 3D gradient. */
const CEL_RAMP = (() => {
  const steps = new Uint8Array([96, 96, 96, 178, 178, 236, 255, 255]);
  const t = new THREE.DataTexture(steps, steps.length, 1, THREE.RedFormat);
  t.minFilter = t.magFilter = THREE.NearestFilter;
  t.needsUpdate = true;
  return t;
})();

/* Lambert (or, for the deer, toon) + injected pigment. `bleed` controls how
   far colour wanders from the base tone; `bands` sets the posterise steps. */
function watercolour(color, { bleed = 0.16, bands = 4.0, scale = 0.35, poster = 0.55, cel = false } = {}) {
  const mat = cel
    ? new THREE.MeshToonMaterial({ color, gradientMap: CEL_RAMP })
    : new THREE.MeshLambertMaterial({ color, flatShading: true });
  mat.onBeforeCompile = (shader) => {
    shader.uniforms.uBleed = { value: bleed };
    shader.uniforms.uBands = { value: bands };
    shader.uniforms.uScale = { value: scale };
    shader.uniforms.uPoster = { value: poster };

    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\n varying vec3 vWcPos;')
      .replace('#include <fog_vertex>',
        '#include <fog_vertex>\n vWcPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');

    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>',
        '#include <common>\n varying vec3 vWcPos;\n uniform float uBleed;\n uniform float uBands;\n uniform float uScale;\n uniform float uPoster;\n' + NOISE_GLSL)
      .replace('#include <dithering_fragment>', /* glsl */`
        #include <dithering_fragment>
        vec3 wcCol = gl_FragColor.rgb;

        // pigment pooling: two octaves at different scales, one warm one cool
        float n1 = wc_fbm(vWcPos.xz * uScale);
        float n2 = wc_fbm(vWcPos.xz * uScale * 3.7 + 31.4);
        wcCol += (n1 - 0.5) * uBleed * vec3(1.10, 0.94, 0.72);
        wcCol += (n2 - 0.5) * uBleed * 0.55 * vec3(0.62, 0.86, 1.05);

        // posterise into flat washes, with a soft edge so bands bleed
        vec3 q = floor(wcCol * uBands) / uBands;
        wcCol = mix(wcCol, q, uPoster);

        // dry-brush: let the paper show through the lightest passages
        float paperThrough = smoothstep(0.72, 0.98, dot(wcCol, vec3(0.299, 0.587, 0.114)));
        wcCol = mix(wcCol, vec3(0.937, 0.910, 0.847), paperThrough * 0.35 * n2);

        gl_FragColor.rgb = wcCol;
      `);
  };
  return mat;
}

/* ------------------------------------------------------------- the ground */

const TRACK = 430;     // world units the deer covers over a full scroll
const AMP   = 9;       // how far left/right the deer wanders
const WAVES = 5.0;     // full snake cycles across the whole page

/* Deer path: x as a function of z-progress. Everything else in the scene is
   scattered around it, never on top of it. */
function pathX(t) {
  return Math.sin(t * Math.PI * 2 * WAVES) * AMP
       + Math.sin(t * Math.PI * 2 * WAVES * 2.7) * AMP * 0.16;
}

const GROUND_W = 300;
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(GROUND_W, TRACK + 320, 150, 400),
  watercolour('#9fae86', { bleed: 0.055, bands: 6.0, scale: 0.045, poster: 0.28 })
);
ground.rotation.x = -Math.PI / 2;
const GROUND_OFF = -TRACK / 2 + 60;
ground.position.z = GROUND_OFF;

/* The plane is authored in local space then rotated flat, so a local Y maps
   to world z = GROUND_OFF - Y. Everything is displaced through the same
   world-space height function, which is what lets the deer and the trees
   sit exactly on the ground. */
const toWorldZ = (localY) => GROUND_OFF - localY;

{
  const pos = ground.geometry.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    pos.setZ(i, terrainH(pos.getX(i), toWorldZ(pos.getY(i))));
  }
  ground.geometry.computeVertexNormals();
}
scene.add(ground);

/* Rolling prairie with a river cut, in world coordinates. Kept deliberately
   flat near the deer path so the animal is never occluded by a ridge. */
function terrainH(x, z) {
  const h =
      Math.sin(x * 0.055) * 1.5 +
      Math.cos(z * 0.041) * 1.9 +
      Math.sin((x - z) * 0.018) * 2.6 +
      Math.sin(x * 0.17 - z * 0.11) * 0.5;
  const river = Math.exp(-Math.pow((x - riverX(z)) / 9, 2)) * 3.4;
  const corridor = Math.exp(-Math.pow(x / 34, 2)) * 0.7;   // flatten the lane
  return h * (1 - corridor) - river;
}
function riverX(z) { return Math.sin(z * 0.0075) * 16 + 58; }

/* Water: a ribbon built directly along the river centreline. Constructed by
   hand rather than by deforming a plane, so the normals are exactly up and
   the surface catches the key light instead of going black at grazing angles. */
{
  const STEPS = 300, HALF = 5.2;
  const zStart = 160, zEnd = -(TRACK + 220);
  const verts = [], norms = [], idx = [];
  for (let i = 0; i <= STEPS; i++) {
    const z = zStart + (zEnd - zStart) * (i / STEPS);
    const cx = riverX(z);
    verts.push(cx - HALF, -1.9, z, cx + HALF, -1.9, z);
    norms.push(0, 1, 0, 0, 1, 0);
    if (i < STEPS) {
      const a = i * 2;
      idx.push(a, a + 2, a + 1, a + 1, a + 2, a + 3);
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(norms, 3));
  g.setIndex(idx);
  const w = new THREE.Mesh(g, watercolour('#8fb4b7', { bleed: 0.05, bands: 4.0, scale: 0.09, poster: 0.35 }));
  scene.add(w);
}

/* ------------------------------------------------------------ vegetation */

const rng = mulberry32(20120501);
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* Scatter helper: rejects anything that would sit in the deer's lane or in
   the river, so the animal always reads clean against open ground. */
function scatter(count, minX, maxX, place, clear = 15) {
  const m = new THREE.Matrix4();
  const q = new THREE.Quaternion();
  const s = new THREE.Vector3();
  const p = new THREE.Vector3();
  const out = [];
  let guard = 0;
  while (out.length < count && guard++ < count * 30) {
    const z = -rng() * (TRACK + 150) + 100;
    const side = rng() < 0.5 ? -1 : 1;
    const x = side * (minX + rng() * (maxX - minX));
    if (Math.abs(x - pathX(-z / TRACK)) < clear) continue;   // deer lane
    if (Math.abs(x - riverX(z)) < 7) continue;               // river
    p.set(x, terrainH(x, z), z);
    const sc = 0.65 + rng() * 0.9;
    s.set(sc, sc * (0.8 + rng() * 0.6), sc);
    q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), rng() * Math.PI * 2);
    m.compose(p, q, s);
    out.push(m.clone());
  }
  out.forEach(place);
  return out.length;
}

function instanced(geo, mat, count, minX, maxX, yLift = 0, clear = 15) {
  const mesh = new THREE.InstancedMesh(geo, mat, count);
  let i = 0;
  const lift = new THREE.Matrix4().makeTranslation(0, yLift, 0);
  scatter(count, minX, maxX, (m) => mesh.setMatrixAt(i++, m.multiply(lift)), clear);
  mesh.count = i;
  mesh.instanceMatrix.needsUpdate = true;
  mesh.frustumCulled = false;
  scene.add(mesh);
  return mesh;
}

/* spruce: a stack of cones over a trunk reads as boreal at this camera height */
const spruceGeo = mergeTree([
  { r: 3.2, h: 6.4, y: 3.4 },
  { r: 2.2, h: 5.4, y: 7.0 },
  { r: 1.3, h: 4.0, y: 10.2 },
]);
instanced(spruceGeo, watercolour('#748b55', { bleed: 0.08, bands: 4.0, scale: 0.5, poster: 0.6 }), 260, 15, 135);

/* aspen / autumn scrub — the warm accents */
instanced(
  mergeTree([{ r: 3.0, h: 4.2, y: 2.6 }, { r: 1.9, h: 3.2, y: 4.9 }], 1.5),
  watercolour('#c1a068', { bleed: 0.09, bands: 4.0, scale: 0.6, poster: 0.6 }),
  170, 14, 125
);

/* low prairie brush, allowed much closer to the lane */
instanced(new THREE.IcosahedronGeometry(0.9, 0),
  watercolour('#9aab6b', { bleed: 0.07, bands: 4.0, scale: 1.2, poster: 0.5 }), 700, 3, 105, 0.35, 8);

/* glacial erratics */
instanced(new THREE.DodecahedronGeometry(1.15, 0),
  watercolour('#9d9787', { bleed: 0.05, bands: 4.0, scale: 1.0, poster: 0.5 }), 120, 5, 95, 0.3, 10);

/* Manual merge — keeps the dependency surface to three's core module.
   De-index first, so the buffer lengths are known before allocating.
   The trunk is merged into the crown rather than scattered separately, so a
   tree is always one object standing on the ground. */
function mergeTree(specs, trunkH = 2.6) {
  const parts = specs.map(({ r, h, y }) => {
    const g = new THREE.ConeGeometry(r, h, 7);
    g.translate(0, y, 0);
    return g.index ? g.toNonIndexed() : g;
  });
  const trunk = new THREE.CylinderGeometry(0.24, 0.4, trunkH, 5);
  trunk.translate(0, trunkH / 2, 0);
  parts.push(trunk.index ? trunk.toNonIndexed() : trunk);
  const len = parts.reduce((n, g) => n + g.attributes.position.array.length, 0);
  const pos = new Float32Array(len);
  const nor = new Float32Array(len);
  let o = 0;
  parts.forEach(g => {
    pos.set(g.attributes.position.array, o);
    nor.set(g.attributes.normal.array, o);
    o += g.attributes.position.array.length;
  });
  const merged = new THREE.BufferGeometry();
  merged.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  merged.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
  return merged;
}

/* ------------------------------------------------------------------ deer */

const DEER_SCALE = 2.85;

/* Ink contour, drawn as an inverted hull: every skin mesh gets a twin pushed
   out along its normals and rendered back-faces-only, which leaves a line
   around the silhouette *and* between overlapping limbs. The push is scaled by
   view depth so the line holds the same weight on screen however the camera
   moves — a drawn line, not a modelled one. */
const INK = new THREE.ShaderMaterial({
  uniforms: {
    uWidth: { value: 0.0027 },
    uInk:   { value: new THREE.Color('#42342a') },
  },
  vertexShader: /* glsl */`
    uniform float uWidth;
    void main(){
      vec4 mv = modelViewMatrix * vec4(position, 1.0);
      vec3 n = normalize(normalMatrix * normal);
      mv.xyz += n * uWidth * -mv.z;
      gl_Position = projectionMatrix * mv;
    }
  `,
  fragmentShader: /* glsl */`
    uniform vec3 uInk;
    void main(){ gl_FragColor = vec4(uInk, 1.0); }
  `,
  side: THREE.BackSide,
});

const hide     = watercolour('#c3a483', { cel: true, bleed: 0.045, bands: 8.0, scale: 1.5, poster: 0.2 });
const hideMid  = watercolour('#a8825d', { cel: true, bleed: 0.04, bands: 8.0, scale: 1.7, poster: 0.2 });
const hideDark = watercolour('#8c7057', { cel: true, bleed: 0.04, bands: 8.0, scale: 1.8, poster: 0.2 });
const cream    = watercolour('#f2e8d4', { cel: true, bleed: 0.05, bands: 8.0, scale: 2.0, poster: 0.2 });
const bone     = watercolour('#d9ccab', { cel: true, bleed: 0.07, bands: 8.0, scale: 2.2, poster: 0.2 });
const soot     = watercolour('#4a3a2c', { cel: true, bleed: 0.02, bands: 8.0, scale: 2.4, poster: 0.2 });

/* Every visible piece of the animal goes through here, so nothing can end up
   on screen without its ink line. */
function skin(geo, mat, parent, x = 0, y = 0, z = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  parent.add(m);
  m.add(new THREE.Mesh(geo, INK));
  return m;
}

const deer = new THREE.Group();
const rig  = new THREE.Group();     // gait bob, roll, pitch and breath live here
deer.add(rig);
const torso = new THREE.Group();    // squash and stretch, separately from the legs
rig.add(torso);

/* Proportions are taken off a white-tailed deer rather than eyeballed, because
   a quadruped reads as the wrong animal the moment they drift: withers at
   y = 2.05, so the body is 1.15 of that long, the barrel a quarter of it wide,
   the brisket a little over half of it off the ground, and the legs long and
   fine. Get those ratios wrong and you have drawn a llama.

   Capsules are authored along local Y and laid down along Z, which makes their
   local scale read as (width, length, depth). */
const chest = skin(new THREE.CapsuleGeometry(0.46, 0.50, 6, 16), hide, torso, 0, 1.58, -0.42);
chest.rotation.x = Math.PI / 2;
chest.scale.set(0.62, 1, 1);

const flank = skin(new THREE.CapsuleGeometry(0.40, 0.50, 6, 16), hide, torso, 0, 1.56, 0.48);
flank.rotation.x = Math.PI / 2;
flank.scale.set(0.66, 1, 1);

skin(new THREE.SphereGeometry(0.44, 16, 12), hide, torso, 0, 1.62, -0.72).scale.set(0.66, 0.97, 0.92);
skin(new THREE.SphereGeometry(0.47, 16, 12), hide, torso, 0, 1.58, 0.74).scale.set(0.72, 0.96, 0.92);

/* the rump flash: the one marking on a deer that a camera overhead can
   actually find, so it is the one that is worth modelling */
skin(new THREE.SphereGeometry(0.16, 14, 10), cream, torso, 0, 1.34, 1.20).scale.set(0.95, 1, 0.42);

/* Neck and head hang off their own pivots so they can lead and lag the body. */
const neckPivot = new THREE.Group();
neckPivot.position.set(0, 1.82, -0.88);
rig.add(neckPivot);

skin(new THREE.SphereGeometry(0.27, 12, 10), hide, neckPivot, 0, 0.02, 0.06).scale.set(0.8, 1, 1);
const neckMesh = skin(new THREE.CapsuleGeometry(0.20, 0.52, 5, 13), hide, neckPivot, 0, 0.375, -0.265);
neckMesh.rotation.x = -0.615;
neckMesh.scale.set(0.88, 1, 1);

const headPivot = new THREE.Group();
headPivot.position.set(0, 0.75, -0.53);
neckPivot.add(headPivot);

const skull = skin(new THREE.CapsuleGeometry(0.16, 0.16, 5, 12), hide, headPivot, 0, 0, -0.10);
skull.rotation.x = Math.PI / 2 - 0.22;
skull.scale.set(0.88, 1, 1);

const muzzle = skin(new THREE.CapsuleGeometry(0.105, 0.18, 4, 11), hide, headPivot, 0, -0.075, -0.45);
muzzle.rotation.x = Math.PI / 2 - 0.22;
muzzle.scale.set(0.9, 1, 1);

skin(new THREE.SphereGeometry(0.078, 9, 7), soot, headPivot, 0, -0.155, -0.635);
[-1, 1].forEach(s => skin(new THREE.SphereGeometry(0.05, 8, 6), soot, headPivot, 0.125 * s, 0.05, -0.185));

/* ears: their own pivots, because a deer that never flicks an ear is furniture */
const ears = [-1, 1].map(s => {
  const p = new THREE.Group();
  p.position.set(0.115 * s, 0.14, -0.02);
  p.rotation.set(-0.2, 0, 0.92 * s);
  headPivot.add(p);
  skin(new THREE.CapsuleGeometry(0.072, 0.15, 4, 10), cream, p, 0, 0.15, 0).scale.set(1, 1, 0.45);
  return p;
});

/* antlers: a swept beam per side with forward tines, built to read as a
   spreading fork from directly above rather than in profile */
[-1, 1].forEach(s => {
  const base = new THREE.Group();
  base.position.set(0.085 * s, 0.19, -0.05);
  base.rotation.set(-0.2, 0, 0.46 * s);
  headPivot.add(base);
  skin(new THREE.CylinderGeometry(0.032, 0.05, 0.38, 7), bone, base, 0, 0.18, 0);

  const upper = new THREE.Group();
  upper.position.set(0, 0.36, 0);
  upper.rotation.set(0.42, 0, 0.40 * s);
  base.add(upper);
  skin(new THREE.CylinderGeometry(0.022, 0.034, 0.44, 6), bone, upper, 0, 0.21, 0);

  const tine = (parent, y, len, rx, rz) => {
    const t = skin(new THREE.CylinderGeometry(0.015, 0.025, len, 6), bone, parent, 0, y, 0);
    t.rotation.set(rx, 0, rz);
    t.translateY(len / 2);
  };
  tine(base, 0.30, 0.32, -1.05, 0.14 * s);
  tine(upper, 0.18, 0.30, -1.00, 0.08 * s);
  tine(upper, 0.38, 0.24, -0.75, -0.12 * s);
});

/* Tail: brown on top and white underneath, which is the whole point of a
   white-tail. Hanging, the camera overhead sees only the brown; when the
   animal breaks into a trot the tail flags up and the white turns to face
   the camera all at once. */
const tailPivot = new THREE.Group();
tailPivot.position.set(0, 1.74, 1.13);
rig.add(tailPivot);
skin(new THREE.CapsuleGeometry(0.085, 0.20, 4, 10), hideMid, tailPivot, 0, -0.16, 0.06).scale.set(1.15, 1, 0.6);
skin(new THREE.CapsuleGeometry(0.072, 0.20, 4, 10), cream, tailPivot, 0, -0.16, -0.03).scale.set(1.1, 1, 0.38);

/* Legs. Each is a two-bone chain solved to a foot target rather than swung on
   a sine, which is what lets the hooves stay planted through the stance
   instead of skating. Hind legs are longer and far more angulated than the
   fore, which is most of what makes a quadruped read as a deer and not a dog.
   Order is [front-right, front-left, hind-right, hind-left]; +x is the
   animal's right, because it faces -z. */
const legs = [
  { x:  0.235, z: -0.70, hipY: 1.28, l1: 0.62, l2: 0.70 },
  { x: -0.235, z: -0.70, hipY: 1.28, l1: 0.62, l2: 0.70 },
  { x:  0.275, z:  0.72, hipY: 1.42, l1: 0.74, l2: 0.82 },
  { x: -0.275, z:  0.72, hipY: 1.42, l1: 0.74, l2: 0.82 },
].map((L, i) => {
  const fore = i < 2;
  skin(new THREE.CapsuleGeometry(fore ? 0.155 : 0.185, 0.22, 5, 11), hide, torso,
    L.x * 0.95, L.hipY + 0.1, L.z).scale.set(0.8, 1, 0.85);   // shoulder / thigh mass

  L.hip = new THREE.Group();
  L.hip.position.set(L.x, L.hipY, L.z);
  rig.add(L.hip);

  skin(new THREE.CapsuleGeometry(fore ? 0.105 : 0.125, L.l1 - 0.26, 4, 10), hide, L.hip, 0, -L.l1 / 2, 0)
    .scale.set(0.85, 1, 1);

  L.knee = new THREE.Group();
  L.knee.position.y = -L.l1;
  L.hip.add(L.knee);
  skin(new THREE.CapsuleGeometry(0.068, L.l2 - 0.30, 4, 9), hideMid, L.knee, 0, -(L.l2 - 0.14) / 2, 0);

  L.fet = new THREE.Group();
  L.fet.position.y = -(L.l2 - 0.14);
  L.knee.add(L.fet);
  skin(new THREE.CylinderGeometry(0.072, 0.056, 0.14, 8), soot, L.fet, 0, -0.07, 0);
  return L;
});

/* Footfall order. A walk is four-beat and lateral-sequence — left hind, left
   fore, right hind, right fore — and a trot is two-beat on diagonal pairs.
   The two sets are crossfaded as the animal changes pace. */
const WALK_PHASE = [0.75, 0.25, 0.50, 0.00];
const TROT_PHASE = [0.00, 0.50, 0.50, 0.00];

/* Two-bone IK in the sagittal plane. `fwd` is how far in front of the hip the
   hoof wants to be, `down` how far below it; the solution always puts the
   joint behind the hip-to-hoof line, which is the way both the carpus and the
   hock fold. */
function solveLeg(l1, l2, fwd, down) {
  const theta = Math.atan2(fwd, down);
  const d = Math.min(Math.hypot(fwd, down), (l1 + l2) * 0.999);
  const a = Math.acos(clamp((d * d + l1 * l1 - l2 * l2) / (2 * d * l1), -1, 1));
  const b = Math.acos(clamp((d * d - l1 * l1 - l2 * l2) / (2 * l1 * l2), -1, 1));
  return { hip: theta - a, knee: b };
}

deer.scale.setScalar(DEER_SCALE);
scene.add(deer);

/* Contact shadow: a soft ink ellipse laid on the terrain, offset along the key
   light. Without it the animal reads as pasted on top of the landscape rather
   than standing in it. */
const shadowGeo = new THREE.PlaneGeometry(1, 1);
shadowGeo.rotateX(-Math.PI / 2);
const shadow = new THREE.Mesh(shadowGeo, new THREE.ShaderMaterial({
  uniforms: { uInk: { value: new THREE.Color('#5e5847') }, uOpacity: { value: 0.34 } },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
  `,
  fragmentShader: /* glsl */`
    varying vec2 vUv;
    uniform vec3 uInk;
    uniform float uOpacity;
    void main(){
      float d = length(vUv - 0.5) * 2.0;
      gl_FragColor = vec4(uInk, smoothstep(1.0, 0.15, d) * uOpacity);
    }
  `,
  transparent: true,
  depthWrite: false,
}));
scene.add(shadow);

/* --------------------------------------------------------- the paper pass */

const rt = new THREE.WebGLRenderTarget(1, 1, {
  minFilter: THREE.LinearFilter,
  magFilter: THREE.LinearFilter,
  type: THREE.HalfFloatType,
});

const postScene = new THREE.Scene();
const postCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const postMat = new THREE.ShaderMaterial({
  uniforms: {
    tDiffuse: { value: rt.texture },
    uRes:     { value: new THREE.Vector2(1, 1) },
    uTime:    { value: 0 },
    uWash:    { value: 0.34 },   // how far the left/right thirds fade to paper
  },
  vertexShader: /* glsl */`
    varying vec2 vUv;
    void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }
  `,
  fragmentShader: /* glsl */`
    varying vec2 vUv;
    uniform sampler2D tDiffuse;
    uniform vec2 uRes;
    uniform float uTime;
    uniform float uWash;
    ${NOISE_GLSL}

    const vec3 PAPER = vec3(0.945, 0.921, 0.859);

    void main(){
      vec2 uv = vUv;
      vec2 fromCentre = uv - 0.5;

      // wet-edge warp: the whole frame sits on paper that never lies flat
      vec2 warp = vec2(
        wc_fbm(uv * 5.0 + uTime * 0.02),
        wc_fbm(uv * 5.0 - uTime * 0.02 + 17.0)
      ) - 0.5;
      uv += warp * 0.0035;

      // chromatic offset — separation grows toward the edges of the frame
      float sep = 0.0007 + length(fromCentre) * 0.0016;
      vec3 col;
      col.r = texture2D(tDiffuse, uv + fromCentre * sep).r;
      col.g = texture2D(tDiffuse, uv).g;
      col.b = texture2D(tDiffuse, uv - fromCentre * sep).b;

      // lift the pigment: watercolour gets its punch from saturated washes
      // sitting against near-white paper, not from mid-grey mud
      float lum = dot(col, vec3(0.299, 0.587, 0.114));
      col = clamp(mix(vec3(lum), col, 1.05), 0.0, 1.0);          // saturation
      col = clamp((col - 0.5) * 1.08 + 0.545, 0.0, 1.0);         // contrast
      lum = dot(col, vec3(0.299, 0.587, 0.114));

      // halftone dots, printed only into the shadows
      vec2 rot = vec2(uv.x * 0.866 - uv.y * 0.5, uv.x * 0.5 + uv.y * 0.866);
      vec2 cell = fract(rot * uRes / 5.5) - 0.5;
      float dot_ = smoothstep(0.36, 0.18, length(cell));
      float shadow = smoothstep(0.5, 0.14, lum);
      col = mix(col, col * 0.82, dot_ * shadow * 0.5);

      // pigment granulation on the paper tooth
      float grain = wc_fbm(uv * uRes / 2.2);
      col *= 0.96 + grain * 0.08;

      // paper wash on the outer thirds: guarantees contrast for the type in
      // the gutters without touching the deer's corridor
      float edge = smoothstep(0.17, 0.46, abs(fromCentre.x));
      col = mix(col, PAPER, edge * uWash);

      // top-of-frame bleed into bare paper, and a soft vignette
      col = mix(col, PAPER, smoothstep(0.42, 0.0, uv.y) * 0.10);
      col *= 1.0 - smoothstep(0.5, 1.0, length(fromCentre)) * 0.10;

      gl_FragColor = vec4(col, 1.0);
    }
  `,
});
postScene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), postMat));

/* --------------------------------------------------------------- resizing */

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  const dpr = renderer.getPixelRatio();
  rt.setSize(Math.round(w * dpr), Math.round(h * dpr));
  postMat.uniforms.uRes.value.set(w * dpr, h * dpr);
  // on narrow screens the layout stacks, so drop the gutter wash
  postMat.uniforms.uWash.value = w < 900 ? 0.0 : 0.34;
}
addEventListener('resize', resize);
resize();

/* ----------------------------------------------------------- scroll drive */

let target = 0;
function readScroll() {
  const max = document.documentElement.scrollHeight - innerHeight;
  target = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
}
addEventListener('scroll', readScroll, { passive: true });
readScroll();

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* The pace, in world units per second. The animal will amble, and it will trot
   to reel in a fast scroll, and it will do nothing faster than that — the cap
   is the whole point. MAX_LAG is the safety valve for an anchor jump, where
   there is no walk that would ever catch up. */
const AMBLE   = 4.2;
const TROT    = 14.0;
const MAX_LAG = 44;

let along = 0;          // world units of track actually walked
let speed = 0;          // current pace
let cycle = 0;          // gait cycle position, 0..1
let facing = 0;         // smoothed 0 or PI, so scrolling up turns the deer round
let heading = 1;
let yawSmooth = 0, yawLag = 0;
let stillFor = 0, graze = 0;
let last = 0;

along = target * TRACK;

const camPos = new THREE.Vector3();
const camAim = new THREE.Vector3();
const camWant = new THREE.Vector3();
const aimWant = new THREE.Vector3();
let camReady = false;

function frame(ms) {
  requestAnimationFrame(frame);
  const t = ms * 0.001;
  const dt = last ? Math.min(0.05, t - last) : 0.016;
  last = t;

  /* --- locomotion ------------------------------------------------------- */

  const want = target * TRACK;
  let gap = want - along;
  if (gap >  MAX_LAG) { along = want - MAX_LAG; gap =  MAX_LAG; }
  if (gap < -MAX_LAG) { along = want + MAX_LAG; gap = -MAX_LAG; }

  const dist = Math.abs(gap);
  const wantSpeed = dist < 0.4 ? 0 : clamp(dist * 0.85, 1.2, TROT);
  speed += (wantSpeed - speed) * Math.min(1, (wantSpeed > speed ? 4.5 : 3.0) * dt);
  if (speed < 0.05) speed = 0;

  let move = Math.sign(gap) * speed * dt;
  if (Math.abs(move) > dist) move = gap;
  if (reduced) { move = gap; speed = 0; }
  along += move;

  const u = along / TRACK;
  const x = pathX(u);
  const z = -along;
  const groundY = terrainH(x, z);
  deer.position.set(x, groundY, z);

  /* Face the way it is travelling. Scrolling back up is a real about-turn
     rather than a moonwalk, so the heading only flips once the animal is
     properly under way and the turn itself is eased. */
  if (speed > 1.0 && Math.abs(gap) > 0.6) heading = Math.sign(gap) || heading;
  facing += ((heading > 0 ? 0 : Math.PI) - facing) * Math.min(1, dt * 2.6);

  const look = 0.0012;
  const pathYaw = Math.atan2(pathX(u + look) - x, look * TRACK);
  const yaw = pathYaw + facing;
  deer.rotation.y = yaw;

  // how much the head has to catch up by: drives the neck's overlapping action
  const yawRate = dt > 0 ? (yaw - yawSmooth) / dt : 0;
  yawSmooth = yaw;
  yawLag += (yawRate - yawLag) * Math.min(1, dt * 4.0);

  /* --- gait ------------------------------------------------------------- */

  // 0 while standing, 1 once properly walking: everything the legs do is
  // faded in through this, so the animal settles onto its feet rather than
  // marching on the spot when the page goes quiet
  const g = smooth(0.3, 1.8, speed);
  const trotMix = smooth(AMBLE * 1.25, TROT * 0.72, speed);

  // stride lengthens with pace, and the cycle is clocked off distance covered
  // rather than off time, so the hooves cannot skate whatever the speed
  const strideLocal = 1.05 + Math.sqrt(Math.max(0, speed)) * 0.22;
  cycle += Math.abs(move) / (strideLocal * DEER_SCALE);
  cycle -= Math.floor(cycle);

  const duty = 0.66 + (0.44 - 0.66) * trotMix;   // fraction of the cycle on the ground
  const liftMax = 0.17 + 0.19 * trotMix;
  const sweep = strideLocal * duty;

  stillFor = g < 0.05 ? stillFor + dt : 0;

  /* --- body ------------------------------------------------------------- */

  // the withers rise and fall twice per cycle, and the barrel rolls once
  const bob = Math.sin(cycle * TAU * 2 + 0.5) * (0.035 + 0.045 * trotMix) * g;
  const breath = reduced ? 0 : Math.sin(t * 1.15) * 0.012 * (1 - g * 0.7);
  rig.position.y = bob + breath;

  // squash and stretch, tied to the bob rather than sprinkled on top of it
  const sq = bob * 0.6 + breath * 0.5;
  torso.scale.set(1 - sq * 0.55, 1 + sq, 1 - sq * 0.35);

  const gaitRoll = Math.sin(cycle * TAU) * (0.045 + 0.03 * trotMix) * g;
  const bank = clamp(-yawLag * 0.42, -0.16, 0.16);   // lean into the turns

  /* --- legs ------------------------------------------------------------- */

  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  let foreGround = 0, hindGround = 0, rightGround = 0, leftGround = 0;

  for (let i = 0; i < 4; i++) {
    const L = legs[i];
    const phase = WALK_PHASE[i] + (TROT_PHASE[i] - WALK_PHASE[i]) * trotMix;
    let p = cycle + phase;
    p -= Math.floor(p);

    let fwd, lift;
    if (p < duty) {
      // stance: the hoof is planted, so in body space it tracks straight back
      // at exactly the speed the body is moving forward
      fwd = sweep * (0.5 - p / duty);
      lift = 0;
    } else {
      // swing: forward on an eased arc, lifting fast and landing soft
      const q = (p - duty) / (1 - duty);
      fwd = sweep * (-0.5 + q * q * (3 - 2 * q));
      lift = liftMax * Math.sin(Math.PI * Math.pow(q, 0.85));
    }
    fwd *= g;
    lift *= g;

    // sample the terrain under this hoof so the deer walks the ground it is on
    const wx = deer.position.x + (L.x * cy + L.z * sy) * DEER_SCALE;
    const wz = deer.position.z + (-L.x * sy + L.z * cy) * DEER_SCALE;
    const hg = terrainH(wx, wz);
    if (i < 2) foreGround += hg * 0.5; else hindGround += hg * 0.5;
    if (i % 2 === 0) rightGround += hg * 0.5; else leftGround += hg * 0.5;

    L.down = rig.position.y + L.hipY + (deer.position.y - hg) / DEER_SCALE - lift;
    L.fwd = fwd;
    L.lift = lift;
  }

  // pitch and roll off the ground the hooves actually found
  const pitch = -Math.atan2(hindGround - foreGround, 1.42 * DEER_SCALE) * 0.75;
  const roll = Math.atan2(rightGround - leftGround, 0.51 * DEER_SCALE) * 0.55;
  rig.rotation.x = pitch;
  rig.rotation.z = roll + gaitRoll + bank;
  rig.rotation.y = Math.sin(cycle * TAU) * 0.03 * g;

  for (let i = 0; i < 4; i++) {
    const L = legs[i];
    const s = solveLeg(L.l1, L.l2, L.fwd, L.down);
    // the hip is a child of the pitched rig, so undo the pitch to keep the
    // legs plumb and the hooves where the terrain sample put them
    L.hip.rotation.x = s.hip - pitch;
    L.knee.rotation.x = s.knee;
    // level the hoof against the ground, toe dropping through the swing
    L.fet.rotation.x = clamp(-(s.hip + s.knee) + (L.lift / Math.max(liftMax, 1e-4)) * 0.45, -1.0, 1.0);
  }

  /* --- head, ears, tail: the parts that carry the life -------------------- */

  // the neck leads, the head trails and catches up a beat later
  neckPivot.rotation.y = clamp(-yawLag * 0.30, -0.30, 0.30);
  headPivot.rotation.y = clamp(-yawLag * 0.16, -0.22, 0.22) + Math.sin(t * 0.43) * 0.05 * (1 - g);

  // the deer grazes when the page has been still a while, and lifts its head
  // the moment it starts moving again
  const wantGraze = (!reduced && stillFor > 2.6) ? 0.5 + Math.sin(t * 0.5) * 0.12 : 0;
  graze += (wantGraze - graze) * Math.min(1, dt * (wantGraze > graze ? 0.9 : 3.5));

  const nod = Math.sin(cycle * TAU + 1.1) * 0.055 * g;
  neckPivot.rotation.x = graze * 0.95 + nod - pitch * 0.5;
  neckPivot.rotation.z = clamp(-yawLag * 0.14, -0.12, 0.12);
  // the head stays level while the body works underneath it
  headPivot.rotation.x = -graze * 0.35 - nod * 1.4 - pitch * 0.4 + 0.1 * g;

  if (!reduced) {
    ears.forEach((ear, i) => {
      // an ear twitches on its own clock, in short snaps rather than a wobble
      const p = t * 0.41 + i * 3.7;
      const n = Math.floor(p), f = p - n;
      const fire = hash1(n + i * 17) > 0.55 ? 1 : 0;
      const flick = fire * Math.exp(-f * 8.5) * Math.sin(f * 38);
      ear.rotation.x = -0.16 + flick * 0.5 - g * 0.18;
      ear.rotation.y = flick * 0.3 * (i ? 1 : -1);
    });
  }

  // the tail follows the body a beat late, and flags up at a trot
  tailPivot.rotation.x = -0.1 - trotMix * 1.25 - g * 0.15;
  tailPivot.rotation.z = Math.sin(t * 1.9 + cycle * TAU) * (0.14 + 0.2 * g) + clamp(yawLag * 0.5, -0.35, 0.35);

  /* --- contact shadow ---------------------------------------------------- */

  shadow.position.set(x + 1.1, groundY + 0.09, z - 0.8);
  shadow.rotation.y = yaw;
  const lifted = 1 + bob * 1.6;
  shadow.scale.set(4.1 * lifted, 1, 7.6 * lifted);
  shadow.material.uniforms.uOpacity.value = 0.34 / lifted;

  /* --- camera ------------------------------------------------------------ */

  // high enough to keep the deer's whole path in the clear centre lane, low
  // enough that the animal reads as a body in the round and not as a plan view
  camWant.set(x * 0.18, groundY + 22.5, z + 26.8);
  aimWant.set(x * 0.46, groundY + 2.6, z - 14.0);
  if (!camReady) { camPos.copy(camWant); camAim.copy(aimWant); camReady = true; }
  camPos.lerp(camWant, Math.min(1, dt * 3.2));
  camAim.lerp(aimWant, Math.min(1, dt * 2.6));
  camera.position.copy(camPos);
  camera.lookAt(camAim);
  camera.rotation.z = Math.sin(u * 6.0) * 0.012;

  postMat.uniforms.uTime.value = t;

  renderer.setRenderTarget(rt);
  renderer.render(scene, camera);
  renderer.setRenderTarget(null);
  renderer.render(postScene, postCam);
}
requestAnimationFrame(frame);
