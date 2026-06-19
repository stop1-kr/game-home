import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="삼각비 점프킹", page_icon="📐")
st.markdown("""
<style>
.block-container {padding-top: 0.5rem; padding-bottom: 0; max-width: 100%;}
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<style>
* {box-sizing: border-box; user-select: none; -webkit-user-select: none; -webkit-tap-highlight-color: transparent;}
body {margin: 0; padding: 0; font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif; background: #f3f4f6;}
.wrap {display: flex; gap: 12px; padding: 10px; height: 100vh; max-height: 760px;}
.game-col {flex: 0 0 auto;}
.side-col {flex: 1; display: flex; flex-direction: column; gap: 10px; min-width: 320px;}
canvas {display: block; border: 3px solid #4A3526; border-radius: 10px; touch-action: none; background: #B8E0F5;}
.problem-box {background: #fff; border: 2px solid #C9A96B; border-radius: 10px; padding: 12px; flex: 1; display: flex; flex-direction: column; gap: 8px; overflow: hidden;}
.problem-label {font-size: 11px; color: #888; letter-spacing: 2px; font-weight: bold;}
.fig-area {display: flex; justify-content: center; align-items: center; min-height: 130px;}
.problem-text {font-size: 16px; font-weight: 600; color: #222; line-height: 1.45; text-align: center;}
.jumps-area {display: flex; gap: 8px; justify-content: center; padding-top: 4px; border-top: 1px dashed #ddd;}
.jump-dot {width: 22px; height: 22px; border-radius: 50%; border: 2px solid #4A3526; background: #fff;}
.jump-dot.filled {background: #ff6b35;}
.jumps-label {font-size: 11px; color: #555; text-align: center; margin-bottom: -2px;}
.control-box {background: #fff; border: 2px solid #4A3526; border-radius: 10px; padding: 12px;}
.arrow-row {display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px;}
.arrow-btn {height: 56px; font-size: 26px; border: 2px solid #4A3526; background: #fffbe6; border-radius: 8px; cursor: pointer; font-weight: bold; color: #4A3526; touch-action: none;}
.arrow-btn:disabled {opacity: 0.35; cursor: not-allowed;}
.arrow-btn.charging {background: #d63031; color: #fff; border-color: #8b0000;}
.ans-row {display: flex; flex-direction: column; gap: 6px;}
.ans-btn {min-height: 42px; padding: 8px 14px; font-size: 16px; border: 2px solid #2d5a3d; background: #e8f5e9; border-radius: 8px; cursor: pointer; font-weight: 600; color: #1b3a26; text-align: left;}
.ans-btn:disabled {opacity: 0.5; cursor: not-allowed;}
.ans-btn.wrong {background: #ff6b6b !important; color: #fff !important; border-color: #8b0000 !important;}
.ans-btn.right {background: #2d5a3d !important; color: #fff !important;}
.gauge-wrap {height: 12px; background: #eee; border-radius: 6px; margin-top: 8px; overflow: hidden; border: 1px solid #ccc;}
.gauge-fill {height: 100%; width: 0%; background: linear-gradient(90deg,#74b9ff,#d63031);}
.hint {font-size: 11px; color: #777; margin-top: 6px; line-height: 1.4;}
.mode-tag {display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #4A3526; color: #fff; margin-left: 6px;}
@media (max-width: 880px) {
  .wrap {flex-direction: column; max-height: none; height: auto;}
  .game-col {align-self: center;}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="game-col">
    <canvas id="game" width="460" height="720"></canvas>
  </div>
  <div class="side-col">
    <div class="problem-box">
      <div class="problem-label">PROBLEM <span class="mode-tag" id="modeTag">SOLVE</span></div>
      <div class="fig-area" id="pfig"></div>
      <div class="problem-text" id="ptext">문제 로딩...</div>
      <div class="jumps-label">남은 점프 기회</div>
      <div class="jumps-area" id="jumpsArea"></div>
    </div>
    <div class="control-box">
      <div class="arrow-row">
        <button class="arrow-btn" id="leftBtn">◀</button>
        <button class="arrow-btn" id="upBtn">▲</button>
        <button class="arrow-btn" id="rightBtn">▶</button>
      </div>
      <div class="ans-row">
        <button class="ans-btn" data-idx="0">A</button>
        <button class="ans-btn" data-idx="1">B</button>
        <button class="ans-btn" data-idx="2">C</button>
      </div>
      <div class="gauge-wrap"><div class="gauge-fill" id="gauge"></div></div>
      <div class="hint">① 문제를 풀고 정답 클릭 → 점프 기회 5회 획득. ② 방향 화살표(◀▲▶)를 꾹 누르면 게이지가 차오르고, 떼면 그 방향으로 점프합니다.</div>
    </div>
  </div>
</div>
<script>
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const W = canvas.width, H = canvas.height;
const WORLD_H = 3600, WORLD_W = W;

const GRAVITY = 0.55, MAX_JUMP_VY = 16.5, MAX_JUMP_VX = 7;
const WALL_BOUNCE = 0.62;
const FRICTION_GROUND = 0.55;          // 일반 타일 마찰 강화 (값이 작을수록 빨리 멈춤)
const STOP_THRESHOLD = 0.25;           // 미끄럼 정지 임계
const SLIDE_NORMAL = 0.08, SLIDE_STEEP = 0.22;
const CHARGE_MAX_MS = 1000;
const JUMPS_PER_PROBLEM = 5;

const SPAWN = {x: 50, y: WORLD_H - 80};
const player = {
  x: SPAWN.x, y: SPAWN.y, w: 22, h: 32,
  vx: 0, vy: 0, onGround: false, groundType: 'flat',
  slopeDir: 0, facing: 1
};

let camY = 0;
function updateCamera() {
  const target = player.y - H * 0.72;
  camY = Math.max(0, Math.min(WORLD_H - H, target));
}

const platforms = [
  {x:0, y:WORLD_H-40, w:WORLD_W, h:40, type:'flat'},
  {x:170, y:WORLD_H-130, w:110, h:18, type:'flat'},
  {x:330, y:WORLD_H-210, w:110, h:18, type:'flat'},
  {x:40, y:WORLD_H-260, w:90, h:18, type:'flat'},
  {x:180, y:WORLD_H-340, w:90, h:18, type:'flat'},
  {x:320, y:WORLD_H-410, w:120, h:18, type:'slope', dir:1},
  {x:30, y:WORLD_H-470, w:130, h:18, type:'slope', dir:-1},
  {x:220, y:WORLD_H-530, w:60, h:14, type:'trap'},
  {x:60, y:WORLD_H-610, w:100, h:18, type:'flat'},
  {x:280, y:WORLD_H-700, w:120, h:18, type:'flat'},
  {x:40, y:WORLD_H-800, w:90, h:18, type:'flat'},
  {x:220, y:WORLD_H-880, w:100, h:18, type:'flat'},
  {x:350, y:WORLD_H-970, w:90, h:18, type:'flat'},
  {x:60, y:WORLD_H-1060, w:140, h:18, type:'steep', dir:1},
  {x:260, y:WORLD_H-1160, w:140, h:18, type:'steep', dir:-1},
  {x:40, y:WORLD_H-1260, w:90, h:18, type:'flat'},
  {x:220, y:WORLD_H-1340, w:90, h:18, type:'flat'},
  {x:350, y:WORLD_H-1430, w:90, h:18, type:'flat'},
  {x:160, y:WORLD_H-1510, w:60, h:14, type:'trap'},
  {x:40, y:WORLD_H-1600, w:80, h:18, type:'flat'},
  {x:340, y:WORLD_H-1600, w:80, h:18, type:'flat'},
  {x:60, y:WORLD_H-1700, w:90, h:18, type:'flat'},
  {x:260, y:WORLD_H-1790, w:120, h:18, type:'flat'},
  {x:60, y:WORLD_H-1890, w:90, h:18, type:'flat'},
  {x:240, y:WORLD_H-1980, w:90, h:18, type:'flat'},
  {x:360, y:WORLD_H-2080, w:80, h:18, type:'flat'},
  {x:40, y:WORLD_H-2180, w:100, h:18, type:'flat'},
  {x:220, y:WORLD_H-2280, w:100, h:18, type:'flat'},
  {x:350, y:WORLD_H-2380, w:90, h:18, type:'flat'},
  {x:140, y:WORLD_H-2480, w:130, h:18, type:'flat'},
  {x:40, y:WORLD_H-2580, w:90, h:18, type:'slope', dir:-1},
  {x:280, y:WORLD_H-2680, w:130, h:18, type:'flat'},
  {x:150, y:WORLD_H-2800, w:160, h:20, type:'flat'},
];
const walls = [
  {x:0, y:0, w:6, h:WORLD_H},
  {x:WORLD_W-6, y:0, w:6, h:WORLD_H},
];
const windZones = [
  {x:6, y:WORLD_H-1100, w:WORLD_W-12, h:200, dir:1, strength:0.28},
  {x:6, y:WORLD_H-2200, w:WORLD_W-12, h:250, dir:-1, strength:0.26},
];

const choco = {x: 230, y: WORLD_H-2830, r: 14, collected: false};
const GOAL_HEIGHT_M = Math.round((WORLD_H - 80 - choco.y) / 10);
let particles = [];

// ---------- 게임 상태 ----------
// mode: 'solve' (문제 풀이) | 'jump' (점프 5회)
let mode = 'solve';
let jumpsLeft = 0;
let currentProblem = null;

// 충전(꾹누름) 상태
let chargingDir = 0;        // -1, 0(위), 1
let chargingActive = false;
let chargeStart = 0;
let chargingBtnEl = null;

// ---------- 문제 생성 ----------
function gcd(a,b){return b===0?a:gcd(b,a%b);}
function frac(n,d){const g=gcd(Math.abs(n),Math.abs(d));n/=g;d/=g;return d===1?(''+n):(n+'/'+d);}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}}

const rightTris = [
  {a:3,b:4,c:5}, {a:5,b:12,c:13}, {a:8,b:15,c:17},
  {a:6,b:8,c:10}, {a:9,b:12,c:15}, {a:7,b:24,c:25},
];

function genProblem() {
  const t = Math.floor(Math.random()*4);
  if (t === 0) {
    // 유형1: 세 변 → 삼각비 값
    const tri = rightTris[Math.floor(Math.random()*rightTris.length)];
    const angle = Math.random()<0.5 ? 'A' : 'B';
    const ratio = ['sin','cos','tan'][Math.floor(Math.random()*3)];
    const opp = angle==='A' ? tri.a : tri.b;
    const adj = angle==='A' ? tri.b : tri.a;
    let num, den;
    if (ratio==='sin') {num=opp; den=tri.c;}
    else if (ratio==='cos') {num=adj; den=tri.c;}
    else {num=opp; den=adj;}
    const ans = frac(num, den);
    const pool = [frac(opp,tri.c),frac(adj,tri.c),frac(opp,adj),frac(adj,opp),frac(tri.c,opp),frac(tri.c,adj)];
    const wrongs = [...new Set(pool)].filter(v=>v!==ans);
    shuffle(wrongs);
    const opts = [ans, wrongs[0], wrongs[1]];
    shuffle(opts);
    return {text:`다음 직각삼각형에서 ${ratio} ${angle}의 값은?`, fig:realTriSVG(tri,angle), options:opts, answer:ans};
  } else if (t === 1) {
    // 유형2: 특수각 삼각비 값
    const data = [
      ['sin 30°','1/2'],['sin 45°','√2/2'],['sin 60°','√3/2'],
      ['cos 30°','√3/2'],['cos 45°','√2/2'],['cos 60°','1/2'],
      ['tan 30°','√3/3'],['tan 45°','1'],['tan 60°','√3'],
    ];
    const p = data[Math.floor(Math.random()*data.length)];
    const ans = p[1];
    const pool = ['1/2','√2/2','√3/2','√3/3','1','√3','2','√2'];
    const wrongs = pool.filter(v=>v!==ans);
    shuffle(wrongs);
    const opts = [ans, wrongs[0], wrongs[1]];
    shuffle(opts);
    return {text:`${p[0]} 의 값은?`, fig:'', options:opts, answer:ans};
  } else if (t === 2) {
    // 유형3: 특수각 + 한 변 → 나머지 변
    const setups = [
      {ang:30, given:'빗변', gv:10, find:'높이', ans:'5'},
      {ang:30, given:'빗변', gv:8, find:'밑변', ans:'4√3'},
      {ang:60, given:'빗변', gv:8, find:'밑변', ans:'4'},
      {ang:60, given:'빗변', gv:6, find:'높이', ans:'3√3'},
      {ang:45, given:'빗변', gv:6, find:'밑변', ans:'3√2'},
      {ang:45, given:'빗변', gv:8, find:'높이', ans:'4√2'},
      {ang:30, given:'밑변', gv:6, find:'높이', ans:'2√3'},
      {ang:60, given:'밑변', gv:4, find:'높이', ans:'4√3'},
      {ang:45, given:'밑변', gv:5, find:'높이', ans:'5'},
      {ang:30, given:'높이', gv:3, find:'빗변', ans:'6'},
      {ang:60, given:'높이', gv:6, find:'밑변', ans:'2√3'},
      {ang:45, given:'높이', gv:4, find:'빗변', ans:'4√2'},
    ];
    const s = setups[Math.floor(Math.random()*setups.length)];
    const ans = s.ans;
    const pool = ['3','4','5','6','8','10','2√2','3√2','4√2','5√2','2√3','3√3','4√3','5√3','6√3'];
    const wrongs = pool.filter(v=>v!==ans);
    shuffle(wrongs);
    const opts = [ans, wrongs[0], wrongs[1]];
    shuffle(opts);
    return {text:`그림과 같은 직각삼각형에서 ${s.find}의 길이는?`, fig:specialAngleSVG(s), options:opts, answer:ans};
  } else {
    // 유형4: 피타고라스
    const tri = rightTris[Math.floor(Math.random()*rightTris.length)];
    const hide = Math.floor(Math.random()*3);
    let text, ans;
    if (hide===2) {text=`두 변의 길이가 ${tri.a}, ${tri.b}인 직각삼각형의 빗변의 길이는?`; ans=''+tri.c;}
    else if (hide===1) {text=`빗변이 ${tri.c}, 한 변이 ${tri.a}인 직각삼각형의 나머지 한 변의 길이는?`; ans=''+tri.b;}
    else {text=`빗변이 ${tri.c}, 한 변이 ${tri.b}인 직각삼각형의 나머지 한 변의 길이는?`; ans=''+tri.a;}
    const pool = ['3','4','5','6','7','8','9','10','12','13','15','17','20','24','25'];
    const wrongs = pool.filter(v=>v!==ans);
    shuffle(wrongs);
    const opts = [ans, wrongs[0], wrongs[1]];
    shuffle(opts);
    return {text:text, fig:'', options:opts, answer:ans};
  }
}

// 세 변 비율 그대로 그리는 직각삼각형
function realTriSVG(tri, angle) {
  // 직각: 오른쪽 아래. A각: 왼쪽 아래. B각: 오른쪽 위.
  // b(가로, 밑변) = tri.b, a(세로, 높이) = tri.a
  const maxDim = 130;
  const scale = maxDim / Math.max(tri.a, tri.b);
  const bw = tri.b * scale;
  const bh = tri.a * scale;
  const padding = 28;
  const svgW = bw + padding*2 + 20;
  const svgH = bh + padding*2;
  const x1 = padding, y1 = padding + bh;       // A (왼쪽 아래)
  const x2 = padding + bw, y2 = padding + bh;  // 직각 (오른쪽 아래)
  const x3 = padding + bw, y3 = padding;       // B (오른쪽 위)
  return `<svg width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
    <polygon points="${x1},${y1} ${x2},${y2} ${x3},${y3}" fill="#fff8e1" stroke="#4A3526" stroke-width="2"/>
    <rect x="${x2-12}" y="${y2-12}" width="12" height="12" fill="none" stroke="#4A3526" stroke-width="1.5"/>
    <text x="${(x1+x2)/2}" y="${y1+16}" text-anchor="middle" font-size="13" fill="#222">${tri.b}</text>
    <text x="${x2+6}" y="${(y2+y3)/2+4}" font-size="13" fill="#222">${tri.a}</text>
    <text x="${(x1+x3)/2-22}" y="${(y1+y3)/2-2}" font-size="13" fill="#222">${tri.c}</text>
    <text x="${x1+8}" y="${y1-6}" font-size="14" fill="${angle==='A'?'#d63031':'#888'}" font-weight="bold">A</text>
    <text x="${x3-14}" y="${y3+16}" font-size="14" fill="${angle==='B'?'#d63031':'#888'}" font-weight="bold">B</text>
  </svg>`;
}

// 특수각: 실제 각도대로 그리기
function specialAngleSVG(s) {
  const rad = s.ang * Math.PI / 180;
  // 직각이 오른쪽 아래, 표시 각도(s.ang)는 왼쪽 아래에 위치
  // 밑변(가로) = base, 높이(세로) = base * tan(ang)
  // 적당한 크기로: 가장 큰 변을 130으로 맞춤
  const maxDim = 130;
  let bw, bh;
  if (s.ang === 30) { bw = maxDim; bh = bw * Math.tan(rad); }
  else if (s.ang === 45) { bw = maxDim; bh = bw; }
  else { bh = maxDim; bw = bh / Math.tan(rad); }
  const padding = 34;
  const svgW = bw + padding*2 + 14;
  const svgH = bh + padding*2;
  const x1 = padding, y1 = padding + bh;
  const x2 = padding + bw, y2 = padding + bh;
  const x3 = padding + bw, y3 = padding;
  // 라벨 결정
  let lb='?', lh='?', lc='?';
  const setLabel = (which, val) => {
    if (which==='밑변') lb = val;
    else if (which==='높이') lh = val;
    else lc = val;
  };
  setLabel(s.given, ''+s.gv);
  // find는 ?
  // 호 표시 (각도 표시) - 왼쪽 아래
  const arcR = 22;
  const arcEndX = x1 + arcR * Math.cos(-rad);
  const arcEndY = y1 + arcR * Math.sin(-rad);
  return `<svg width="${svgW}" height="${svgH}" viewBox="0 0 ${svgW} ${svgH}">
    <polygon points="${x1},${y1} ${x2},${y2} ${x3},${y3}" fill="#fff8e1" stroke="#4A3526" stroke-width="2"/>
    <rect x="${x2-12}" y="${y2-12}" width="12" height="12" fill="none" stroke="#4A3526" stroke-width="1.5"/>
    <path d="M ${x1+arcR},${y1} A ${arcR},${arcR} 0 0 0 ${arcEndX},${arcEndY}" fill="none" stroke="#d63031" stroke-width="1.5"/>
    <text x="${x1+arcR+4}" y="${y1-6}" font-size="13" fill="#d63031" font-weight="bold">${s.ang}°</text>
    <text x="${(x1+x2)/2}" y="${y1+16}" text-anchor="middle" font-size="13" fill="#222">${lb}</text>
    <text x="${x2+6}" y="${(y2+y3)/2+4}" font-size="13" fill="#222">${lh}</text>
    <text x="${(x1+x3)/2-26}" y="${(y1+y3)/2-2}" font-size="13" fill="#222">${lc}</text>
  </svg>`;
}

// ---------- UI 업데이트 ----------
function renderJumps() {
  const area = document.getElementById('jumpsArea');
  let html = '';
  for (let i = 0; i < JUMPS_PER_PROBLEM; i++) {
    html += `<div class="jump-dot ${i < jumpsLeft ? 'filled' : ''}"></div>`;
  }
  area.innerHTML = html;
}

function setMode(m) {
  mode = m;
  document.getElementById('modeTag').textContent = (m === 'solve') ? 'SOLVE' : 'JUMP';
  document.querySelectorAll('.ans-btn').forEach(b => { b.disabled = (m !== 'solve'); });
  document.querySelectorAll('.arrow-btn').forEach(b => { b.disabled = (m !== 'jump'); });
}

function loadProblem() {
  currentProblem = genProblem();
  document.getElementById('ptext').textContent = currentProblem.text;
  document.getElementById('pfig').innerHTML = currentProblem.fig;
  document.querySelectorAll('.ans-btn').forEach((b,i)=>{
    b.textContent = `${'ABC'[i]}.  ${currentProblem.options[i]}`;
    b.classList.remove('wrong','right');
    b.style.background = '';
    b.style.color = '';   // ← color 도 명시적으로 초기화
  });
  setMode('solve');
}

// ---------- 답안 클릭 (단순 click) ----------
document.querySelectorAll('.ans-btn').forEach(btn => {
  const idx = parseInt(btn.dataset.idx);
  btn.addEventListener('click', () => {
    if (mode !== 'solve') return;
    const isCorrect = currentProblem.options[idx] === currentProblem.answer;
    if (isCorrect) {
      btn.classList.add('right');
      jumpsLeft = JUMPS_PER_PROBLEM;
      renderJumps();
      setTimeout(() => setMode('jump'), 350);
    } else {
      btn.classList.add('wrong');
      btn.disabled = true;
    }
  });
});

// ---------- 화살표 꾹누르기 → 점프 ----------
function startCharge(dir, el) {
  if (mode !== 'jump') return;
  if (!player.onGround) return;
  if (chargingActive) return;
  if (jumpsLeft <= 0) return;
  chargingActive = true;
  chargingDir = dir;
  chargingBtnEl = el;
  chargeStart = performance.now();
  el.classList.add('charging');
  if (dir !== 0) player.facing = dir;
}
function endCharge(el) {
  if (!chargingActive || chargingBtnEl !== el) return;
  const dt = Math.min(performance.now() - chargeStart, CHARGE_MAX_MS);
  const power = Math.max(0.25, dt / CHARGE_MAX_MS);
  doJump(chargingDir, power);
  chargingActive = false;
  chargingBtnEl.classList.remove('charging');
  chargingBtnEl = null;
  chargingDir = 0;
}
function bindHoldButton(btn, dir) {
  btn.addEventListener('pointerdown', (e) => {
    e.preventDefault();
    btn.setPointerCapture(e.pointerId);
    startCharge(dir, btn);
  });
  btn.addEventListener('pointerup', (e) => {
    e.preventDefault();
    endCharge(btn);
  });
  btn.addEventListener('pointercancel', () => endCharge(btn));
}
bindHoldButton(document.getElementById('leftBtn'), -1);
bindHoldButton(document.getElementById('upBtn'), 0);
bindHoldButton(document.getElementById('rightBtn'), 1);

function doJump(dir, power) {
  player.vy = -MAX_JUMP_VY * power;
  player.vx = dir * MAX_JUMP_VX * power;
  player.onGround = false;
  jumpsLeft--;
  renderJumps();
}

// ---------- 물리 ----------
function rectOverlap(a, b) {
  return a.x < b.x+b.w && a.x+a.w > b.x && a.y < b.y+b.h && a.y+a.h > b.y;
}

function update() {
  document.getElementById('gauge').style.width = chargingActive
    ? (Math.min(performance.now()-chargeStart, CHARGE_MAX_MS)/CHARGE_MAX_MS*100)+'%'
    : '0%';

  for (const wz of windZones) {
    if (player.x > wz.x && player.x < wz.x+wz.w && player.y > wz.y && player.y < wz.y+wz.h) {
      if (!player.onGround) player.vx += wz.dir * wz.strength;
    }
  }

  if (!player.onGround) player.vy += GRAVITY;

  if (player.onGround) {
    if (player.groundType === 'slope') {
      player.vx += player.slopeDir * SLIDE_NORMAL;
      if (Math.abs(player.vx) > 1.5) player.vx = Math.sign(player.vx)*1.5;
    } else if (player.groundType === 'steep') {
      player.vx += player.slopeDir * SLIDE_STEEP;
      if (Math.abs(player.vx) > 4) player.vx = Math.sign(player.vx)*4;
    } else {
      player.vx *= FRICTION_GROUND;
      if (Math.abs(player.vx) < STOP_THRESHOLD) player.vx = 0;
    }
  }

  player.x += player.vx;
  for (const w of walls) {
    if (rectOverlap(player, w)) {
      if (player.vx > 0) player.x = w.x - player.w;
      else if (player.vx < 0) player.x = w.x + w.w;
      player.vx = -player.vx * WALL_BOUNCE;
      if (Math.abs(player.vx) < 0.5) player.vx = 0;
    }
  }
  if (!player.onGround) {
    for (const p of platforms) {
      if (rectOverlap(player, p)) {
        const prevX = player.x - player.vx;
        const wasInsideY = (player.y + player.h > p.y + 2 && player.y < p.y + p.h - 2);
        if (wasInsideY) {
          if (player.vx > 0 && prevX + player.w <= p.x + 1) {
            player.x = p.x - player.w;
            player.vx = -player.vx * WALL_BOUNCE;
          } else if (player.vx < 0 && prevX >= p.x + p.w - 1) {
            player.x = p.x + p.w;
            player.vx = -player.vx * WALL_BOUNCE;
          }
        }
      }
    }
  }

  player.y += player.vy;
  const wasOnGround = player.onGround;
  player.onGround = false;
  for (const p of platforms) {
    if (rectOverlap(player, p)) {
      const prevY = player.y - player.vy;
      if (player.vy >= 0 && prevY + player.h <= p.y + 1) {
        player.y = p.y - player.h;
        player.vy = 0;
        player.onGround = true;
        player.groundType = p.type;
        player.slopeDir = p.dir || 0;
        if (p.type === 'trap') {respawn(); break;}
      } else if (player.vy < 0 && prevY >= p.y + p.h - 1) {
        player.y = p.y + p.h;
        player.vy = 0;
        player.vx = 0;
      }
    }
  }

  if (player.x < 6) {player.x = 6; player.vx = Math.abs(player.vx)*WALL_BOUNCE;}
  if (player.x + player.w > WORLD_W - 6) {player.x = WORLD_W - 6 - player.w; player.vx = -Math.abs(player.vx)*WALL_BOUNCE;}

  // 점프 5회 다 쓰고 완전히 멈추면 → 새 문제
  if (mode === 'jump' && jumpsLeft <= 0 && player.onGround && Math.abs(player.vx) < 0.1 && Math.abs(player.vy) < 0.1) {
    if (!choco.collected) setTimeout(loadProblem, 400);
  }

  if (!choco.collected) {
    const dx = (player.x + player.w/2) - choco.x;
    const dy = (player.y + player.h/2) - choco.y;
    if (dx*dx + dy*dy < (choco.r + 20)*(choco.r + 20)) {
      choco.collected = true;
      triggerFireworks();
    }
  }

  updateCamera();
  for (const pt of particles) {pt.x += pt.vx; pt.y += pt.vy; pt.vy += 0.12; pt.life--;}
  particles = particles.filter(p => p.life > 0);
}

function respawn() {
  player.x = SPAWN.x; player.y = SPAWN.y;
  player.vx = 0; player.vy = 0;
}

function triggerFireworks() {
  for (let burst = 0; burst < 6; burst++) {
    setTimeout(() => {
      const cx = 60 + Math.random()*(WORLD_W-120);
      const cy = choco.y + (Math.random()-0.5)*240;
      const col = ['#ff6b6b','#feca57','#48dbfb','#1dd1a1','#5f27cd','#ff9ff3','#ffd700'][Math.floor(Math.random()*7)];
      for (let i = 0; i < 32; i++) {
        const a = (i/32)*Math.PI*2;
        const sp = 2 + Math.random()*2;
        particles.push({x:cx, y:cy, vx:Math.cos(a)*sp, vy:Math.sin(a)*sp, life:70, color:col});
      }
    }, burst*350);
  }
}

// ---------- 렌더링 ----------
function drawBackground() {
  const g = ctx.createLinearGradient(0,0,0,H);
  g.addColorStop(0, '#FFD9A8');
  g.addColorStop(0.4, '#FFE5C2');
  g.addColorStop(0.7, '#C5E5F5');
  g.addColorStop(1, '#A8D8B0');
  ctx.fillStyle = g;
  ctx.fillRect(0,0,W,H);
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  for (let i = 0; i < 14; i++) {
    const seed = i*173;
    const cx = (seed % (W-60)) + 30;
    const baseY = (seed*7) % WORLD_H;
    const cy = baseY - camY*0.25;
    const yMod = ((cy % (H+200)) + (H+200)) % (H+200) - 100;
    if (yMod > -50 && yMod < H+50) {
      ctx.beginPath();
      ctx.arc(cx, yMod, 16, 0, Math.PI*2);
      ctx.arc(cx+16, yMod-4, 20, 0, Math.PI*2);
      ctx.arc(cx+32, yMod, 14, 0, Math.PI*2);
      ctx.fill();
    }
  }
}

function drawPlatform(p) {
  const y = p.y - camY;
  if (y < -40 || y > H+40) return;
  if (p.type === 'trap') {
    ctx.fillStyle = '#d63031';
    ctx.fillRect(p.x, y, p.w, p.h);
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    for (let i = 0; i < p.w; i += 8) {
      ctx.beginPath(); ctx.moveTo(p.x+i, y); ctx.lineTo(p.x+i+4, y+p.h); ctx.stroke();
    }
    ctx.strokeStyle = '#8b0000';
    ctx.strokeRect(p.x, y, p.w, p.h);
  } else if (p.type === 'slope') {
    ctx.fillStyle = '#8FBC8F';
    ctx.fillRect(p.x, y, p.w, p.h);
    ctx.strokeStyle = '#2d5a3d'; ctx.lineWidth = 2;
    ctx.strokeRect(p.x, y, p.w, p.h);
    ctx.fillStyle = '#2d5a3d'; ctx.font = 'bold 9px sans-serif';
    ctx.fillText('~ SLIDE ~', p.x+8, y+12);
  } else if (p.type === 'steep') {
    ctx.fillStyle = '#E17055';
    ctx.fillRect(p.x, y, p.w, p.h);
    ctx.strokeStyle = '#8b0000'; ctx.lineWidth = 2;
    ctx.strokeRect(p.x, y, p.w, p.h);
    ctx.fillStyle = '#fff'; ctx.font = 'bold 9px sans-serif';
    ctx.fillText('>> STEEP >>', p.x+6, y+12);
  } else {
    ctx.fillStyle = '#C9A96B';
    ctx.fillRect(p.x, y, p.w, p.h);
    ctx.fillStyle = '#A88B4F';
    ctx.fillRect(p.x, y+p.h-4, p.w, 4);
    ctx.strokeStyle = '#4A3526'; ctx.lineWidth = 2;
    ctx.strokeRect(p.x, y, p.w, p.h);
  }
}

function drawWindZone(wz) {
  const y = wz.y - camY;
  if (y < -wz.h || y > H) return;
  ctx.fillStyle = 'rgba(135, 206, 250, 0.18)';
  ctx.fillRect(wz.x, y, wz.w, wz.h);
  ctx.strokeStyle = 'rgba(70,130,180,0.7)'; ctx.lineWidth = 2;
  const t = performance.now()/250;
  for (let i = 0; i < 5; i++) {
    const ay = y + 25 + i*38;
    const offset = ((t*30 + i*40) % (wz.w+40)) - 20;
    const ax = wz.dir > 0 ? offset : wz.w - offset;
    ctx.beginPath();
    ctx.moveTo(ax, ay); ctx.lineTo(ax + wz.dir*22, ay);
    ctx.lineTo(ax + wz.dir*16, ay-5);
    ctx.moveTo(ax + wz.dir*22, ay); ctx.lineTo(ax + wz.dir*16, ay+5);
    ctx.stroke();
  }
  ctx.fillStyle = 'rgba(70,130,180,0.8)'; ctx.font = 'bold 11px sans-serif';
  ctx.fillText('WIND ZONE', wz.x+8, y+14);
}

function drawChoco() {
  if (choco.collected) return;
  const y = choco.y - camY;
  if (y < -40 || y > H+40) return;
  const t = performance.now()/200;
  const glow = 8 + Math.sin(t)*5;
  ctx.fillStyle = 'rgba(255, 215, 0, 0.35)';
  ctx.beginPath(); ctx.arc(choco.x, y, choco.r + glow, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = 'rgba(255, 215, 0, 0.5)';
  ctx.beginPath(); ctx.arc(choco.x, y, choco.r + glow*0.5, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#5a3a1a';
  ctx.beginPath(); ctx.arc(choco.x, y, choco.r, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#fff8e1';
  ctx.beginPath(); ctx.arc(choco.x, y, choco.r*0.55, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#fff';
  for (let i = 0; i < 4; i++) {
    const ang = t + i*1.57;
    const sx = choco.x + Math.cos(ang)*(choco.r+10);
    const sy = y + Math.sin(ang)*(choco.r+10);
    ctx.beginPath(); ctx.arc(sx, sy, 2.5, 0, Math.PI*2); ctx.fill();
  }
}

function drawPlayer() {
  const px = player.x, py = player.y - camY;
  const f = player.facing;
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.beginPath();
  ctx.ellipse(px+player.w/2, py+player.h+2, player.w/2, 3, 0, 0, Math.PI*2);
  ctx.fill();
  // 다리(짙은 갈색 바지)
  ctx.fillStyle = '#3A2820';
  ctx.fillRect(px+3, py+22, 6, 10);
  ctx.fillRect(px+13, py+22, 6, 10);
  ctx.fillStyle = '#1a1a1a';
  ctx.fillRect(px+2, py+30, 8, 3);
  ctx.fillRect(px+12, py+30, 8, 3);
  // 몸통(베이지 블레이저)
  ctx.fillStyle = '#C9A96B';
  ctx.fillRect(px+2, py+13, 18, 12);
  // 라펠(다크브라운)
  ctx.fillStyle = '#3A2820';
  ctx.beginPath();
  ctx.moveTo(px+2, py+13); ctx.lineTo(px+6, py+13); ctx.lineTo(px+9, py+20); ctx.lineTo(px+5, py+22); ctx.closePath(); ctx.fill();
  ctx.beginPath();
  ctx.moveTo(px+20, py+13); ctx.lineTo(px+16, py+13); ctx.lineTo(px+13, py+20); ctx.lineTo(px+17, py+22); ctx.closePath(); ctx.fill();
  // 흰 셔츠
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.moveTo(px+9, py+13); ctx.lineTo(px+13, py+13); ctx.lineTo(px+11, py+18); ctx.closePath(); ctx.fill();
  // 녹색 체크 넥타이
  ctx.fillStyle = '#2d5a3d';
  ctx.beginPath();
  ctx.moveTo(px+10, py+15); ctx.lineTo(px+12, py+15); ctx.lineTo(px+13, py+22); ctx.lineTo(px+9, py+22); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = '#a0c890'; ctx.lineWidth = 0.6;
  ctx.beginPath(); ctx.moveTo(px+9, py+17); ctx.lineTo(px+13, py+17); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(px+9, py+20); ctx.lineTo(px+13, py+20); ctx.stroke();
  // 노란 엠블럼
  ctx.fillStyle = '#f0d020';
  ctx.fillRect(px+15, py+15, 3, 4);
  // 머리(검은 머리)
  ctx.fillStyle = '#1a1a1a';
  ctx.beginPath(); ctx.arc(px+11, py+7, 8, 0, Math.PI*2); ctx.fill();
  // 얼굴
  ctx.fillStyle = '#ffe0b0';
  ctx.beginPath(); ctx.arc(px+11, py+9, 6, 0, Math.PI*2); ctx.fill();
  // 앞머리
  ctx.fillStyle = '#1a1a1a';
  ctx.beginPath(); ctx.ellipse(px+11, py+4, 8, 4.5, 0, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(px+8, py+6, 4, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(px+14, py+6, 3.5, 0, Math.PI*2); ctx.fill();
  // 눈
  ctx.fillStyle = '#000';
  ctx.beginPath(); ctx.arc(px+8+f*0.5, py+10, 1.4, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(px+14+f*0.5, py+10, 1.4, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(px+8+f*0.5, py+9.5, 0.5, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(px+14+f*0.5, py+9.5, 0.5, 0, Math.PI*2); ctx.fill();
  // 볼터치
  ctx.fillStyle = 'rgba(255,150,150,0.65)';
  ctx.beginPath(); ctx.arc(px+7, py+12, 1.6, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc(px+15, py+12, 1.6, 0, Math.PI*2); ctx.fill();
  // 입
  ctx.strokeStyle = '#5a3a1a'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.arc(px+11, py+12.5, 1.2, 0.2, Math.PI-0.2); ctx.stroke();
}

function drawParticles() {
  for (const pt of particles) {
    ctx.fillStyle = pt.color;
    ctx.globalAlpha = Math.min(1, pt.life / 50);
    ctx.beginPath();
    ctx.arc(pt.x, pt.y - camY, 3, 0, Math.PI*2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function drawHUD() {
  const h = Math.max(0, Math.round((WORLD_H - 80 - player.y) / 10));
  ctx.fillStyle = 'rgba(0,0,0,0.6)';
  ctx.fillRect(8, 8, 170, 28);
  ctx.fillStyle = '#fff';
  ctx.font = 'bold 14px sans-serif';
  ctx.fillText(`HEIGHT  ${h} m / ${GOAL_HEIGHT_M} m`, 14, 27);
}

function drawWinOverlay() {
  if (!choco.collected) return;
  ctx.fillStyle = 'rgba(0,0,0,0.45)';
  ctx.fillRect(0, H/2-60, W, 120);
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 32px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('정상 정복!', W/2, H/2 + 4);
  ctx.font = '14px sans-serif';
  ctx.fillStyle = '#fff';
  ctx.fillText('초코파이 획득 - 축하합니다!', W/2, H/2 + 30);
  ctx.textAlign = 'left';
}

function render() {
  drawBackground();
  for (const wz of windZones) drawWindZone(wz);
  for (const p of platforms) drawPlatform(p);
  drawChoco();
  drawPlayer();
  drawParticles();
  drawHUD();
  drawWinOverlay();
}

function loop() {
  update();
  render();
  requestAnimationFrame(loop);
}

renderJumps();
loadProblem();
loop();
</script>
</body>
</html>
"""

components.html(HTML, height=770, scrolling=False)
