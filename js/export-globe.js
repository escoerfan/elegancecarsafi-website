/* =========================================================================
   3D-Globus der Export-Sektion (normales Skript mit dynamischen Imports,
   damit der Globus auch beim direkten Öffnen der HTML-Datei läuft)
   ========================================================================= */
(() => {
const reducedMotion = window
  .matchMedia("(prefers-reduced-motion: reduce)")
  .matches;

const canvases = Array
  .from(document.querySelectorAll("[data-ecs-export-globe]"))
  .filter((canvas) => !canvas.dataset.ecsExportInitialized);

canvases.forEach((canvas) => {
  canvas.dataset.ecsExportInitialized = "true";

  const start = () => {
    initEcsExportGlobe(canvas).catch(() => {
      canvas.style.display = "none";
    });
  };

  /* Erst laden, wenn der Globus in die Nähe des Bildschirms kommt */
  if (!("IntersectionObserver" in window)) {
    start();
    return;
  }

  const nearObserver = new IntersectionObserver((entries) => {
    if (!entries.some((entry) => entry.isIntersecting)) return;
    nearObserver.disconnect();
    start();
  }, { rootMargin: "1000px 0px" });

  nearObserver.observe(canvas);
});

async function initEcsExportGlobe(canvas) {
  const THREE = await import(
    "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.min.js"
  );

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    alpha: true,
    powerPreference: "high-performance"
  });

  renderer.setClearColor(0x000000, 0);
  renderer.setPixelRatio(
    Math.min(window.devicePixelRatio || 1, 2)
  );

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
  camera.position.set(0, 0, 7.5);

  const globeGroup = new THREE.Group();

  const baseRotationX = THREE.MathUtils.degToRad(30);
  const baseRotationY = THREE.MathUtils.degToRad(-98);
  const baseRotationZ = THREE.MathUtils.degToRad(-3);

  globeGroup.rotation.set(
    baseRotationX,
    baseRotationY,
    baseRotationZ
  );

  scene.add(globeGroup);

  const globeRadius = 2;
  const routeTone = new THREE.Color("#d9d6cf");

  /* Weltkarte als fertiges Bild (früher bei jedem Aufruf mit d3 aus dem
     Weltatlas gezeichnet – das blockierte die Seite mehrere Sekunden) */
  const worldTexture = await new THREE.TextureLoader().loadAsync(
    "assets/img/globus-textur.webp"
  );
  worldTexture.colorSpace = THREE.SRGBColorSpace;
  worldTexture.anisotropy = 8;

  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(globeRadius, 80, 80),
    new THREE.MeshBasicMaterial({
      color: new THREE.Color("#ffffff"),
      map: worldTexture
    })
  );

  globeGroup.add(sphere);

  const atmosphere = new THREE.Mesh(
    new THREE.SphereGeometry(
      globeRadius * 1.012,
      96,
      96
    ),
    new THREE.MeshBasicMaterial({
      color: new THREE.Color("#f2f0eb"),
      transparent: true,
      opacity: 0.045,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      depthWrite: false
    })
  );

  globeGroup.add(atmosphere);

  const routeMaterial = new THREE.MeshBasicMaterial({
    color: routeTone,
    transparent: true,
    opacity: 0.55,
    depthWrite: false
  });

  function latLngToVector3(
    lat,
    lng,
    radius = globeRadius
  ) {
    const phi = THREE.MathUtils.degToRad(90 - lat);
    const theta = THREE.MathUtils.degToRad(lng + 180);

    return new THREE.Vector3(
      -radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }

  function makeArc(
    start,
    end,
    lift = 0.18,
    segments = 44
  ) {
    const a = latLngToVector3(
      start[0],
      start[1],
      globeRadius * 1.018
    );

    const b = latLngToVector3(
      end[0],
      end[1],
      globeRadius * 1.018
    );

    const points = [];

    for (let i = 0; i <= segments; i += 1) {
      const t = i / segments;

      const p = new THREE.Vector3()
        .copy(a)
        .lerp(b, t)
        .normalize();

      const height = globeRadius * (
        1.018 + Math.sin(Math.PI * t) * lift
      );

      points.push(p.multiplyScalar(height));
    }

    return points;
  }

  function makeRoute(start, end) {
    const points = makeArc(start, end);
    const curve = new THREE.CatmullRomCurve3(points);
    const radialSegments = 6;

    const drawGeometry = new THREE.TubeGeometry(
      curve,
      points.length - 1,
      0.006,
      radialSegments,
      false
    );

    drawGeometry.setDrawRange(0, 0);

    const route = new THREE.Mesh(
      drawGeometry,
      routeMaterial
    );

    route.userData.drawGeometry = drawGeometry;
    route.userData.segmentIndexCount =
      radialSegments * 6;
    route.userData.segmentCount =
      points.length - 1;

    globeGroup.add(route);

    return route;
  }

  const start = [52.32, 9.61];

  const destinations = [
    [52.37, 4.90],
    [51.22, 4.40],
    [48.86, 2.35],
    [45.46, 9.19],
    [48.21, 16.37],
    [44.81, 20.46],
    [42.70, 23.32],
    [44.43, 26.10],
    [41.33, 19.82],
    [36.75, 3.06],
    [33.57, -7.59],
    [36.81, 10.18],
    [30.04, 31.24],
    [41.72, 44.78],
    [41.31, 69.24],
    [43.24, 76.89],
    [25.20, 55.27],
    [24.45, 54.38],
    [24.71, 46.68],
    [21.49, 39.19],
    [31.95, 35.91]
  ];

  const routes = destinations.map(
    (destination) => makeRoute(start, destination)
  );

  const widget = canvas.closest(
    ".ecs-export-widget"
  );

  const scrollViews = [window];
  let routeProgress = 0;

  try {
    let currentView = window;

    while (
      currentView.parent !== currentView &&
      currentView.frameElement
    ) {
      currentView = currentView.parent;
      scrollViews.push(currentView);
    }
  } catch (_) {
    /*
     * Falls Onepage einen fremden Iframe verwendet,
     * bleibt die aktuelle Fensterposition als Fallback.
     */
  }

  function updateRoutes() {
    routes.forEach((route) => {
      const visibleSegments = Math.round(
        routeProgress *
        route.userData.segmentCount
      );

      const visibleIndexCount =
        visibleSegments *
        route.userData.segmentIndexCount;

      route.userData.drawGeometry.setDrawRange(
        0,
        visibleIndexCount
      );
    });
  }

  function getViewportMetrics() {
    const widgetRect = widget.getBoundingClientRect();

    let top = widgetRect.top;
    let height = widgetRect.height;
    let viewportHeight = window.innerHeight;

    try {
      let currentView = window;

      while (
        currentView.parent !== currentView &&
        currentView.frameElement
      ) {
        const frame = currentView.frameElement;
        const frameRect =
          frame.getBoundingClientRect();

        const scaleY = frame.clientHeight
          ? frameRect.height / frame.clientHeight
          : 1;

        top = frameRect.top + top * scaleY;
        height *= scaleY;

        currentView = currentView.parent;
        viewportHeight = currentView.innerHeight;
      }
    } catch (_) {
      /*
       * Fallback für nicht zugängliche Parent-Frames.
       */
    }

    return {
      top,
      height,
      viewportHeight
    };
  }

  function updateRouteProgress() {
    const metrics = getViewportMetrics();

    /*
     * Die Animation beginnt erst, wenn der Ursprung
     * am rechten unteren Globe-Rand sichtbar wird.
     */
    const startY =
      metrics.viewportHeight * 0.42;

    /*
     * Sie endet, während der Globe noch sichtbar ist.
     */
    const endY =
      metrics.viewportHeight * 0.70 -
      metrics.height;

    const rawProgress =
      (startY - metrics.top) /
      Math.max(1, startY - endY);

    routeProgress = THREE.MathUtils.clamp(
      rawProgress,
      0,
      1
    );

    updateRoutes();
  }

  function resize() {
    const rect =
      canvas.parentElement.getBoundingClientRect();

    const width = Math.max(
      1,
      Math.floor(rect.width)
    );

    const height = Math.max(
      1,
      Math.floor(rect.height)
    );

    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    updateRouteProgress();

    /* Ohne Animationsschleife (Bewegung reduzieren) sonst leer nach Größenänderung */
    if (reducedMotion) {
      renderer.render(scene, camera);
    }
  }

  function handleScroll() {
    updateRouteProgress();

    if (reducedMotion) {
      renderer.render(scene, camera);
    }
  }

  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(canvas.parentElement);

  scrollViews.forEach((view) => {
    view.addEventListener(
      "scroll",
      handleScroll,
      { passive: true }
    );

    view.document.addEventListener(
      "scroll",
      handleScroll,
      {
        passive: true,
        capture: true
      }
    );

    view.addEventListener(
      "resize",
      handleScroll,
      { passive: true }
    );
  });

  resize();
  updateRouteProgress();

  /* Außerhalb des Bildschirms pausiert die Animation */
  let onScreen = true;
  let frameId = 0;

  new IntersectionObserver((entries) => {
    onScreen = entries[entries.length - 1].isIntersecting;

    if (onScreen && !frameId && !reducedMotion) {
      frameId = requestAnimationFrame(animate);
    }
  }).observe(canvas);

  function animate(time = 0) {
    frameId = 0;

    if (!reducedMotion) {
      globeGroup.rotation.x =
        baseRotationX +
        Math.sin(time * 0.00018) * 0.025;

      globeGroup.rotation.y =
        baseRotationY +
        Math.sin(time * 0.00016) * 0.08;

      globeGroup.rotation.z =
        baseRotationZ +
        Math.sin(time * 0.00012) * 0.012;
    }

    /*
     * Der Fortschritt wird in jedem Frame gelesen.
     * Dadurch funktioniert es auch mit Onepage-
     * Scrollcontainern und Smooth-Scrolling.
     */
    updateRouteProgress();
    renderer.render(scene, camera);

    if (!reducedMotion && onScreen) {
      frameId = requestAnimationFrame(animate);
    }
  }

  animate();
}
})();
