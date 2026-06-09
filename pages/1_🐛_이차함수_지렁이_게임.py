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
            targetBox.classList.remove("event");
            targetVar.innerText = normalStages[stage];
        }
        drawMathGraph();
    }

    function drawMathGraph() {
        const w = graphCanvas.width; const h = graphCanvas.height;
        const limit = 10; const scale = w / (limit * 2); 
        
        graphCtx.clearRect(0, 0, w, h);
        graphCtx.lineWidth = 1;
        for(let i = -limit; i <= limit; i++) {
            graphCtx.strokeStyle = (i % 5 === 0) ? "#adb5bd" : "#f1f3f5"; 
            let px = w/2 + i*scale; let py = h/2 - i*scale;
            graphCtx.beginPath(); graphCtx.moveTo(px, 0); graphCtx.lineTo(px, h); graphCtx.stroke();
            graphCtx.beginPath(); graphCtx.moveTo(0, py); graphCtx.lineTo(w, py); graphCtx.stroke();
        }
        graphCtx.strokeStyle = "#495057"; graphCtx.lineWidth = 2;
        graphCtx.beginPath(); graphCtx.moveTo(0, h/2); graphCtx.lineTo(w, h/2);
        graphCtx.moveTo(w/2, 0); graphCtx.lineTo(w/2, h); graphCtx.stroke();

        graphCtx.fillStyle = "#212529"; graphCtx.font = "bold 12px Arial";
        graphCtx.textAlign = "center"; graphCtx.textBaseline = "middle";
        for(let i = -limit; i <= limit; i+=5) { 
             if(i===0) continue;
             graphCtx.fillText(i, w/2 + i*scale, h/2 + 15);
             graphCtx.fillText(i, w/2 - 15, h/2 - i*scale);
        }
        graphCtx.fillText("0", w/2 - 10, h/2 + 15);
        
        graphCtx.strokeStyle = isEventMode ? "#7209b7" : "#e63946"; 
        graphCtx.lineWidth = 4; graphCtx.beginPath();
        for(let px = 0; px <= w; px += 2) {
            let mathX = (px - w/2) / scale;
            let mathY = currentA * Math.pow(mathX - currentP, 2) + currentQ;
            let py = h/2 - mathY * scale;
            if(px === 0) graphCtx.moveTo(px, py); else graphCtx.lineTo(px, py);
        }
        graphCtx.stroke();
    }

    function spawnFoods() {
        foods = [];
        let correctVal, vals = [];

        if (isEventMode) {
            correctVal = (stage === 0) ? genA : (stage === 1) ? genB : genC;
            let wrong1, wrong2;
            do { wrong1 = correctVal + Math.floor(Math.random()*10) - 5; } while(wrong1 === correctVal);
            do { wrong2 = correctVal + Math.floor(Math.random()*10) - 5; } while(wrong2 === correctVal || wrong2 === wrong1);
            vals = [{v: correctVal, c: true}, {v: wrong1, c: false}, {v: wrong2, c: false}];
        } else {
            if (stage === 0) { 
                vals = [{v: "+", c: currentA > 0}, {v: "-", c: currentA < 0}];
            } else { 
                correctVal = (stage === 1) ? currentP : currentQ;
                let w1, w2;
                const range = 6;
                do { w1 = Math.floor(Math.random()*(range*2+1))-range; } while(w1===correctVal);
                do { w2 = Math.floor(Math.random()*(range*2+1))-range; } while(w2===correctVal || w2===w1);
                vals = [{v: correctVal, c: true}, {v: w1, c: false}, {v: w2, c: false}];
            }
        }
        
        vals.forEach(item => {
            let fx, fy, occupied;
            do {
                occupied = false;
                fx = Math.floor(Math.random() * (tileCount - 2)) + 1;
                fy = Math.floor(Math.random() * (tileCount - 2)) + 1;
                for(let s of snake) if(s.x === fx && s.y === fy) occupied = true;
                for(let f of foods) if(f.x === fx && f.y === fy) occupied = true;
            } while(occupied);
            foods.push({x: fx, y: fy, val: item.v, isCorrect: item.c});
        });
    }

    function updateGame() {
        if(isGameOver) return;
        dx = nextDx; dy = nextDy;
        let head = {x: snake[0].x + dx, y: snake[0].y + dy};
        
        if(head.x<0||head.x>=tileCount||head.y<0||head.y>=tileCount) { endGame("벽에 부딪혔습니다! 💥"); return; }
        for(let i=0; i<snake.length; i++) { if(head.x===snake[i].x && head.y===snake[i].y) { endGame("자기 꼬리를 물었습니다! 😵"); return; } }
        
        snake.unshift(head); 
        
        let ateIdx = foods.findIndex(f => f.x === head.x && f.y === head.y);
        if(ateIdx !== -1) {
            if(foods[ateIdx].isCorrect) {
                if(isEventMode) {
                    snake.unshift({...head}); snake.unshift({...head});
                    score += 3;
                } else {
                    score += 1;
                }
                document.getElementById("score").innerText = score;
                
                calculateSpeed();
                if(!isBoosting) startGameLoop(); 

                stage++;
                if(stage > 2) { 
                    problemsSolved++;
                    nextProblem(); 
                } else { 
                    updateUI(); spawnFoods(); 
                }
            } else {
                endGame(`오답! [ ${foods[ateIdx].val} ] 을(를) 먹었습니다. 😭`); return;
            }
        } else {
            snake.pop(); 
        }
        drawGame();
    }

    function drawGame() {
        ctx.fillStyle = "#1a1a2e"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        foods.forEach(f => {
            ctx.fillStyle = isEventMode ? "#ffd60a" : "#ffb703"; 
            ctx.beginPath(); ctx.arc(f.x*gridSize+gridSize/2, f.y*gridSize+gridSize/2, gridSize/2-2, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#023047"; 
            ctx.font = (f.val==="+"||f.val==="-") ? "bold 26px Arial" : "bold 16px Arial";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(f.val, f.x*gridSize+gridSize/2, f.y*gridSize+gridSize/2);
        });
        for(let i=0; i<snake.length; i++) {
            let s = snake[i];
            if(i === 0) { 
                ctx.fillStyle = isEventMode ? "#9b5de5" : "#06d6a0"; 
                ctx.fillRect(s.x*gridSize, s.y*gridSize, gridSize-1, gridSize-1);
                ctx.fillStyle = "white"; ctx.fillRect(s.x*gridSize+4, s.y*gridSize+4, 5, 5); ctx.fillRect(s.x*gridSize+15, s.y*gridSize+4, 5, 5);
            } else { 
                let baseColor = isEventMode ? {r:155, g:93, b:229} : {r:6, g:214, b:160};
                let darken = i*2;
                ctx.fillStyle = `rgb(${Math.max(0,baseColor.r-darken)}, ${Math.max(0,baseColor.g-darken)}, ${Math.max(0,baseColor.b-darken)})`;
                ctx.fillRect(s.x*gridSize+1, s.y*gridSize+1, gridSize-3, gridSize-3);
            }
        }
    }

    function resetGame() {
        snake = [ {x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12} ];
        score = 3; document.getElementById("score").innerText = score;
        dx = 0; dy = -1; nextDx = 0; nextDy = -1;
        isBoosting = false; problemsSolved = 0; isEventMode = false;
        document.getElementById("warningOverlay").style.display = "none";
        document.getElementById("overlay").style.display = "none";
        
        calculateSpeed(); 
        nextProblem();
        isGameOver = false;
        document.getElementById("overlay").style.display = "none"; // 강제 해제
        startGameLoop();
    }

    function endGame(msg) {
        isGameOver = true; clearInterval(gameLoop);
        document.getElementById("overTitle").innerText = "게임 오버! 💀";
        document.getElementById("overDesc").innerHTML = `${msg}<br>최종 길이: <b>${score}</b> 🐛<br>(길수록 빨라집니다!)`;
        document.getElementById("overlay").style.display = "flex";
        isBoosting = false; document.getElementById("btnBoost").classList.remove("active");
    }

    function changeDir(newDx, newDy) {
        if (dx !== 0 && newDy !== 0) { nextDx = 0; nextDy = newDy; }
        if (dy !== 0 && newDx !== 0) { nextDx = newDx; nextDy = 0; }
        if (dx === 0 && dy === 0) { nextDx = newDx; nextDy = newDy; }
    }
    const bindBtn = (id, ndx, ndy) => document.getElementById(id).addEventListener("pointerdown", (e)=>{e.preventDefault();changeDir(ndx, ndy);});
    bindBtn("btnUp", 0, -1); bindBtn("btnDown", 0, 1); bindBtn("btnLeft", -1, 0); bindBtn("btnRight", 1, 0);

    const btnBoost = document.getElementById("btnBoost");
    const toggleBoost = (on) => {
        if(isGameOver || document.getElementById("warningOverlay").style.display === "flex") return; // 이벤트 멈춤 중에는 부스트 불가
        isBoosting = on;
        if(on) btnBoost.classList.add("active"); else btnBoost.classList.remove("active");
        startGameLoop();
    };
    btnBoost.addEventListener("pointerdown", (e)=>{e.preventDefault(); toggleBoost(true);});
    ["pointerup", "pointerleave", "pointercancel"].forEach(evt => btnBoost.addEventListener(evt, (e)=>{e.preventDefault(); toggleBoost(false);}));
    document.getElementById("startBtn").addEventListener("pointerdown", (e)=>{e.preventDefault(); resetGame();});

    document.getElementById("overlay").style.display = "flex"; // 시작 전 대기화면
    drawMathGraph();
</script>
</body>
</html>
"""

# 전체 높이를 660으로 줄여 아이패드에서 스크롤 없이 하단 버튼까지 완벽히 보이도록 최적화
components.html(game_html, height=660)
