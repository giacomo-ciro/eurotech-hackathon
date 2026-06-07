"use client";

import { useEffect, useMemo, useRef } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import type { TimeseriesPoint } from "../lib/types";

type Props = {
  points: TimeseriesPoint[];
  currentTime: number;
  task?: string;
  jointUnits?: string;
  heightClassName?: string;
};

type TwinHandles = {
  renderer: THREE.WebGLRenderer;
  scene: THREE.Scene;
  camera: THREE.OrthographicCamera;
  controls: OrbitControls;
  root: THREE.Group;
  pan: THREE.Group;
  shoulder: THREE.Group;
  elbow: THREE.Group;
  wristFlex: THREE.Group;
  wristRoll: THREE.Group;
  leftFinger: THREE.Mesh;
  rightFinger: THREE.Mesh;
  modelRoot: THREE.Group;
  mount: HTMLDivElement;
  frameId: number;
  resizeObserver: ResizeObserver;
};

const LINK_LENGTHS = {
  upper: 0.18,
  forearm: 0.16,
  wrist: 0.1,
  tool: 0.07,
};
const CAMERA_OFFSET = new THREE.Vector3(0.62, 0.42, 0.66);
const MIN_VIEW_WIDTH = 0.86;
const MIN_VIEW_HEIGHT = 0.58;
const FRAME_PADDING = 1.28;

function degToRad(value: number): number {
  return (value * Math.PI) / 180;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function interpolatePose(points: TimeseriesPoint[], t: number): number[] {
  if (points.length === 0) return [0, -70, 70, 35, 0, 1];
  if (t <= points[0].t) return points[0].joints;
  const last = points[points.length - 1];
  if (t >= last.t) return last.joints;

  let lo = 0;
  let hi = points.length - 1;
  while (hi - lo > 1) {
    const mid = Math.floor((lo + hi) / 2);
    if (points[mid].t <= t) lo = mid;
    else hi = mid;
  }

  const a = points[lo];
  const b = points[hi];
  const span = Math.max(b.t - a.t, 1e-6);
  const mix = (t - a.t) / span;
  return a.joints.map((v, i) => v + ((b.joints[i] ?? v) - v) * mix);
}

function makeBox(
  size: [number, number, number],
  color: number,
  position: [number, number, number],
): THREE.Mesh {
  const mesh = new THREE.Mesh(
    new THREE.BoxGeometry(size[0], size[1], size[2]),
    new THREE.MeshStandardMaterial({ color, roughness: 0.55, metalness: 0.08 }),
  );
  mesh.position.set(position[0], position[1], position[2]);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function makeJoint(radius: number, color = 0x111827): THREE.Mesh {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(radius, 24, 16),
    new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.15 }),
  );
  mesh.castShadow = true;
  return mesh;
}

function addLink(parent: THREE.Group, length: number, color: number): THREE.Group {
  const link = makeBox([length, 0.032, 0.036], color, [length / 2, 0, 0]);
  parent.add(link);
  const next = new THREE.Group();
  next.position.x = length;
  parent.add(next);
  return next;
}

function resetCamera(
  camera: THREE.OrthographicCamera,
  controls: OrbitControls,
  modelRoot: THREE.Object3D,
) {
  const bounds = new THREE.Box3().setFromObject(modelRoot);
  const target = new THREE.Vector3();
  bounds.getCenter(target);

  camera.position.copy(target).add(CAMERA_OFFSET);
  camera.zoom = 1;
  camera.lookAt(target);
  controls.target.copy(target);
  controls.update();
}

function fitCameraToModel(
  camera: THREE.OrthographicCamera,
  controls: OrbitControls,
  modelRoot: THREE.Object3D,
  mount: HTMLDivElement,
  renderer: THREE.WebGLRenderer,
) {
  const width = Math.max(mount.clientWidth, 1);
  const height = Math.max(mount.clientHeight, 1);
  const aspect = width / height;
  const bounds = new THREE.Box3().setFromObject(modelRoot);
  const size = new THREE.Vector3();
  bounds.getSize(size);

  const modelWidth = Math.max(size.x, size.z) * FRAME_PADDING;
  const modelHeight = Math.max(size.y + size.z * 0.45, size.x * 0.55) * FRAME_PADDING;
  const viewWidth = Math.max(MIN_VIEW_WIDTH, modelWidth, modelHeight * aspect);
  const viewHeight = Math.max(MIN_VIEW_HEIGHT, modelHeight, modelWidth / aspect);

  renderer.setSize(width, height, false);
  camera.left = -viewWidth / 2;
  camera.right = viewWidth / 2;
  camera.top = viewHeight / 2;
  camera.bottom = -viewHeight / 2;
  camera.updateProjectionMatrix();
  resetCamera(camera, controls, modelRoot);
}

function buildScene(mount: HTMLDivElement): TwinHandles {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b1220);

  const camera = new THREE.OrthographicCamera(-0.48, 0.48, 0.36, -0.36, 0.01, 10);

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.style.cursor = "grab";
  renderer.domElement.style.touchAction = "none";
  mount.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.enablePan = false;
  controls.minZoom = 0.25;
  controls.maxZoom = 3.5;
  controls.mouseButtons = {
    LEFT: THREE.MOUSE.ROTATE,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.ROTATE,
  };
  controls.touches = {
    ONE: THREE.TOUCH.ROTATE,
    TWO: THREE.TOUCH.DOLLY_ROTATE,
  };
  controls.addEventListener("start", () => {
    renderer.domElement.style.cursor = "grabbing";
  });
  controls.addEventListener("end", () => {
    renderer.domElement.style.cursor = "grab";
  });
  const modelRoot = new THREE.Group();
  scene.add(modelRoot);

  const ambient = new THREE.AmbientLight(0xffffff, 0.58);
  scene.add(ambient);
  const key = new THREE.DirectionalLight(0xffffff, 1.35);
  key.position.set(0.2, 0.8, 0.6);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  scene.add(key);

  const table = makeBox([0.72, 0.024, 0.46], 0x111827, [0.12, -0.014, 0]);
  table.receiveShadow = true;
  modelRoot.add(table);

  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(0.055, 0.072, 0.055, 40),
    new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.45, metalness: 0.2 }),
  );
  base.position.set(0, 0.028, 0);
  base.castShadow = true;
  base.receiveShadow = true;
  modelRoot.add(base);

  const root = new THREE.Group();
  root.position.set(0, 0.06, 0);
  modelRoot.add(root);

  const pan = new THREE.Group();
  root.add(pan);
  pan.add(makeJoint(0.03, 0x22d3ee));

  const shoulder = new THREE.Group();
  shoulder.position.y = 0.035;
  pan.add(shoulder);
  shoulder.add(makeJoint(0.028, 0xa78bfa));

  const elbow = addLink(shoulder, LINK_LENGTHS.upper, 0x38bdf8);
  elbow.add(makeJoint(0.024, 0x34d399));

  const wristFlex = addLink(elbow, LINK_LENGTHS.forearm, 0x5eead4);
  wristFlex.add(makeJoint(0.021, 0xfbbf24));

  const wristRoll = addLink(wristFlex, LINK_LENGTHS.wrist, 0xfcd34d);
  wristRoll.add(makeJoint(0.018, 0xf87171));
  wristRoll.add(makeBox([LINK_LENGTHS.tool, 0.018, 0.02], 0xe5e7eb, [LINK_LENGTHS.tool / 2, 0, 0]));

  const gripperRoot = new THREE.Group();
  gripperRoot.position.x = LINK_LENGTHS.tool;
  wristRoll.add(gripperRoot);
  const leftFinger = makeBox([0.042, 0.01, 0.01], 0xe5e7eb, [0.02, 0, 0.018]);
  const rightFinger = makeBox([0.042, 0.01, 0.01], 0xe5e7eb, [0.02, 0, -0.018]);
  gripperRoot.add(leftFinger, rightFinger);

  const resize = () => {
    fitCameraToModel(camera, controls, modelRoot, mount, renderer);
  };
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(mount);
  resize();

  const handles: TwinHandles = {
    renderer,
    scene,
    camera,
    controls,
    root,
    pan,
    shoulder,
    elbow,
    wristFlex,
    wristRoll,
    leftFinger,
    rightFinger,
    modelRoot,
    mount,
    frameId: 0,
    resizeObserver,
  };

  const animate = () => {
    handles.frameId = window.requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  };
  animate();

  return handles;
}

function applyPose(handles: TwinHandles, joints: number[]) {
  const pan = joints[0] ?? 0;
  const shoulder = joints[1] ?? -70;
  const elbow = joints[2] ?? 70;
  const wristFlex = joints[3] ?? 35;
  const wristRoll = joints[4] ?? 0;
  const gripper = joints[5] ?? 1;

  handles.pan.rotation.y = degToRad(pan);
  handles.shoulder.rotation.z = degToRad(shoulder + 92);
  handles.elbow.rotation.z = degToRad(elbow - 68);
  handles.wristFlex.rotation.z = degToRad(wristFlex - 45);
  handles.wristRoll.rotation.x = degToRad(wristRoll);

  const opening = 0.014 + clamp((gripper - 0.8) / 4.8, 0, 1) * 0.048;
  handles.leftFinger.position.z = opening;
  handles.rightFinger.position.z = -opening;

}

export function DigitalTwinViewer({
  points,
  currentTime,
  task,
  jointUnits = "degrees",
  heightClassName = "h-[320px]",
}: Props) {
  const mountRef = useRef<HTMLDivElement | null>(null);
  const handlesRef = useRef<TwinHandles | null>(null);
  const errorRef = useRef<HTMLDivElement | null>(null);
  const pose = useMemo(() => interpolatePose(points, currentTime), [points, currentTime]);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;
    let handles: TwinHandles;
    try {
      handles = buildScene(mount);
    } catch (err) {
      if (errorRef.current) {
        errorRef.current.textContent =
          err instanceof Error ? `3D renderer unavailable: ${err.message}` : "3D renderer unavailable";
      }
      return;
    }
    handlesRef.current = handles;
    applyPose(handles, pose);
    fitCameraToModel(handles.camera, handles.controls, handles.modelRoot, handles.mount, handles.renderer);
    return () => {
      window.cancelAnimationFrame(handles.frameId);
      handles.resizeObserver.disconnect();
      handles.controls.dispose();
      handles.renderer.dispose();
      mount.replaceChildren();
      handlesRef.current = null;
    };
  }, []);

  useEffect(() => {
    const handles = handlesRef.current;
    if (!handles) return;
    applyPose(handles, pose);
  }, [pose]);

  useEffect(() => {
    const handles = handlesRef.current;
    if (!handles || points.length === 0) return;
    applyPose(handles, interpolatePose(points, currentTime));
    fitCameraToModel(handles.camera, handles.controls, handles.modelRoot, handles.mount, handles.renderer);
  }, [points]);

  return (
    <section className="min-w-0">
      <div className="flex items-center justify-between mb-2">
        <h4 className="text-xs uppercase tracking-widest text-slate-400">Digital twin</h4>
        <span className="text-xs font-mono text-slate-500">
          {task || "trajectory"} · {jointUnits}
        </span>
      </div>
      <div className={`relative w-full overflow-hidden bg-slate-950 ${heightClassName}`}>
        <div ref={mountRef} className="absolute inset-0" />
        <button
          type="button"
          onClick={() => {
            const handles = handlesRef.current;
            if (handles) resetCamera(handles.camera, handles.controls, handles.modelRoot);
          }}
          className="absolute right-3 top-3 rounded-md border border-slate-700 bg-slate-950/85 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-slate-500 hover:text-slate-100"
        >
          Reset view
        </button>
        <div
          ref={errorRef}
          className="absolute inset-0 flex items-center justify-center px-4 text-center text-sm text-slate-500 pointer-events-none"
        />
      </div>
    </section>
  );
}
