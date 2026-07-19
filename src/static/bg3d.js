import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js";

const canvas = document.getElementById("bg");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, 2, 0.1, 1000);
camera.position.set(0, 0, 18);

const group = new THREE.Group();
scene.add(group);

// Lumière
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dir = new THREE.DirectionalLight(0xffffff, 1.2);
dir.position.set(5, 10, 7);
scene.add(dir);

// Objet 3D
const geo = new THREE.TorusKnotGeometry(4, 1.2, 220, 32);
const mat = new THREE.MeshStandardMaterial({
  color: 0x2aa6ff,
  metalness: 0.6,
  roughness: 0.25,
  emissive: 0x061a2b,
  emissiveIntensity: 0.7
});
const mesh = new THREE.Mesh(geo, mat);
group.add(mesh);

// Particules
const pCount = 1200;
const pGeo = new THREE.BufferGeometry();
const pos = new Float32Array(pCount * 3);
for (let i = 0; i < pCount * 3; i += 3) {
  pos[i] = (Math.random() - 0.5) * 120;
  pos[i + 1] = (Math.random() - 0.5) * 70;
  pos[i + 2] = (Math.random() - 0.5) * 120;
}
pGeo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
const pMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.08, transparent: true, opacity: 0.65 });
const points = new THREE.Points(pGeo, pMat);
scene.add(points);

function resize() {
  const w = window.innerWidth;
  const h = window.innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
window.addEventListener("resize", resize);
resize();

let t = 0;
function animate() {
  t += 0.006;
  group.rotation.x = t * 0.7;
  group.rotation.y = t * 0.9;
  points.rotation.y = t * 0.15;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
animate();
