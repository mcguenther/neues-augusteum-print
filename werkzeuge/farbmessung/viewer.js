/* 3D-Betrachter des Farbvergleichs: Modell vorher/nachher mit Trennregler, Änderungskarte, Ansichten.
   Daten: <script type="application/json" id="modelldaten"> (werkzeuge/farbmessung/modell_export.py),
   Bibliotheken: three.js r128 und OrbitControls (Klassik-Skripte). Kein Build-Schritt. */
(function () {
  var root = document.getElementById('viewer3d');
  if (!root) return;
  var canvas = root.querySelector('canvas');
  var meldung = root.querySelector('.meldung');
  function fehler(text) {
    if (meldung) { meldung.textContent = text; meldung.hidden = false; }
  }
  if (typeof THREE === 'undefined' || !THREE.OrbitControls) {
    fehler('Der 3D-Betrachter lädt three.js aus dem Netz und konnte es nicht laden. Die Bilder unten zeigen dasselbe.');
    return;
  }
  if (typeof DecompressionStream === 'undefined') {
    fehler('Dieser Browser kann die Modelldaten nicht entpacken (DecompressionStream fehlt). Bitte einen aktuellen Browser nehmen.');
    return;
  }
  var daten = JSON.parse(document.getElementById('modelldaten').textContent);
  var HEISS = ['#c9ced1', '#f2d04f', '#ee8a2b', '#c4234f'];   // Änderungsklassen 0..3

  var renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
  } catch (e) {
    fehler('WebGL ist in diesem Browser nicht verfügbar, der 3D-Betrachter bleibt aus.');
    return;
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.setClearColor(0x000000, 0);

  var camera = new THREE.PerspectiveCamera(32, 1, 5, 4000);
  var controls = new THREE.OrbitControls(camera, canvas);
  controls.enableDamping = false;
  controls.maxPolarAngle = Math.PI * 0.49;
  controls.minDistance = 25;
  controls.maxDistance = 1600;
  controls.screenSpacePanning = true;

  function szene() {
    var s = new THREE.Scene();
    s.add(new THREE.HemisphereLight(0xffffff, 0x9aa4ab, 0.78));
    var sonne = new THREE.DirectionalLight(0xffffff, 0.62);
    sonne.position.set(-260, 420, 180);       // von Südost-Ost, schräg oben: Fassaden zum Platz bekommen Licht
    s.add(sonne);
    var boden = new THREE.Mesh(new THREE.CircleGeometry(900, 64).rotateX(-Math.PI / 2),
      new THREE.MeshBasicMaterial({ color: 0xffffff }));
    boden.position.y = -0.15;
    boden.name = 'boden';
    s.add(boden);
    return s;
  }
  var szA = szene(), szB = szene(), szD = szene();

  function linear(hex) { return new THREE.Color(hex).convertSRGBToLinear(); }

  function bodenfarbe() {
    var c = getComputedStyle(root).getPropertyValue('--boden').trim() || '#e4e8ea';
    var col = linear(c);
    [szA, szB, szD].forEach(function (s) { s.getObjectByName('boden').material.color.copy(col); });
  }

  function entpacke(b64) {
    var bin = atob(b64), n = bin.length, u8 = new Uint8Array(n);
    for (var i = 0; i < n; i++) u8[i] = bin.charCodeAt(i);
    var strom = new Blob([u8]).stream().pipeThrough(new DecompressionStream('deflate'));
    return new Response(strom).arrayBuffer();
  }

  function lies(b) {
    return entpacke(b.bin).then(function (buf) {
      var o = 0;
      var v = new Uint16Array(buf.slice(o, o + b.nv * 6)); o += b.nv * 6;
      var f = new Uint32Array(buf.slice(o, o + b.nf * 12)); o += b.nf * 12;
      var c = new Uint8Array(buf, o, b.nf); o += b.nf;
      var d = new Uint8Array(buf, o, b.nf);
      return { v: v, f: f, c: c, d: d, nf: b.nf, pal: b.pal };
    });
  }

  function positionen(m) {
    var r = daten.raster, lo = daten.lo, pos = new Float32Array(m.nf * 9), i, k, vi;
    for (i = 0; i < m.nf; i++) {
      for (k = 0; k < 3; k++) {
        vi = m.f[i * 3 + k] * 3;
        pos[i * 9 + k * 3] = lo[0] + m.v[vi] * r;
        pos[i * 9 + k * 3 + 1] = lo[2] + m.v[vi + 2] * r;      // z (hoch) -> y von three.js
        pos[i * 9 + k * 3 + 2] = -(lo[1] + m.v[vi + 1] * r);   // y (Nord) -> -z
      }
    }
    return pos;
  }

  function farbpuffer(m, index, tabelle) {
    var col = new Float32Array(m.nf * 9), i, k, t;
    for (i = 0; i < m.nf; i++) {
      t = tabelle[index[i]];
      for (k = 0; k < 3; k++) {
        col[i * 9 + k * 3] = t.r; col[i * 9 + k * 3 + 1] = t.g; col[i * 9 + k * 3 + 2] = t.b;
      }
    }
    return new THREE.BufferAttribute(col, 3);
  }

  function netz(posAttr, farbAttr) {
    var g = new THREE.BufferGeometry();
    g.setAttribute('position', posAttr);
    g.setAttribute('color', farbAttr);
    g.computeBoundingSphere();
    return new THREE.Mesh(g, new THREE.MeshPhongMaterial({
      vertexColors: true, flatShading: true, shininess: 0, specular: 0x000000
    }));
  }

  var modus = 'teilen', anteil = 0.37, bereit = false;

  function groesse() {
    var w = canvas.clientWidth, h = canvas.clientHeight;
    if (!w || !h) return false;
    var pr = renderer.getPixelRatio();
    if (canvas.width !== Math.round(w * pr) || canvas.height !== Math.round(h * pr)) {
      renderer.setSize(w, h, false);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    return true;
  }

  var geplant = false;
  function zeichne() {
    geplant = false;
    if (!bereit || !groesse()) return;
    var w = canvas.clientWidth, h = canvas.clientHeight;
    renderer.setScissorTest(false);
    renderer.clear();
    if (modus === 'teilen') {
      var x = Math.round(w * anteil);
      renderer.setScissorTest(true);
      renderer.setScissor(0, 0, x, h);
      renderer.setViewport(0, 0, w, h);
      renderer.render(szA, camera);
      renderer.setScissor(x, 0, w - x, h);
      renderer.render(szB, camera);
      renderer.setScissorTest(false);
    } else {
      renderer.render(modus === 'vorher' ? szA : (modus === 'aenderung' ? szD : szB), camera);
    }
  }
  function neuZeichnen() {
    if (!geplant) { geplant = true; requestAnimationFrame(zeichne); }
  }
  controls.addEventListener('change', neuZeichnen);
  window.addEventListener('resize', neuZeichnen);
  if (window.ResizeObserver) new ResizeObserver(neuZeichnen).observe(canvas);

  /* Ansichten: Ziel [Ost, Nord, Höhe] in lokalen Metern, yaw = Kompasskurs der Blickrichtung (0 = Nord, 90 = Ost),
     elev = Höhenwinkel der Kamera über dem Ziel, dist = Abstand in m */
  var ANSICHTEN = {
    platz: { ziel: [-75, 10, 45], yaw: 270, elev: 14, dist: 380 },
    sued: { ziel: [-90, 10, 45], yaw: 0, elev: 18, dist: 410 },
    nord: { ziel: [-90, 10, 45], yaw: 180, elev: 18, dist: 410 },
    west: { ziel: [-90, 10, 45], yaw: 90, elev: 18, dist: 410 },
    oben: { ziel: [-90, 10, 0], yaw: 270, elev: 80, dist: 560 },
    uniriese: { ziel: [-65, -60, 68], yaw: 270, elev: 8, dist: 340 }
  };
  function ansicht(name) {
    var a = ANSICHTEN[name], y = a.yaw * Math.PI / 180, e = a.elev * Math.PI / 180;
    var t = new THREE.Vector3(a.ziel[0], a.ziel[2], -a.ziel[1]);      // three.js: x Ost, y hoch, z = -Nord
    groesse();
    var dist = a.dist * (camera.aspect < 1.4 ? 1.4 / camera.aspect : 1);   // Hochformat (Handy): weiter weg
    controls.target.copy(t);
    camera.position.set(t.x - Math.sin(y) * Math.cos(e) * dist, t.y + Math.sin(e) * dist,
                        t.z + Math.cos(y) * Math.cos(e) * dist);
    camera.lookAt(t);
    controls.update();
    neuZeichnen();
  }

  /* Bedienelemente */
  var regler = root.querySelector('input[type=range]');
  var trenner = root.querySelector('.trenner');
  var tags = root.querySelectorAll('.tag');
  var legende = root.querySelector('.legende');
  function zeigeModus() {
    var teilen = modus === 'teilen';
    trenner.hidden = !teilen;
    regler.disabled = !teilen;
    regler.closest('label').classList.toggle('aus', !teilen);
    tags[0].textContent = teilen ? 'vorher' : (modus === 'vorher' ? 'vorher' : (modus === 'nachher' ? 'nachher' : 'Änderung'));
    tags[0].className = 'tag l ' + (modus === 'nachher' ? 'neu' : (modus === 'aenderung' ? 'heiss' : 'alt'));
    tags[1].hidden = !teilen;
    legende.hidden = modus !== 'aenderung';
    root.querySelectorAll('[data-modus]').forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-modus') === modus ? 'true' : 'false');
    });
    setzeTrenner();
    neuZeichnen();
  }
  function setzeTrenner() {
    trenner.style.left = (anteil * 100) + '%';
  }
  root.querySelectorAll('[data-modus]').forEach(function (b) {
    b.addEventListener('click', function () { modus = b.getAttribute('data-modus'); zeigeModus(); });
  });
  root.querySelectorAll('[data-ansicht]').forEach(function (b) {
    b.addEventListener('click', function () { ansicht(b.getAttribute('data-ansicht')); });
  });
  regler.addEventListener('input', function () {
    anteil = regler.value / 100; setzeTrenner(); neuZeichnen();
  });
  // Trenner mit dem Zeiger ziehen (ohne die Orbit-Steuerung zu stören)
  (function () {
    var griff = trenner.querySelector('.griff'), zieht = false;
    function pos(e) {
      var r = canvas.getBoundingClientRect();
      anteil = Math.min(0.98, Math.max(0.02, (e.clientX - r.left) / r.width));
      regler.value = Math.round(anteil * 100);
      setzeTrenner(); neuZeichnen();
    }
    griff.addEventListener('pointerdown', function (e) { zieht = true; griff.setPointerCapture(e.pointerId); e.preventDefault(); });
    griff.addEventListener('pointermove', function (e) { if (zieht) pos(e); });
    griff.addEventListener('pointerup', function () { zieht = false; });
    griff.addEventListener('pointercancel', function () { zieht = false; });
  })();

  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(function () { bodenfarbe(); neuZeichnen(); });
  }
  new MutationObserver(function () { bodenfarbe(); neuZeichnen(); })
    .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  Promise.all([lies(daten.vorher), lies(daten.nachher)]).then(function (r) {
    var a = r[0], b = r[1];
    function tab(pal) { return pal.map(linear); }
    var posA = new THREE.BufferAttribute(positionen(a), 3);
    var posB = new THREE.BufferAttribute(positionen(b), 3);
    szA.add(netz(posA, farbpuffer(a, a.c, tab(a.pal))));
    szB.add(netz(posB, farbpuffer(b, b.c, tab(b.pal))));
    szD.add(netz(posB, farbpuffer(b, b.d, tab(HEISS))));
    bodenfarbe();
    bereit = true;
    root.classList.add('bereit');
    ansicht('platz');
    zeigeModus();
  }).catch(function (e) {
    fehler('Die Modelldaten konnten nicht gelesen werden: ' + e);
  });
})();
