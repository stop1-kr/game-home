import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(page_title="✨이차함수 지렁이 대모험✨", page_icon="🐛", layout="wide")

# 상단 여백을 극단적으로 줄여 아이패드 세로 공간 확보
st.markdown("""
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0rem;
        max-width: 1200px; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐛 ✨ 이차함수 지렁이 대모험! (도전 모드🔥) ✨")
st.markdown("""
**목표:** 그래프를 보고 식의 계수를 찾아 지렁이를 키우세요! (🚨 **경고가 뜨면 멈춰서 그래프를 분석하세요!**)
""")

# 🎮 세로 크기가 콤팩트하게 최적화된 게임 엔진 HTML/CSS/JS
game_html = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0; padding: 0;
            background-color: #f8f9fa;
            font-family: 'Pretendard', sans-serif;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
        }
        /* 컨테이너 여백 축소 */
        .container {
            position: relative;
            display: flex;
            flex-direction: row;
            gap: 20px;
            background: white;
            padding: 15px 20px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .game-panel { position: relative; display: flex; flex-direction: column; gap: 10px; }
        
        /* 캔버스 크기 축소 (450x450) */
        #gameCanvas { background-color: #1a1a2e; border-radius: 15px; border: 4px solid #4a4e69; }
        
        /* 상태창 높이/패딩 축소 */
        .status-box {
            background: #ffe3e3; padding: 10px; border-radius: 10px;
            text-align: center; font-size: 1.3rem; font-weight: bold; color: #d90429;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;
        }
        .status-box.event { background: #7209b7; color: #ffd60a; animation: pulse-fast 0.8s infinite; }
        
        .right-panel { display: flex; flex-direction: column; gap: 10px; width: 330px; }
        
        .graph-panel {
            background: white; border: 3px solid #dee2e6; border-radius: 15px;
            padding: 10px; text-align: center;
        }
        /* 그래프 캔버스 크기 축소 (300x300) */
        #graphCanvas { background-color: #ffffff; border-radius: 10px; }
        
        /* 방향키 크기 및 간격 축소 */
        .dpad-container {
            display: grid; grid-template-columns: 75px 75px 75px; grid-template-rows: 75px 75px 75px;
            gap: 6px; justify-content: center; margin-top: 5px;
        }
        .btn {
            background: #457b9d; border: none; border-radius: 15px; color: white;
            font-size: 2rem; width: 100%; height: 100%;
            box-shadow: 0 5px 0 #1d3557; cursor: pointer;
            display: flex; justify-content: center; align-items: center; touch-action: manipulation;
        }
        .btn:active { transform: translateY(5px); box-shadow: 0 0 0 transparent; background: #1d3557; }
        .btn.up { grid-column: 2; grid-row: 1; }
        .btn.left { grid-column: 1; grid-row: 2; }
        .btn.right { grid-column: 3; grid-row: 2; }
        .btn.down { grid-column: 2; grid-row: 3; }
        .btn.boost { grid-column: 2; grid-row: 2; background: #fca311; box-shadow: 0 5px 0 #d08c00; font-size: 1.6rem; }
        .btn.boost.active { background: #d90429; box-shadow: 0 5px 0 transparent; transform: translateY(5px); }
        
        /* 오버레이 캔버스 크기에 맞춤 (450x450) */
        .overlay, .warning-overlay {
            position: absolute; top: 0; left: 0; width: 450px; height: 450px;
            border-radius: 15px; display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .overlay { background: rgba(0,0,0,0.8); color: white; z-index: 20; display: none; }
        .overlay h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .start-btn {
            padding: 12px 35px; font-size: 1.5rem; font-weight: bold; border: none;
            border-radius: 40px; background: #e63946; color: white; cursor: pointer;
        }

        .warning-overlay {
            background: rgba(220, 53, 69, 0.85); color: #fff; z-index: 15; display: none;
            animation: flash 0.5s infinite alternate; text-align: center; padding: 20px; box-sizing: border-box;
        }
        .warning-overlay h1 { font-size: 2.2rem; margin: 0; text-transform: uppercase; }
        
        .watermark { position: absolute; bottom: 5px; left: 15px; font-size: 13px; color: #adb5bd; opacity: 0.5; font-weight: bold; pointer-events: none; }
        
        @keyframes pulse-fast { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }
        @keyframes flash { from { opacity: 0.8; } to { opacity: 1; } }
    </style>
</head>
<body>

<div class="container">
    <div class="watermark">stop1</div>
    <div class="game-panel">
        <canvas id="gameCanvas" width="450" height="450"></canvas>
        
        <!-- 시작/종료 오버레이 -->
        <div id="overlay" class="overlay">
            <h1 id="overTitle">🐍 지렁이 대모험</h1>
            <p id="overDesc" style="text-align:center; font-size:1.2rem;">그래프를 보고 계수를 맞춰보세요!<br>돌발 이벤트는 고득점의 기회! 🚨</p>
            <button id="startBtn" class="start-btn">게임 시작 🚀</button>
        </div>
        
        <!-- 이벤트 경고 오버레이 -->
        <div id="warningOverlay" class="warning-overlay">
            <h1>🚨 긴급 미션 발동! 🚨</h1>
            <p style="font-size:1.3rem; margin-top:10px;"><b>잠시 일시정지!</b><br>오른쪽 그래프를 분석하여<br>y = ax² + bx + c 형태를 찾으세요!</p>
        </div>

        <div class="status-box" id="targetBox">
            🔥 현재 목표: <span id="targetVar" style="font-size:1.5rem;">a (부호)</span>
        </div>
    </div>

    <div class="right-panel">
        <div class="graph-panel">
            <h3 id="graphTitle" style="margin: 5px 0; color:#343a40;">y = a(x-p)² + q</h3>
            <canvas id="graphCanvas" width="300" height="300"></canvas>
        </div>
        
        <div class="dpad-container">
            <button class="btn up" id="btnUp">🔼</button>
            <button class="btn left" id="btnLeft">◀️</button>
            <button class="btn boost" id="btnBoost">🚀</button>
            <button class="btn right" id="btnRight">▶️</button>
            <button class="btn down" id="btnDown">🔽</button>
        </div>
        
        <div style="text-align:center; font-weight:bold; color:#457b9d; font-size:1.3rem; margin-top:5px;">
            지렁이 길이: <span id="score">3</span> 🐛
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas"); const ctx = canvas.getContext("2d");
    const graphCanvas = document.getElementById("graphCanvas"); const graphCtx = graphCanvas.getContext("2d");
    const gridSize = 25; // 칸 크기 25px
    const tileCount = canvas.width / gridSize; // 450 / 25 = 18칸
    
    let snake = []; let dx = 0; let dy = 0; let nextDx = 0; let nextDy = 0;
    let score = 3; let gameLoop; let isGameOver = true;
    
    // 속도 관련
    const START_SPEED = 500; 
    const MIN_SPEED = 150;   
    const BOOST_SPEED = 100; 
    let currentBaseSpeed = START_SPEED;
    let isBoosting = false;

    // 문제 관련 변수
    let currentA, currentP, currentQ; // 표준형
    let genA, genB, genC; // 일반형
    
    let isEventMode = false;
    let stage = 0; 
    let problemsSolved = 0; 

    const normalStages = ['a (부호)', 'p (꼭짓점 x)', 'q (꼭짓점 y)'];
    const eventStages = ['a (값!)', 'b (값!)', 'c (값!)'];
    let foods = [];

    function calculateSpeed() {
        let speedDec = (score - 3) * 15; 
        currentBaseSpeed = Math.max(MIN_SPEED, START_SPEED - speedDec);
    }

    function startGameLoop() {
        if(gameLoop) clearInterval(gameLoop);
        let speed = isBoosting ? BOOST_SPEED : currentBaseSpeed;
        gameLoop = setInterval(updateGame, speed);
    }

    function nextProblem() {
        stage = 0;
        if (!isEventMode && problemsSolved >= 2 && Math.random() < 0.3) {
            triggerEvent();
        } else {
            isEventMode = false;
            generateNormalProblem();
        }
    }

    // 🚨 이벤트 발동 (수정됨: 일시정지 및 식 숨김 기능)
    function triggerEvent() {
        isEventMode = true;
        
        // 1. 게임 루프 정지 (지렁이 멈춤!)
        clearInterval(gameLoop); 
        
        const warning = document.getElementById("warningOverlay");
        warning.style.display = "flex";
        
        // 2. 문제를 즉시 생성하여 우측 그래프를 먼저 보여줌 (학생이 분석할 수 있게)
        generateEventProblem();
        
        // 3. 2.5초 후 경고창 사라지고 다시 움직임 시작
        setTimeout(() => { 
            warning.style.display = "none"; 
            startGameLoop(); 
        }, 2500); 
    }

    function generateNormalProblem() {
        const aPool = [-2, -1, 1, 2];
        currentA = aPool[Math.floor(Math.random() * aPool.length)];
        currentP = Math.floor(Math.random() * 11) - 5; 
        currentQ = Math.floor(Math.random() * 11) - 5;
        updateUI();
        spawnFoods();
    }

    function generateEventProblem() {
        const aPool = [-2, -1, 1, 2];
        currentA = aPool[Math.floor(Math.random() * aPool.length)];
        currentP = Math.floor(Math.random() * 7) - 3; 
        currentQ = Math.floor(Math.random() * 9) - 4; 
        
        genA = currentA;
        genB = -2 * currentA * currentP;
        genC = currentA * currentP * currentP + currentQ;
        
        updateUI();
        spawnFoods();
    }

    // 📝 UI 업데이트 (수정됨: 이벤트 시 y = ax² + bx + c 표기)
    function updateUI() {
        const title = document.getElementById("graphTitle");
        const targetBox = document.getElementById("targetBox");
        const targetVar = document.getElementById("targetVar");

        if (isEventMode) {
            title.innerText = "y = ax² + bx + c"; // 식에 답을 보여주지 않음!
            targetBox.classList.add("event");
            targetVar.innerText = eventStages[stage];
        } else {
            title.innerText = "y = a(x-p)² + q";
