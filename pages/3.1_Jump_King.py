
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="삼각비 점프킹", layout="wide", initial_sidebar_state="collapsed")

# Streamlit 기본 여백 최소화
st.markdown("""
<style>
.block-container {padding: 0.5rem 0.5rem 0 0.5rem; max-width: 100%;}
header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

GAME_HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>삼각비 점프킹</title>
<style>
  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; user-select: none; -webkit-user-select: none; }
  html, body { margin:0; padding:0; height:100%; background:#1a1a2e; font-family: -apple-system, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; color:#fff; overflow:hidden;}
  #wrap { display:flex; width:100vw; height:100vh; gap:8px; padding:8px;}
  #left { flex: 1 1 auto; background:#0d1b2a; border-radius:10px; overflow:hidden; position:relative; min-width:0;}
  #game { width:100%; height:100%; display:block; touch-action: none;}
  #right { flex: 0 0 360px; display:flex; flex-direction:column; gap:8px;}
  #problem {
    background:#fff; color:#222; border-radius:10px; padding:14px;
    flex: 0 0 auto;
  }
  #problem h3 { margin:0 0 8px 0; font-size:15px; color:#2a4a8a;}
  #problem .q { font-size:18px; line-height:1.4; font-weight:600;}
  #problem .hint { margin-top:6px; font-size:12px; color:#666;}
  #controls { flex:1 1 auto; background:#16213e; border-radius:10px; padding:10px; display:flex; flex-direction:column; gap:10px;}
  .arrow-row { display:flex; gap:10px; justify-content:center;}
  .btn {
    background:#2a4a8a; color:#fff; border:none; border-radius:10px; font-size:20px; font-weight:700;
    padding:18px 10px; min-height:60px; cursor:pointer; touch-action: none;
    transition: transform 0.05s, background 0.1s;
  }
  .btn:active, .btn.pressed { background:#4a6aba; transform: scale(0.96);}
  .arrow { flex: 1 1 0; font-size:28px;}
  .answer-row { display:flex; flex-direction:column; gap:8px;}
  .ans { background:#3a7a3a; font-size:18px; padding:16px 8px;}
  .ans:active, .ans.pressed { background:#5a9a5a;}
  #status { font-size:12px; color:#aaa; text-align:center; padding:4px;}
  #gauge-wrap { height:14px; background:#222; border-radius:7px; overflow:hidden; border:1px solid #444;}
  #gauge { height:100%; width:0%; background: linear-gradient(90deg, #ffeb3b, #ff5722); transition: width 0.05s;}
  #win-overlay {
    position:absolute; inset:0; background:rgba(0,0,0,0.7); display:none;
    align-items:center; justify-content:center; flex-direction:column; color:#fff; z-index:10;
    border-radius:10px;
  }
  #win-overlay.show { display:flex;}
  #win-overlay h1 { margin:0 0 10px 0; font-size:36px; color:#ffd700;}
  #win-overlay button { margin-top:14px; padding:12px 24px; border:none; border-radius:8px; background:#ffd700; color:#222; font-weight:700; font-size:16px; cursor:pointer;}
  @media (max-width: 900px) {
    #wrap { flex-direction: column;}
    #right { flex: 0 0 auto; height: 42vh;}
    #left { height: 56vh;}
  }
</style>
</head>
<body>
<div id="wrap">
  <div id="left">
    <canvas id="game"></canvas>
    <div id="win-overlay">
      <h1>🎉 정상 정복! 🎉</h1>
      <div>초코파이를 획득했습니다!</div>
      <button id="restartBtn">다시 도전</button>
    </div>
  </div>
  <div id="right">
    <div id="problem">
      <h3>오늘의 문제</h3>
      <div class="q" id="q-text">문제 로딩 중...</div>
      <div class="hint">정답 버튼은 누른 시간만큼 점프 게이지가 차오릅니다 (최대 1초). 오답은 즉시 최대 점프!</div>
    </div>
    <div id="controls">
      <div class="arrow-row">
        <button class="btn arrow" data-key="left">◀</button>
        <button class="btn arrow" data-key="right">▶</button>
      </div>
      <div id="gauge-wrap"><div id="gauge"></div></div>
      <div class="answer-row">
        <button class="btn ans" data-idx="0">A</button>
        <button class="btn ans" data-idx="1">B</button>
        <button class="btn ans" data-idx="2">C</button>
      </div>
      <div id="status">캐릭터가 멈춰 있을 때만 조작 가능</div>
    </div>
  </div>
</div>

<script>
"use strict";

// ================= 캔버스/세계 설정 =================
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const WORLD_W = 640;
const WORLD_H = 3600;   // 위로 갈수록 y 작아짐. 0이 정상, WORLD_H-1이 바닥
let viewScale = 1;
let viewW = 640, viewH = 800;

function resize() {
  const rect = canvas.parentElement.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = rect.height + 'px';
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  viewW = rect.width;
  viewH = rect.height;
  viewScale = viewW / WORLD_W;  // 가로 기준으로 스케일
}
window.addEventListener('resize', resize);

// ================= 맵 데이터 =================
// 직사각형 플랫폼: {x, y, w, h, type:'solid'|'slope_l'|'slope_r'|'steep_l'|'steep_r'|'pit'}
// slope_l: 왼쪽이 높은 경사 (오른쪽으로 미끄러짐). slope_r: 오른쪽이 높음(왼쪽으로 미끄러짐)
// steep_*: 가파른 경사 (멈출 수 없음)
// pit: 닿으면 시작점으로 (태초마을 구멍)
const platforms = [
  // 양옆 벽
  {x:0, y:0, w:20, h:WORLD_H, type:'solid'},
  {x:WORLD_W-20, y:0, w:20, h:WORLD_H, type:'solid'},

  // 바닥 (태초마을)
  {x:20, y:WORLD_H-40, w:WORLD_W-40, h:40, type:'solid'},

  // ===== 1구간 (시작) =====
  {x:80,  y:WORLD_H-160, w:120, h:18, type:'solid'},
  {x:280, y:WORLD_H-220, w:120, h:18, type:'solid'},
  {x:460, y:WORLD_H-300, w:120, h:18, type:'solid'},
  {x:120, y:WORLD_H-380, w:140, h:18, type:'solid'},

  // 경사면 (살짝 미끄러움)
  {x:320, y:WORLD_H-460, w:160, h:60, type:'slope_r'},

  {x:60,  y:WORLD_H-560, w:140, h:18, type:'solid'},

  // 함정 (태초마을로) - 좁은 구멍 옆 발판
  {x:220, y:WORLD_H-640, w:60,  h:18, type:'solid'},
  {x:300, y:WORLD_H-640, w:80,  h:18, type:'pit'},   // 함정 발판
  {x:400, y:WORLD_H-640, w:60,  h:18, type:'solid'},

  // ===== 2구간 (바람 시작 부근) =====
  {x:480, y:WORLD_H-740, w:140, h:18, type:'solid'},
  {x:250, y:WORLD_H-820, w:120, h:18, type:'solid'},
  {x:60,  y:WORLD_H-900, w:140, h:18, type:'solid'},

  // 가파른 경사 (못 멈춤)
  {x:240, y:WORLD_H-980, w:160, h:80, type:'steep_l'},

  {x:440, y:WORLD_H-1080, w:140, h:18, type:'solid'},
  {x:200, y:WORLD_H-1180, w:120, h:18, type:'solid'},
  {x:60,  y:WORLD_H-1260, w:120, h:18, type:'solid'},

  // 천장 (머리 박는 곳)
  {x:200, y:WORLD_H-1380, w:240, h:18, type:'solid'},
  {x:60,  y:WORLD_H-1460, w:120, h:18, type:'solid'},
  {x:460, y:WORLD_H-1460, w:160, h:18, type:'solid'},

  // ===== 3구간 (가운데 함정 - 큰 태초마을 행) =====
  {x:140, y:WORLD_H-1560, w:80,  h:18, type:'solid'},
  {x:260, y:WORLD_H-1560, w:120, h:18, type:'pit'},
  {x:420, y:WORLD_H-1560, w:80,  h:18, type:'solid'},

  {x:60,  y:WORLD_H-1660, w:120, h:18, type:'solid'},
  {x:280, y:WORLD_H-1720, w:140, h:18, type:'solid'},
  {x:500, y:WORLD_H-1800, w:120, h:18, type:'solid'},

  // 경사
  {x:140, y:WORLD_H-1880, w:180, h:50, type:'slope_l'},

  {x:380, y:WORLD_H-1980, w:140, h:18, type:'solid'},
  {x:160, y:WORLD_H-2080, w:140, h:18, type:'solid'},

  // 가파른 경사
  {x:320, y:WORLD_H-2180, w:200, h:100, type:'steep_r'},

  {x:60,  y:WORLD_H-2280, w:140, h:18, type:'solid'},
  {x:260, y:WORLD_H-2380, w:140, h:18, type:'solid'},
  {x:460, y:WORLD_H-2460, w:140, h:18, type:'solid'},

  // ===== 4구간 (바람 강한 구역) =====
  {x:140, y:WORLD_H-2560, w:140, h:18, type:'solid'},
  {x:360, y:WORLD_H-2640, w:140, h:18, type:'solid'},
  {x:200, y:WORLD_H-2720, w:120, h:18, type:'solid'},
  {x:440, y:WORLD_H-2800, w:140, h:18, type:'solid'},

  // 천장
  {x:60,  y:WORLD_H-2900, w:200, h:18, type:'solid'},

  // ===== 5구간 (꼭대기) =====
  {x:280, y:WORLD_H-2960, w:160, h:18, type:'solid'},
  {x:480, y:WORLD_H-3040, w:120, h:18, type:'solid'},
  {x:200, y:WORLD_H-3120, w:140, h:18, type:'solid'},
  {x:60,  y:WORLD_H-3200, w:140, h:18, type:'solid'},
  {x:260, y:WORLD_H-3280, w:120, h:18, type:'solid'},

  // 정상 발판
  {x:200, y:WORLD_H-3400, w:240, h:24, type:'solid'},
];

// 바람 구역: {y_top, y_bottom, fx (+가 오른쪽으로 미는 가속도)}
const windZones = [
  {y1: WORLD_H-1100, y2: WORLD_H-740,  fx: +0.12, label:"→ 바람"},
  {y1: WORLD_H-2900, y2: WORLD_H-2500, fx: -0.16, label:"← 강풍"},
];

// 초코파이 (목표)
const goal = { x: WORLD_W/2, y: WORLD_H - 3430, r: 16 };

// ================= 플레이어 =================
const player = {
  x: WORLD_W/2, y: WORLD_H - 60,
  w: 26, h: 38,
  vx: 0, vy: 0,
  onGround: false,
  facing: 1,
  charging: false,
  chargeStart: 0,
  pressedDir: 0,
  controllable: true,
  bobTime: 0,
};

const START_POS = {x: WORLD_W/2, y: WORLD_H - 60};

// ================= 물리 상수 =================
const GRAVITY = 0.42;
const MAX_CHARGE_MS = 1000;
const MIN_JUMP_VY = 8;
const MAX_JUMP_VY = 17.5;
const JUMP_VX = 6.2;         // 좌우 방향 점프 시 가로 속도
const FRICTION_AIR = 1.0;    // 공중 마찰 거의 없음
const SLOPE_SLIDE_VX = 1.3;
const STEEP_SLIDE_VX = 4.0;
const WALL_BOUNCE = 0.62;    // 벽 반사 계수

// ================= 문제 (삼각비) =================
const problems = [
  {q:"sin 30°의 값은?", a:"1/2", choices:["1/2","√2/2","√3/2"]},
  {q:"cos 60°의 값은?", a:"1/2", choices:["1/2","√3/2","√2/2"]},
  {q:"tan 45°의 값은?", a:"1", choices:["1","√3","√3/3"]},
  {q:"sin 45°의 값은?", a:"√2/2", choices:["1/2","√2/2","√3/2"]},
  {q:"cos 30°의 값은?", a:"√3/2", choices:["1/2","√3/2","√2/2"]},
  {q:"tan 30°의 값은?", a:"√3/3", choices:["√3","1","√3/3"]},
  {q:"tan 60°의 값은?", a:"√3", choices:["√3","√3/3","1"]},
  {q:"sin 60°의 값은?", a:"√3/2", choices:["√2/2","√3/2","1/2"]},
  {q:"cos 45°의 값은?", a:"√2/2", choices:["√3/2","√2/2","1/2"]},
  {q:"직각삼각형에서 sin θ = (대변)/(?)", a:"빗변", choices:["밑변","빗변","높이"]},
  {q:"cos θ = (밑변)/(?)", a:"빗변", choices:["대변","높이","빗변"]},
  {q:"tan θ = (대변)/(?)", a:"밑변", choices:["밑변","빗변","높이"]},
  {q:"sin²θ + cos²θ = ?", a:"1", choices:["0","1","tanθ"]},
  {q:"sin 90°의 값은?", a:"1", choices:["0","1","1/2"]},
  {q:"cos 0°의 값은?", a:"1", choices:["0","1","√2/2"]},
];

let currentProblem = null;
let correctIdx = 0;

function pickProblem() {
  currentProblem = problems[Math.floor(Math.random()*problems.length)];
  // 보기 섞기
  const c = currentProblem.choices.slice();
  for (let i=c.length-1; i>0; i--) {
    const j = Math.floor(Math.random()*(i+1));
    [c[i],c[j]] = [c[j],c[i]];
  }
  correctIdx = c.indexOf(currentProblem.a);
  document.getElementById('q-text').textContent = currentProblem.q;
  const btns = document.querySelectorAll('.ans');
  btns.forEach((b,i)=>{ b.textContent = c[i]; });
}

// ================= 입력 처리 =================
let keys = {left:false, right:false};
const ansBtns = document.querySelectorAll('.ans');
const arrowBtns = document.querySelectorAll('.arrow');

function setStatus(msg) {
  document.getElementById('status').textContent = msg;
}

function startCharge(isCorrect) {
  if (!player.controllable || !player.onGround) return;
  if (!isCorrect) {
    // 오답 → 즉시 최대 점프
    doJump(MAX_JUMP_VY);
    pickProblem();
    return;
  }
  player.charging = true;
  player.chargeStart = performance.now();
  setStatus("게이지 충전 중... (떼면 점프)");
}

function endCharge(isCorrect) {
  if (!isCorrect) return;        // 오답은 이미 처리됨
  if (!player.charging) return;
  const dt = Math.min(performance.now() - player.chargeStart, MAX_CHARGE_MS);
  const ratio = dt / MAX_CHARGE_MS;
  const vy = MIN_JUMP_VY + (MAX_JUMP_VY - MIN_JUMP_VY) * ratio;
  doJump(vy);
  player.charging = false;
  document.getElementById('gauge').style.width = '0%';
  pickProblem();
}

function doJump(vy) {
  player.vy = -vy;
  let dir = 0;
  if (keys.left && !keys.right) dir = -1;
  else if (keys.right && !keys.left) dir = 1;
  player.vx = dir * JUMP_VX;
  if (dir !== 0) player.facing = dir;
  player.onGround = false;
  player.controllable = false;
  setStatus("점프 중! 착지까지 조작 불가");
}

// 정답/오답 버튼: 누르고 있는 동안 게이지 충전, 떼면 점프
ansBtns.forEach((b, idx) => {
  const onDown = (e) => {
    e.preventDefault();
    b.classList.add('pressed');
    if (idx === correctIdx) startCharge(true);
    else startCharge(false);
  };
  const onUp = (e) => {
    e.preventDefault();
    b.classList.remove('pressed');
    if (idx === correctIdx) endCharge(true);
  };
  b.addEventListener('pointerdown', onDown);
  b.addEventListener('pointerup', onUp);
  b.addEventListener('pointercancel', onUp);
  b.addEventListener('pointerleave', onUp);
});

// 화살표: 누르고 있을 동안 방향 보존
arrowBtns.forEach(b => {
  const key = b.dataset.key;
  const onDown = (e) => { e.preventDefault(); b.classList.add('pressed'); keys[key] = true; if(player.controllable){ player.facing = (key==='left')?-1:1; } };
  const onUp   = (e) => { e.preventDefault(); b.classList.remove('pressed'); keys[key] = false; };
  b.addEventListener('pointerdown', onDown);
  b.addEventListener('pointerup', onUp);
  b.addEventListener('pointercancel', onUp);
  b.addEventListener('pointerleave', onUp);
});

// 키보드 (디버그용 / PC 테스트)
window.addEventListener('keydown', (e)=>{
  if (e.key === 'ArrowLeft') keys.left = true;
  if (e.key === 'ArrowRight') keys.right = true;
  if (e.key === '1') { ansBtns[0].dispatchEvent(new PointerEvent('pointerdown')); }
  if (e.key === '2') { ansBtns[1].dispatchEvent(new PointerEvent('pointerdown')); }
  if (e.key === '3') { ansBtns[2].dispatchEvent(new PointerEvent('pointerdown')); }
});
window.addEventListener('keyup', (e)=>{
  if (e.key === 'ArrowLeft') keys.left = false;
  if (e.key === 'ArrowRight') keys.right = false;
  if (e.key === '1') { ansBtns[0].dispatchEvent(new PointerEvent('pointerup')); }
  if (e.key === '2') { ansBtns[1].dispatchEvent(new PointerEvent('pointerup')); }
  if (e.key === '3') { ansBtns[2].dispatchEvent(new PointerEvent('pointerup')); }
});

// ================= 충돌/물리 =================
function aabb(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function getWind(y) {
  for (const z of windZones) {
    if (y >= z.y1 && y <= z.y2) return z.fx;
  }
  return 0;
}

// 경사면 위에 서 있는지 판정 + 미끄럼 적용
function applySlope(plat) {
  if (plat.type === 'slope_l') { // 왼쪽이 높음 → 오른쪽으로 미끄러짐
    player.vx += 0.15;
    if (player.vx > SLOPE_SLIDE_VX) player.vx = SLOPE_SLIDE_VX;
  } else if (plat.type === 'slope_r') {
    player.vx -= 0.15;
    if (player.vx < -SLOPE_SLIDE_VX) player.vx = -SLOPE_SLIDE_VX;
  } else if (plat.type === 'steep_l') {
    player.vx += 0.35;
    if (player.vx > STEEP_SLIDE_VX) player.vx = STEEP_SLIDE_VX;
    player.controllable = false;  // 못 멈춤
  } else if (plat.type === 'steep_r') {
    player.vx -= 0.35;
    if (player.vx < -STEEP_SLIDE_VX) player.vx = -STEEP_SLIDE_VX;
    player.controllable = false;
  }
}

function respawn() {
  player.x = START_POS.x;
  player.y = START_POS.y;
  player.vx = 0;
  player.vy = 0;
  player.onGround = true;
  player.controllable = true;
  setStatus("태초마을로 돌아왔습니다!");
}

let won = false;
const particles = [];

function spawnFireworks() {
  for (let i=0; i<80; i++) {
    const ang = Math.random()*Math.PI*2;
    const sp = 2 + Math.random()*5;
    particles.push({
      x: goal.x, y: goal.y,
      vx: Math.cos(ang)*sp, vy: Math.sin(ang)*sp,
      life: 60 + Math.random()*40,
      color: `hsl(${Math.floor(Math.random()*360)}, 90%, 60%)`,
    });
  }
}

function step() {
  if (won) {
    // 폭죽만 업데이트
    for (const p of particles) {
      p.x += p.vx; p.y += p.vy;
      p.vy += 0.08;
      p.life--;
    }
    for (let i=particles.length-1; i>=0; i--) if (particles[i].life<=0) particles.splice(i,1);
    // 가끔 더 터트림
    if (Math.random() < 0.05) spawnFireworks();
    return;
  }

  // 중력
  player.vy += GRAVITY;

  // 바람 (공중에서만 영향)
  if (!player.onGround) {
    const w = getWind(player.y);
    player.vx += w;
  }

  // 게이지 표시
  if (player.charging) {
    const dt = Math.min(performance.now() - player.chargeStart, MAX_CHARGE_MS);
    document.getElementById('gauge').style.width = (dt/MAX_CHARGE_MS*100) + '%';
  }

  // X축 이동 + 충돌
  player.x += player.vx;
  for (const p of platforms) {
    if (aabb(player, p)) {
      if (p.type === 'pit') { respawn(); return; }
      // 벽 반사
      if (player.vx > 0) {
        player.x = p.x - player.w;
        if (!player.onGround) player.vx = -player.vx * WALL_BOUNCE;
        else player.vx = 0;
      } else if (player.vx < 0) {
        player.x = p.x + p.w;
        if (!player.onGround) player.vx = -player.vx * WALL_BOUNCE;
        else player.vx = 0;
      }
    }
  }

  // Y축 이동 + 충돌
  player.y += player.vy;
  player.onGround = false;
  for (const p of platforms) {
    if (aabb(player, p)) {
      if (p.type === 'pit') { respawn(); return; }
      if (player.vy > 0) {
        // 위에서 내려옴 → 착지
        player.y = p.y - player.h;
        player.vy = 0;
        player.onGround = true;
        player.controllable = true;
        player.vx *= 0.6;  // 착지 마찰
        if (Math.abs(player.vx) < 0.05) player.vx = 0;
        applySlope(p);
        setStatus("정답 버튼을 누르고 있으면 게이지가 차오릅니다.");
      } else if (player.vy < 0) {
        // 아래에서 위로 → 머리 박음. 수직 낙하
        player.y = p.y + p.h;
        player.vy = 0;
        player.vx = 0;   // 수직으로 떨어지게
        setStatus("머리를 부딪혔다! 수직으로 낙하 중");
      }
    }
  }

  // 지상이지만 경사 위에 있으면 계속 미끄러짐
  if (player.onGround) {
    // 발 밑의 플랫폼 다시 검사
    const probe = {x: player.x, y: player.y + 1, w: player.w, h: player.h};
    for (const p of platforms) {
      if (aabb(probe, p)) {
        if (p.type !== 'solid') applySlope(p);
        break;
      }
    }
  }

  // 골 닿음
  const dx = (player.x + player.w/2) - goal.x;
  const dy = (player.y + player.h/2) - goal.y;
  if (dx*dx + dy*dy < (goal.r + 18)*(goal.r + 18)) {
    won = true;
    spawnFireworks();
    document.getElementById('win-overlay').classList.add('show');
  }

  player.bobTime += 0.1;
}

// ================= 렌더링 =================
function worldToScreen(x, y) {
  // 카메라: 플레이어 중심
  const camY = player.y - viewH/(2*viewScale) + 100;
  const sx = x * viewScale;
  const sy = (y - camY) * viewScale;
  return [sx, sy];
}

function drawPlatform(p) {
  const [sx, sy] = worldToScreen(p.x, p.y);
  const sw = p.w * viewScale;
  const sh = p.h * viewScale;
  if (sy + sh < 0 || sy > viewH) return;

  ctx.save();
  if (p.type === 'pit') {
    // 함정 - 빨간 점선 표시
    ctx.fillStyle = '#5a1a1a';
    ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = '#aa3333';
    for (let i=0; i<sw; i+=10) ctx.fillRect(sx+i, sy, 5, sh);
    ctx.fillStyle = '#fff';
    ctx.font = `${10*viewScale}px sans-serif`;
    ctx.fillText("함정", sx + sw/2 - 15*viewScale, sy + sh/2 + 4*viewScale);
  } else if (p.type === 'slope_l' || p.type === 'slope_r') {
    ctx.fillStyle = '#6a8a4a';
    ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = '#8aaa6a';
    ctx.fillRect(sx, sy, sw, 4*viewScale);
    // 방향 표시
    ctx.fillStyle = '#fff';
    ctx.font = `bold ${14*viewScale}px sans-serif`;
    ctx.fillText(p.type==='slope_l'?'↘ 미끄럼':'↙ 미끄럼', sx+8, sy + sh/2);
  } else if (p.type === 'steep_l' || p.type === 'steep_r') {
    ctx.fillStyle = '#a23a3a';
    ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = '#d25a5a';
    ctx.fillRect(sx, sy, sw, 4*viewScale);
    ctx.fillStyle = '#fff';
    ctx.font = `bold ${14*viewScale}px sans-serif`;
    ctx.fillText(p.type==='steep_l'?'⇘ 가파름!':'⇙ 가파름!', sx+8, sy + sh/2);
  } else {
    // 일반 솔리드
    ctx.fillStyle = '#3a5a8a';
    ctx.fillRect(sx, sy, sw, sh);
    ctx.fillStyle = '#5a7aaa';
    ctx.fillRect(sx, sy, sw, 4*viewScale);
  }
  ctx.restore();
}

function drawWind() {
  for (const z of windZones) {
    const [sx1, sy1] = worldToScreen(20, z.y1);
    const [sx2, sy2] = worldToScreen(WORLD_W-20, z.y2);
    if (sy2 < 0 || sy1 > viewH) continue;
    ctx.save();
    ctx.fillStyle = z.fx > 0 ? 'rgba(120,180,255,0.10)' : 'rgba(255,180,120,0.10)';
    ctx.fillRect(sx1, sy1, sx2-sx1, sy2-sy1);
    // 바람 화살표 애니메이션
    const t = performance.now()/200;
    ctx.fillStyle = z.fx > 0 ? 'rgba(120,180,255,0.35)' : 'rgba(255,180,120,0.35)';
    for (let yy = sy1+20; yy < sy2; yy += 50) {
      for (let i=0; i<5; i++) {
        const off = ((t*30 + i*100) % (sx2-sx1));
        const ax = z.fx>0 ? sx1+off : sx2-off;
        ctx.fillText(z.fx>0?'→':'←', ax, yy);
      }
    }
    ctx.font = `bold ${14*viewScale}px sans-serif`;
    ctx.fillStyle = '#fff';
    ctx.fillText(z.label, sx1+10, sy1+18);
    ctx.restore();
  }
}

function drawGoal() {
  const [sx, sy] = worldToScreen(goal.x, goal.y);
  if (sy < -50 || sy > viewH+50) return;
  const t = performance.now()/300;
  const glow = 1 + Math.sin(t)*0.3;
  ctx.save();
  // 반짝임
  ctx.globalAlpha = 0.4;
  ctx.fillStyle = '#ffeb3b';
  ctx.beginPath();
  ctx.arc(sx, sy, 40 * viewScale * glow, 0, Math.PI*2);
  ctx.fill();
  ctx.globalAlpha = 0.7;
  ctx.fillStyle = '#ffd700';
  ctx.beginPath();
  ctx.arc(sx, sy, 26 * viewScale, 0, Math.PI*2);
  ctx.fill();
  ctx.globalAlpha = 1;
  // 초코파이 본체
  const r = 18 * viewScale;
  ctx.fillStyle = '#5a2a1a';
  ctx.beginPath();
  ctx.arc(sx, sy, r, 0, Math.PI*2);
  ctx.fill();
  ctx.fillStyle = '#7a3a2a';
  ctx.beginPath();
  ctx.arc(sx, sy, r*0.85, 0, Math.PI*2);
  ctx.fill();
  // 마시멜로 줄
  ctx.fillStyle = '#fff8e8';
  ctx.fillRect(sx - r*0.8, sy - r*0.15, r*1.6, r*0.3);
  // 텍스트
  ctx.fillStyle = '#fff';
  ctx.font = `bold ${10*viewScale}px sans-serif`;
  ctx.textAlign = 'center';
  ctx.fillText('초코파이', sx, sy + 4);
  ctx.textAlign = 'start';
  ctx.restore();
}

function drawParticles() {
  for (const p of particles) {
    const [sx, sy] = worldToScreen(p.x, p.y);
    ctx.save();
    ctx.globalAlpha = Math.max(0, p.life/100);
    ctx.fillStyle = p.color;
    ctx.beginPath();
    ctx.arc(sx, sy, 3*viewScale, 0, Math.PI*2);
    ctx.fill();
    ctx.restore();
  }
}

// 귀여운 중학생 SD 캐릭터 그리기
function drawPlayer() {
  const [sx, sy] = worldToScreen(player.x + player.w/2, player.y + player.h);
  const s = viewScale;
  const face = player.facing;
  const bob = player.onGround ? Math.sin(player.bobTime)*0.8 : 0;
  ctx.save();
  ctx.translate(sx, sy + bob*s);
  ctx.scale(face*s, s);

  // 그림자
  ctx.fillStyle = 'rgba(0,0,0,0.3)';
  ctx.beginPath();
  ctx.ellipse(0, 2, 14, 4, 0, 0, Math.PI*2);
  ctx.fill();

  // 다리 (회색 바지)
  ctx.fillStyle = '#2a2a3a';
  ctx.fillRect(-8, -14, 6, 14);
  ctx.fillRect( 2, -14, 6, 14);
  // 신발
  ctx.fillStyle = '#111';
  ctx.fillRect(-10, -3, 9, 4);
  ctx.fillRect( 1, -3, 9, 4);

  // 몸통 (남색 블레이저)
  ctx.fillStyle = '#1a2a5a';
  ctx.fillRect(-12, -32, 24, 20);
  // 블레이저 라펠
  ctx.fillStyle = '#0a1a3a';
  ctx.beginPath();
  ctx.moveTo(-12, -32); ctx.lineTo(-3, -22); ctx.lineTo(-12, -16); ctx.fill();
  ctx.beginPath();
  ctx.moveTo( 12, -32); ctx.lineTo( 3, -22); ctx.lineTo( 12, -16); ctx.fill();
  // 흰 셔츠
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.moveTo(-3, -32); ctx.lineTo(3, -32); ctx.lineTo(2, -20); ctx.lineTo(-2, -20); ctx.closePath(); ctx.fill();
  // 빨간 넥타이
  ctx.fillStyle = '#c0392b';
  ctx.beginPath();
  ctx.moveTo(-2, -28); ctx.lineTo(2, -28); ctx.lineTo(3, -19); ctx.lineTo(0, -16); ctx.lineTo(-3, -19); ctx.closePath();
  ctx.fill();
  // 단추
  ctx.fillStyle = '#ffd700';
  ctx.fillRect(-1, -24, 2, 2);
  ctx.fillRect(-1, -18, 2, 2);

  // 팔
  ctx.fillStyle = '#1a2a5a';
  let armAng = 0;
  if (!player.onGround) armAng = player.vy < 0 ? -0.6 : 0.4;
  ctx.save(); ctx.translate(-12, -30); ctx.rotate(armAng);
  ctx.fillRect(-3, 0, 5, 16); ctx.restore();
  ctx.save(); ctx.translate(12, -30); ctx.rotate(-armAng);
  ctx.fillRect(-2, 0, 5, 16); ctx.restore();
  // 손
  ctx.fillStyle = '#ffe0bd';
  ctx.beginPath(); ctx.arc(-12 + Math.sin(armAng)*16, -30 + Math.cos(armAng)*16, 2.5, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc( 12 - Math.sin(armAng)*16, -30 + Math.cos(armAng)*16, 2.5, 0, Math.PI*2); ctx.fill();

  // 머리 (얼굴)
  ctx.fillStyle = '#ffe0bd';
  ctx.beginPath();
  ctx.arc(0, -42, 12, 0, Math.PI*2);
  ctx.fill();
  // 머리카락 (검정)
  ctx.fillStyle = '#1a1a1a';
  ctx.beginPath();
  ctx.arc(0, -45, 13, Math.PI, Math.PI*2);
  ctx.fill();
  // 앞머리
  ctx.beginPath();
  ctx.moveTo(-12, -45);
  ctx.quadraticCurveTo(-6, -38, 0, -42);
  ctx.quadraticCurveTo(6, -38, 12, -45);
  ctx.lineTo(12, -50); ctx.lineTo(-12, -50); ctx.closePath();
  ctx.fill();

  // 볼터치
  ctx.fillStyle = 'rgba(255,150,150,0.5)';
  ctx.beginPath(); ctx.arc(-6, -38, 2.5, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc( 6, -38, 2.5, 0, Math.PI*2); ctx.fill();

  // 눈
  ctx.fillStyle = '#000';
  ctx.beginPath(); ctx.arc(-4, -42, 1.8, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc( 4, -42, 1.8, 0, Math.PI*2); ctx.fill();
  // 눈 하이라이트
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(-3.4, -42.6, 0.6, 0, Math.PI*2); ctx.fill();
  ctx.beginPath(); ctx.arc( 4.6, -42.6, 0.6, 0, Math.PI*2); ctx.fill();

  // 입
  ctx.strokeStyle = '#7a3a2a';
  ctx.lineWidth = 1;
  ctx.beginPath();
  if (player.charging) { ctx.arc(0, -37, 1.6, 0, Math.PI*2); }   // 동그란 입 (집중)
  else { ctx.arc(0, -37, 2, 0.1*Math.PI, 0.9*Math.PI); }          // 웃는 입
  ctx.stroke();

  // 이름표
  ctx.fillStyle = '#fff';
  ctx.fillRect(4, -28, 6, 4);
  ctx.fillStyle = '#222';
  ctx.font = 'bold 3px sans-serif';
  ctx.fillText('★', 5, -25);

  ctx.restore();
}

function drawBackground() {
  // 배경 그라데이션은 div로 처리하고, 캔버스에 별 그리기
  const camY = player.y - viewH/(2*viewScale) + 100;
  ctx.fillStyle = '#0d1b2a';
  ctx.fillRect(0,0,viewW,viewH);
  // 별 (위로 올라갈수록 많아짐)
  const heightRatio = 1 - (camY / WORLD_H);
  const starCount = Math.floor(40 + heightRatio*80);
  for (let i=0; i<starCount; i++) {
    const x = ((i*97) % viewW);
    const y = ((i*131 + Math.floor(camY*0.3)) % viewH);
    ctx.fillStyle = `rgba(255,255,255,${0.2 + (i%5)*0.15})`;
    ctx.fillRect(x, y, 2, 2);
  }
  // 높이 표시
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = 'bold 14px sans-serif';
  const height = Math.max(0, Math.floor((WORLD_H - 60 - player.y)/10));
  ctx.fillText(`높이 ${height} m`, 10, 24);
}

function render() {
  drawBackground();
  drawWind();
  for (const p of platforms) drawPlatform(p);
  drawGoal();
  drawPlayer();
  drawParticles();
}

// ================= 메인 루프 =================
function loop() {
  step();
  render();
  requestAnimationFrame(loop);
}

document.getElementById('restartBtn').addEventListener('click', ()=>{
  won = false;
  particles.length = 0;
  document.getElementById('win-overlay').classList.remove('show');
  respawn();
  pickProblem();
});

// 초기화
resize();
pickProblem();
respawn();
loop();
</script>
</body>
</html>
"""

components.html(GAME_HTML, height=820, scrolling=False)
