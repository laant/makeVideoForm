/*
 * doongk — 둥근 크로스백 캐릭터 (ink-theater 플러그인)
 * 원화: mascot-template-round-crossbody.svg · 규격: CHARACTER-SPEC-round-crossbody.md
 *
 * InkTheater.mascot() 와 같은 사용법:
 *   var D = InkTheater.doongk({ x, y, scale });   // scale 2 = 원화(600×600 템플릿) 크기, (x,y) = 몸 중심
 *   svg.appendChild(D.g);  D.reachR([wx, wy]);    // 손끝 목표(화면 좌표) → 팔 2마디 IK
 * 추가 기능:
 *   D.legs([lx,ly],[rx,ry]) 발끝 목표(화면 좌표) → 다리 2마디 IK(무릎은 바깥·앞으로)
 *   D.walk(phase)  걷기 한 주기(0~1 반복) — 다리 교차 + 몸 상하(최대 8)
 *   D.look(dx)     두 점눈을 함께 dx(−4~4, 원화 단위) 이동 · D.blink() 은 아무것도 안 함(점눈 유지 규칙)
 *   D.mouth("none"|"smile"|"o")   D.armFront("L"|"R", true/false)  — 몸 앞/뒤 그리기 순서
 *   D.moveTo(x, y)  몸 중심 이동(팔·다리 목표는 화면 좌표라 그대로 따라옴)
 * 결정론: 상태는 호출 인자로만 결정됨(난수·시각 없음) — HyperFrames 시크 안전.
 */
(function (root) {
  "use strict";
  var IT = root.InkTheater, NS = "http://www.w3.org/2000/svg", INK = "#000";
  function el(tag, a, kids) { var n = document.createElementNS(NS, tag); if (a) for (var k in a) n.setAttribute(k, a[k]); (kids || []).forEach(function (c) { n.appendChild(c); }); return n; }
  function r2(v) { return Math.round(v * 100) / 100; }

  // 원화 좌표(몸 중심 0,0 · 템플릿 단위)
  var SH = { L: [-65, -2], R: [65, -2] }, ARM = [55, 50];
  var HIP = { L: [-28, 62], R: [28, 62] }, LEG = [70, 70];
  var REST = { handL: [-88, 95], handR: [88, 95], footL: [-28, 202], footR: [28, 202] };
  var SW = 4;

  function doongk(opt) {
    opt = opt || {};
    var k = (opt.scale || 2) / 2;                    // scale 2 → 원화 1:1
    var ox = opt.x || 0, oy = opt.y || 0;
    var g = el("g", { transform: "" });
    var line = function () { return el("path", { d: "", fill: "none", stroke: INK, "stroke-width": SW, "stroke-linecap": "round", "stroke-linejoin": "round" }); };
    var armL = line(), armR = line(), legL = line(), legR = line();
    var gArmL = el("g", { id: "armL" }, [armL]), gArmR = el("g", { id: "armR" }, [armR]);
    var gLegL = el("g", { id: "legL" }, [legL]), gLegR = el("g", { id: "legR" }, [legR]);
    var body = el("g", { id: "body" }, [el("path", { d: "M 0,-70 C 39,-70 70,-39 70,0 C 70,39 40,70 0,70 C -40,70 -70,40 -70,0 C -70,-39 -40,-70 0,-70 Z", fill: "#fff", stroke: INK, "stroke-width": SW, "stroke-linejoin": "round" })]);
    var strap = el("g", { id: "strap" }, [el("path", { d: "M -62.4,-32 C -41,-1 -9,30 28,41 C 33,42.5 37,43.5 41,44", fill: "none", stroke: INK, "stroke-width": 3.8, "stroke-linecap": "round" })]);
    var bag = el("g", { id: "bag", transform: "translate(46 47) rotate(-16)" }, [
      el("path", { d: "M -17,-7 C -17,-11 -14,-13 -10,-13 L 10,-13 C 14,-13 17,-11 17,-7 L 17,4 C 17,11 11,15 0,15 C -11,15 -17,11 -17,4 Z", fill: "#fff", stroke: INK, "stroke-width": SW, "stroke-linejoin": "round" }),
      el("path", { d: "M -17,-6 C -16,1 -10,4 0,4 C 10,4 16,1 17,-6", fill: "none", stroke: INK, "stroke-width": 3.8, "stroke-linecap": "round" })]);
    var eyeL = el("circle", { cx: -23, cy: -20, r: 5.5, fill: INK }), eyeR = el("circle", { cx: 23, cy: -20, r: 5.5, fill: INK });
    var gEyes = el("g", { id: "eyes" }, [el("g", { id: "eyeL" }, [eyeL]), el("g", { id: "eyeR" }, [eyeR])]);
    var mSmile = el("path", { d: "M -7,0 C -5,7 5,7 7,0", fill: "none", stroke: INK, "stroke-width": 3.5, "stroke-linecap": "round", display: "none" });
    var mO = el("ellipse", { cx: 0, cy: 3, rx: 4.5, ry: 5.5, fill: "none", stroke: INK, "stroke-width": 3.2, display: "none" });
    var gMouth = el("g", { id: "mouth" }, [mSmile, mO]);
    // 기본 순서(아래→위): 팔, 다리, 몸, 끈, 가방, 눈, 입  — 팔은 armFront 로 몸 앞으로 옮길 수 있음
    var back = el("g", null, [gArmL, gArmR]), front = el("g");
    [back, gLegL, gLegR, body, strap, bag, gEyes, gMouth, front].forEach(function (n) { g.appendChild(n); });

    function place() { g.setAttribute("transform", "translate(" + r2(ox) + "," + r2(oy) + ") scale(" + k + ")"); }
    function toLocal(p) { return [(p[0] - ox) / k, (p[1] - oy) / k]; }
    function toWorld(p) { return [ox + p[0] * k, oy + p[1] * k]; }
    // 2마디 IK — 굽힘 방향 bend(+1/−1) 고정으로 팔꿈치·무릎이 갑자기 뒤집히지 않게
    function ik2(a, t, L1, L2, bend) {
      var dx = t[0] - a[0], dy = t[1] - a[1], d = Math.hypot(dx, dy), max = L1 + L2 - 0.01;
      if (d > max) { t = [a[0] + dx / d * max, a[1] + dy / d * max]; d = max; }
      if (d < 1e-3) d = 1e-3;
      var cos = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d), ang = Math.acos(Math.max(-1, Math.min(1, cos)));
      var base = Math.atan2(t[1] - a[1], t[0] - a[0]) + bend * ang;
      return [[a[0] + Math.cos(base) * L1, a[1] + Math.sin(base) * L1], t];
    }
    function limbD(a, j, t, tip) {   // 관절 j 를 정확히 지나는 매끄러운 곡선 하나(제어점 = 2j − (a+t)/2)
      var c = [2 * j[0] - (a[0] + t[0]) / 2, 2 * j[1] - (a[1] + t[1]) / 2];
      var d = "M " + r2(a[0]) + "," + r2(a[1]) + " Q " + r2(c[0]) + "," + r2(c[1]) + " " + r2(t[0]) + "," + r2(t[1]);
      if (tip) d += " q " + tip[0] * 0.2 + "," + 4 + " " + tip[0] + "," + 2;   // 발끝 짧은 굽힘(원화의 끝 처리)
      return d;
    }
    var state = { hL: REST.handL, hR: REST.handR, fL: REST.footL, fR: REST.footR };
    function drawArm(side) {
      var s = SH[side], t = side === "L" ? state.hL : state.hR;
      var jt = ik2(s, t, ARM[0], ARM[1], side === "L" ? 1 : -1);   // 팔꿈치는 바깥·아래로
      (side === "L" ? armL : armR).setAttribute("d", limbD(s, jt[0], jt[1]));
    }
    function drawLeg(side) {
      var h = HIP[side], t = side === "L" ? state.fL : state.fR;
      var jt = ik2(h, t, LEG[0], LEG[1], side === "L" ? 1 : -1);   // 무릎은 바깥으로
      (side === "L" ? legL : legR).setAttribute("d", limbD(h, jt[0], jt[1], side === "L" ? [-11, 0] : [11, 0]));
    }
    function redraw() { drawArm("L"); drawArm("R"); drawLeg("L"); drawLeg("R"); }

    var api = {
      g: g, body: body, strap: strap, bag: bag, eyeL: eyeL, eyeR: eyeR, armL: armL, armR: armR, legL: legL, legR: legR,
      get origin() { return [ox, oy]; },
      get shoulderL() { return toWorld(SH.L); }, get shoulderR() { return toWorld(SH.R); },
      reachL: function (p) { state.hL = toLocal(p); drawArm("L"); autoFront("L"); },
      reachR: function (p) { state.hR = toLocal(p); drawArm("R"); autoFront("R"); },
      rest: function () { state.hL = REST.handL; state.hR = REST.handR; state.fL = REST.footL; state.fR = REST.footR; redraw(); api.armFront("L", false); api.armFront("R", false); },
      legs: function (pl, pr) { if (pl) state.fL = toLocal(pl); if (pr) state.fR = toLocal(pr); drawLeg("L"); drawLeg("R"); },
      walk: function (phase) {   // phase 0~1 한 주기 — 정면 걷기: 두 다리가 번갈아 바깥으로 벌어지며 들림(원화 7번 역삼각)
        var a = phase * Math.PI * 2, sL = Math.max(0, Math.sin(a)), sR = Math.max(0, -Math.sin(a));
        state.fL = [REST.footL[0] - 6 - 16 * sL, REST.footL[1] - 14 * sL];
        state.fR = [REST.footR[0] + 6 + 16 * sR, REST.footR[1] - 14 * sR];
        drawLeg("L"); drawLeg("R");
        return -Math.abs(Math.sin(a)) * 8 * k;   // 몸 상하(화면 단위) — 호출 측이 moveTo 에 더해 씀
      },
      look: function (dx) { eyeL.setAttribute("cx", -23 + dx); eyeR.setAttribute("cx", 23 + dx); },
      blink: function () { /* 점눈 유지 규칙: 눈 모양을 바꾸지 않음 */ },
      mouth: function (kind) { mSmile.setAttribute("display", kind === "smile" ? "inline" : "none"); mO.setAttribute("display", kind === "o" ? "inline" : "none"); },
      armFront: function (side, on) { var n = side === "L" ? gArmL : gArmR; (on ? front : back).appendChild(n); },
      moveTo: function (x, y) { ox = x; oy = y; place(); },
      scale: k * 2
    };
    // 손이 몸 실루엣 안(원 반지름 70)으로 들어오면 그 팔을 몸 앞으로(물건 들기·얼굴 근처 손)
    function autoFront(side) {
      var t = side === "L" ? state.hL : state.hR;
      api.armFront(side, Math.hypot(t[0], t[1]) < 66);
    }
    place(); redraw();
    return api;
  }
  if (IT) IT.doongk = doongk;
  root.Doongk = doongk;
})(window);
