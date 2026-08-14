/* deer + almond — scroll-driven watercolour wilderness
 *
 * A slightly-off bird's-eye camera tracks a deer walking north through a
 * Manitoba boreal/prairie landscape. Scroll drives the deer forward; the deer
 * snakes left-right across the centre corridor of the screen, which the page
 * layout keeps free of text.
 *
 * Look: everything is rendered flat-lit and posterised, then run through a
 * paper pass — pigment granulation, halftone in the shadows, chromatic
 * offset and a paper-white wash on the left/right thirds so the ink-dark
 * type in the gutters always keeps its contrast.
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

/* Lambert + injected pigment. `bleed` controls how far colour wanders from
   the base tone; `bands` sets the posterisation step count. */
function watercolour(color, { bleed = 0.16, bands = 4.0, scale = 0.35, poster = 0.55 } = {}) {
  const mat = new THREE.MeshLambertMaterial({ color, flatShading: true });
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

const TRACK = 900;     // world units the deer covers over a full scroll
const AMP   = 8;       // how far left/right the deer wanders
const WAVES = 5.5;     // full snake cycles across the whole page

/* Deer path: x as a function of z-progress. Everything else in the scene is
   scattered around it, never on top of it. */
function pathX(t) {
  return Math.sin(t * Math.PI * 2 * WAVES) * AMP
       + Math.sin(t * Math.PI * 2 * WAVES * 2.7) * AMP * 0.16;
}

const GROUND_W = 300;
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(GROUND_W, TRACK + 260, 150, 420),
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
  const zStart = 140, zEnd = -(TRACK + 200);
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
    const z = -rng() * (TRACK + 140) + 90;
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

const deer = new THREE.Group();
const hide     = watercolour('#bfa183', { bleed: 0.035, bands: 6.0, scale: 1.6, poster: 0.4 });
const hideDark = watercolour('#8d7259', { bleed: 0.03, bands: 6.0, scale: 1.8, poster: 0.4 });
const cream    = watercolour('#ece0ca', { bleed: 0.05, bands: 3.0, scale: 2.0 });
const bone     = watercolour('#cfc2a5', { bleed: 0.10, bands: 3.0, scale: 2.2 });

function part(geo, mat, x, y, z, rx = 0, rz = 0) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, y, z);
  m.rotation.x = rx; m.rotation.z = rz;
  deer.add(m);
  return m;
}

/* body */
const body = part(new THREE.CapsuleGeometry(0.52, 1.6, 3, 8), hide, 0, 1.42, 0, Math.PI / 2);
body.scale.set(1, 1, 0.8);
part(new THREE.CapsuleGeometry(0.5, 0.5, 3, 8), cream, 0, 1.15, 0.35, Math.PI / 2).scale.set(0.9, 1, 0.7);

/* neck + head */
const neck = part(new THREE.CapsuleGeometry(0.3, 0.9, 3, 7), hide, 0, 2.05, -1.05, -0.55);
const head = part(new THREE.CapsuleGeometry(0.25, 0.55, 3, 7), hide, 0, 2.62, -1.62, Math.PI / 2.2);
part(new THREE.SphereGeometry(0.1, 6, 5), hideDark, 0, 2.52, -2.05);
part(new THREE.ConeGeometry(0.13, 0.34, 5), cream, 0.2, 2.85, -1.45, 0, 0.8);
part(new THREE.ConeGeometry(0.13, 0.34, 5), cream, -0.2, 2.85, -1.45, 0, -0.8);

/* antlers */
[-1, 1].forEach(s => {
  part(new THREE.CylinderGeometry(0.05, 0.07, 0.7, 5), bone, 0.15 * s, 3.05, -1.52, -0.3, 0.62 * s);
  part(new THREE.CylinderGeometry(0.035, 0.045, 0.44, 5), bone, 0.46 * s, 3.28, -1.74, -0.6, 1.1 * s);
  part(new THREE.CylinderGeometry(0.035, 0.045, 0.38, 5), bone, 0.4 * s, 3.34, -1.28, 0.45, 0.75 * s);
});

/* tail */
part(new THREE.ConeGeometry(0.16, 0.42, 5), cream, 0, 1.75, 1.02, 0.9);

/* legs: upper + lower, animated in a two-beat gait */
const legs = [];
[[0.46, -0.74], [-0.46, -0.74], [0.5, 0.8], [-0.5, 0.8]].forEach(([x, z], i) => {
  const hip = new THREE.Group();
  hip.position.set(x, 1.32, z);
  const upper = new THREE.Mesh(new THREE.CapsuleGeometry(0.13, 0.62, 3, 6), hide);
  upper.position.y = -0.36;
  const knee = new THREE.Group();
  knee.position.y = -0.72;
  const lower = new THREE.Mesh(new THREE.CapsuleGeometry(0.09, 0.6, 3, 6), hideDark);
  lower.position.y = -0.34;
  const hoof = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.08, 0.16, 5), hideDark);
  hoof.position.y = -0.7;
  knee.add(lower, hoof);
  hip.add(upper, knee);
  deer.add(hip);
  legs.push({ hip, knee, phase: (i === 0 || i === 3) ? 0 : Math.PI });
});

deer.scale.setScalar(2.2);
scene.add(deer);

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

let target = 0, current = 0, travelled = 0;

function readScroll() {
  const max = document.documentElement.scrollHeight - innerHeight;
  target = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
}
addEventListener('scroll', readScroll, { passive: true });
readScroll();
current = target;

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const tmp = new THREE.Vector3();

function frame(ms) {
  requestAnimationFrame(frame);
  const t = ms * 0.001;

  const prev = current;
  current += (target - current) * (reduced ? 1 : 0.075);
  const step = Math.abs(current - prev) * TRACK;
  travelled += step;

  // deer position along the snaking path
  const z = -current * TRACK;
  const x = pathX(current);
  const y = terrainH(x, z);
  deer.position.set(x, y, z);

  // face the direction of travel
  const dt = 0.0008;
  const ahead = pathX(Math.min(1, current + dt));
  deer.rotation.y = Math.atan2(ahead - x, dt * TRACK);

  // gait: stride length tied to real distance, plus an idle amble when the
  // page is still, so the animal never freezes mid-step
  const idle = reduced ? 0 : t * 1.1;
  const stride = travelled * 1.15 + idle;
  legs.forEach(({ hip, knee, phase }) => {
    const s = Math.sin(stride + phase);
    hip.rotation.x = s * 0.55;
    knee.rotation.x = Math.max(0, -Math.cos(stride + phase)) * 0.6;
  });
  deer.position.y += Math.abs(Math.sin(stride)) * 0.07;   // shoulder bob
  head.rotation.z = Math.sin(stride * 0.5) * 0.06;
  neck.rotation.x = -0.55 + Math.sin(stride * 0.5) * 0.04;

  // camera: high and slightly behind — an off bird's-eye that keeps the deer
  // in the clear centre lane while the type sits in the gutters
  const lag = x * 0.22;                       // a little sway, never a follow
  camera.position.set(lag, y + 42, z + 34);
  tmp.set(x * 0.35, y + 1.5, z - 13);
  camera.lookAt(tmp);
  camera.rotation.z = Math.sin(current * 6.0) * 0.012;

  postMat.uniforms.uTime.value = t;

  renderer.setRenderTarget(rt);
  renderer.render(scene, camera);
  renderer.setRenderTarget(null);
  renderer.render(postScene, postCam);
}
requestAnimationFrame(frame);
