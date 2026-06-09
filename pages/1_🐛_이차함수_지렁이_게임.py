import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(page_title="✨이차함수 지렁이 대모험✨", page_icon="🐛", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        max-width: 1200px; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐛 ✨ 이차함수 지렁이 대모험! (도전 모드🔥) ✨ 🐛")
st.markdown("""
**목표:** 그래프를 보고 식의 계수를 찾아 지렁이를 키우세요!
*   **기본 모드:** $y=a(x-p)^2+q$ 에서 **a(부호) ➔ p ➔ q** 맞추기 (보상: 꼬리 +1)
*   **🚨돌발 이벤트:** $y=ax^2+bx+c$ 에서 **a ➔ b ➔ c 숫자** 맞추기 (보상: **꼬리 +3!**)
*   **주의:** 지렁이가 길어질수록 점점 빨라집니다! ⚡
""")

# 🎮 게임 엔진 HTML/CSS/JS
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
        .container {
            position: relative;
            display: flex;
            flex-direction: row;
            gap: 30px;
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        .game-panel { position: relative; display: flex; flex-direction: column; gap: 15px; }
        #gameCanvas { background-color: #1a1a2e; border-radius: 15px; border: 4px solid #4a4e69; }
        .status-box {
            background: #ffe3e3; padding: 15px; border-radius: 10px;
            text-align: center; font-size: 1.4rem; font-weight: bold; color: #d90429;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: all 0.3s;
        }
        .status-box.event { background: #7209b7; color: #ffd60a; animation: pulse-fast 0.8s infinite; }
        
        .right-panel { display: flex; flex-direction: column; gap: 20px; width: 360px; }
        .graph-panel {
            background: white; border: 3px solid #dee2e6; border-radius: 15px;
            padding: 10px; text-align: center;
        }
        #graphCanvas { background-color: #ffffff; border-radius: 10px; }
        
        .dpad-container {
            display: grid; grid-template-columns: 80px 80px 80px; grid-template-rows: 80px 80px 80px;
            gap: 8px; justify-content: center; margin-top: 10px;
        }
        .btn {
            background: #457b9d; border: none; border-radius: 15px; color: white;
            font-size: 2.2rem; width: 100%; height: 100%;
            box-shadow: 0 6px 0 #1d3557; cursor: pointer;
            display: flex; justify-content: center; align-items: center; touch-action: manipulation;
        }
        .btn:active { transform: translateY(6px); box-shadow: 0 0 0 transparent; background: #1d3557; }
        .btn.up { grid-column: 2; grid-row: 1; }
        .btn.left { grid-column: 1; grid-row: 2; }
        .btn.right { grid-column: 3; grid-row: 2; }
        .btn.down { grid-column: 2; grid-row: 3; }
        .btn.boost { grid-column: 2; grid-row: 2; background: #fca311; box-shadow: 0 6px 0 #d08c00; font-size: 1.8rem; }
        .btn.boost.active { background: #d90429; box-shadow: 0 6px 0 transparent; transform: translateY(6px); }
        
        /* 오버레이 (시작/종료) */
        .overlay {
            position: absolute; top: 0; left: 0; width: 500px; height: 500px;
            background: rgba(0,0,0,0.8); border-radius: 15px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: white; z-index: 20;
        }
        .overlay h1 { font-size: 3rem; margin-bottom: 10px; }
        .start-btn {
            padding: 15px 40px; font-size: 1.8rem; font-weight: bold; border: none;
            border-radius: 40px; background: #e63946; color: white; cursor: pointer;
        }

        /* 🚨 이벤트 경고 오버레이 */
        .warning-overlay {
            position: absolute; top: 0; left: 0; width: 500px; height: 500px;
            background: rgba(220, 53, 69, 0.85); border-radius: 15px;
            display: none; flex-direction: column; justify-content: center; align-items: center;
            color: #fff; z-index: 15; animation: flash 0.5s infinite alternate;
        }
        .warning-overlay h1 { font-size: 2.5rem; margin: 0; text-transform: uppercase; letter-spacing: 2px; }
        
        .watermark { position: absolute; bottom: 10px; left: 20px; font-size: 13px; color: #adb5bd; opacity: 0.5; font-weight: bold; pointer-events: none; }
        
        @keyframes pulse-fast { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }
        @keyframes flash { from { opacity: 0.8; } to { opacity: 1; } }
    </style>
</head>
<body>

<div class="container">
    <div class="watermark">stop1</div>
    <div class="game-panel">
        <canvas id="gameCanvas" width="500" height="500"></canvas>
        
        <!-- 시작/종료 오버레이 -->
        <div id="overlay" class="overlay">
            <h1 id="overTitle">🐍 지렁이 대모험</h1>
            <p id="overDesc" style="text-align:center; font-size:1.3rem;">그래프를 보고 계수를 맞춰보세요!<br>돌발 이벤트는 고득점의 기회! 🚨</p>
            <button id="startBtn" class="start-btn">게임 시작 🚀</button>
        </div>
        <!-- 이벤트 경고 오버레이 -->
        <div id="warningOverlay" class="warning-overlay">
            <h1>🚨 긴급 미션 발동! 🚨</h1>
            <p style="font-size:1.5rem; margin-top:10px;">일반형(y=ax²+bx+c) 문제가 출제됩니다!</p>
        </div>

        <div class="status-box" id="targetBox">
            🔥 현재 목표: <span id="targetVar" style="font-size:1.7rem;">a (부호)</span>
        </div>
    </div>

    <div class="right-panel">
        <div class="graph-panel">
            <h3 id="graphTitle" style="margin: 5px 0; color:#343a40;">y = a(x-p)² + q</h3>
            <canvas id="graphCanvas" width="340" height="340"></canvas>
        </div>
        
        <div class="dpad-container">
            <button class="btn up" id="btnUp">🔼</button>
            <button class="btn left" id="btnLeft">◀️</button>
            <button class="btn boost" id="btnBoost">🚀</button>
            <button class="btn right" id="btnRight">▶️</button>
            <button class="btn down" id="btnDown">🔽</button>
        </div>
        
        <div style="text-align:center; font-weight:bold; color:#457b9d; font-size:1.4rem; margin-top:5px;">
            지렁이 길이: <span id="score">3</span> 🐛
        </div>
    </div>
</div>

<script>
    const canvas = document.getElementById("gameCanvas"); const ctx = canvas.getContext("2d");
    const graphCanvas = document.getElementById("graphCanvas"); const graphCtx = graphCanvas.getContext("2d");
    const gridSize = 25; const tileCount = canvas.width / gridSize;
    
    let snake = []; let dx = 0; let dy = 0; let nextDx = 0; let nextDy = 0;
    let score = 3; let gameLoop; let isGameOver = true;
    
    // 속도 관련
    const START_SPEED = 500; // 초기 속도 (느림)
    const MIN_SPEED = 150;   // 최고 속도 한계 (빠름)
    const BOOST_SPEED = 100; // 부스트 시 속도
    let currentBaseSpeed = START_SPEED;
    let isBoosting = false;

    // 문제 관련 변수
    let currentA, currentP, currentQ; // 표준형 변수
    let genA, genB, genC; // 일반형 변수
    
    let isEventMode = false; // 이벤트 모드 플래그
    let stage = 0; // 현재 단계 (0, 1, 2)
    let problemsSolved = 0; // 푼 문제 수 카운트

    const normalStages = ['a (부호)', 'p (꼭짓점 x)', 'q (꼭짓점 y)'];
    const eventStages = ['a (값!)', 'b (값!)', 'c (값!)'];
    let foods = [];

    // === 속도 계산 (길어질수록 빨라짐) ===
    function calculateSpeed() {
        // 길이 3부터 시작, 길이가 늘어날수록 속도 값(주기)이 줄어듦
        let speedDec = (score - 3) * 15; 
        currentBaseSpeed = Math.max(MIN_SPEED, START_SPEED - speedDec);
    }

    // === 게임 루프 시작/재시작 ===
    function startGameLoop() {
        if(gameLoop) clearInterval(gameLoop);
        let speed = isBoosting ? BOOST_SPEED : currentBaseSpeed;
        gameLoop = setInterval(updateGame, speed);
    }

    // === 문제 생성 루틴 ===
    function nextProblem() {
        stage = 0;
        
        // 이벤트 발동 조건 체크 (랜덤 또는 특정 문제 수 이후)
        // 예: 3문제 이상 풀었고, 25% 확률로 발동
        if (!isEventMode && problemsSolved >= 2 && Math.random() < 0.3) {
            triggerEvent();
        } else {
            isEventMode = false;
            generateNormalProblem();
        }
    }

    // 🚨 이벤트 발동!
    function triggerEvent() {
        isEventMode = true;
        // 경고창 표시
        const warning = document.getElementById("warningOverlay");
        warning.style.display = "flex";
        setTimeout(() => { warning.style.display = "none"; }, 2500); // 2.5초 후 사라짐
        
        generateEventProblem();
    }

    // 일반 문제 생성 (y = a(x-p)^2 + q)
    function generateNormalProblem() {
        const aPool = [-2, -1, 1, 2];
        currentA = aPool[Math.floor(Math.random() * aPool.length)];
        currentP = Math.floor(Math.random() * 11) - 5; // -5 ~ 5
        currentQ = Math.floor(Math.random() * 11) - 5;
        updateUI();
        spawnFoods();
    }

    // 이벤트 문제 생성 (y = ax^2 + bx + c)
    function generateEventProblem() {
        // 전개를 위해 표준형 계수 먼저 생성 (b,c가 너무 커지지 않게 범위 조절)
        const aPool = [-2, -1, 1, 2];
        currentA = aPool[Math.floor(Math.random() * aPool.length)];
        currentP = Math.floor(Math.random() * 7) - 3; // -3 ~ 3
        currentQ = Math.floor(Math.random() * 9) - 4; // -4 ~ 4
        
        // 일반형 계수 계산: a(x-p)^2+q = ax^2 - 2apx + ap^2+q
        genA = currentA;
        genB = -2 * currentA * currentP;
        genC = currentA * currentP * currentP + currentQ;
        
        updateUI();
        spawnFoods();
    }

    // UI 업데이트
    function updateUI() {
        const title = document.getElementById("graphTitle");
        const targetBox = document.getElementById("targetBox");
        const targetVar = document.getElementById("targetVar");

        if (isEventMode) {
            title.innerText = `y = ${genA}x² + ${genB}x + ${genC}`; // 식 보여주기
            targetBox.classList.add("event");
            targetVar.innerText = eventStages[stage];
        } else {
            title.innerText = "y = a(x-p)² + q";
            targetBox.classList.remove("event");
            targetVar.innerText = normalStages[stage];
        }
        drawMathGraph();
    }

    // === 그래프 그리기 (공통) ===
    function drawMathGraph() {
        const w = graphCanvas.width; const h = graphCanvas.height;
        const limit = 10; const scale = w / (limit * 2); 
        
        graphCtx.clearRect(0, 0, w, h);
        graphCtx.lineWidth = 1;
        for(let i = -limit; i <= limit; i++) {
            graphCtx.strokeStyle = (i % 5 === 0) ? "#adb5bd" : "#f1f3f5"; // 5단위 강조
            let px = w/2 + i*scale; let py = h/2 - i*scale;
            graphCtx.beginPath(); graphCtx.moveTo(px, 0); graphCtx.lineTo(px, h); graphCtx.stroke();
            graphCtx.beginPath(); graphCtx.moveTo(0, py); graphCtx.lineTo(w, py); graphCtx.stroke();
        }
        graphCtx.strokeStyle = "#495057"; graphCtx.lineWidth = 2;
        graphCtx.beginPath(); graphCtx.moveTo(0, h/2); graphCtx.lineTo(w, h/2);
        graphCtx.moveTo(w/2, 0); graphCtx.lineTo(w/2, h); graphCtx.stroke();

        graphCtx.fillStyle = "#212529"; graphCtx.font = "bold 12px Arial";
        graphCtx.textAlign = "center"; graphCtx.textBaseline = "middle";
        for(let i = -limit; i <= limit; i+=5) { // 5단위 숫자 표시
             if(i===0) continue;
             graphCtx.fillText(i, w/2 + i*scale, h/2 + 15);
             graphCtx.fillText(i, w/2 - 15, h/2 - i*scale);
        }
        graphCtx.fillText("0", w/2 - 10, h/2 + 15);
        
        graphCtx.strokeStyle = isEventMode ? "#7209b7" : "#e63946"; // 모드별 그래프 색상 변경
        graphCtx.lineWidth = 4; graphCtx.beginPath();
        for(let px = 0; px <= w; px += 2) {
            let mathX = (px - w/2) / scale;
            // 그래프는 항상 표준형 식을 이용해 그리면 됨 (동치이므로)
            let mathY = currentA * Math.pow(mathX - currentP, 2) + currentQ;
            let py = h/2 - mathY * scale;
            if(px === 0) graphCtx.moveTo(px, py); else graphCtx.lineTo(px, py);
        }
        graphCtx.stroke();
    }

    // === 먹이 생성 ===
    function spawnFoods() {
        foods = [];
        let correctVal, vals = [];

        if (isEventMode) {
            // 이벤트 모드: a, b, c '값' 맞추기
            correctVal = (stage === 0) ? genA : (stage === 1) ? genB : genC;
            // 오답 생성 (정답 주변 범위에서 랜덤)
            let wrong1, wrong2;
            do { wrong1 = correctVal + Math.floor(Math.random()*10) - 5; } while(wrong1 === correctVal);
            do { wrong2 = correctVal + Math.floor(Math.random()*10) - 5; } while(wrong2 === correctVal || wrong2 === wrong1);
            vals = [{v: correctVal, c: true}, {v: wrong1, c: false}, {v: wrong2, c: false}];
        } else {
            // 기본 모드
            if (stage === 0) { // a 부호
                vals = [{v: "+", c: currentA > 0}, {v: "-", c: currentA < 0}];
            } else { // p, q 값
                correctVal = (stage === 1) ? currentP : currentQ;
                let w1, w2;
                const range = 6;
                do { w1 = Math.floor(Math.random()*(range*2+1))-range; } while(w1===correctVal);
                do { w2 = Math.floor(Math.random()*(range*2+1))-range; } while(w2===correctVal || w2===w1);
                vals = [{v: correctVal, c: true}, {v: w1, c: false}, {v: w2, c: false}];
            }
        }
        
        // 좌표 배정
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

    // === 게임 메인 로직 ===
    function updateGame() {
        if(isGameOver) return;
        dx = nextDx; dy = nextDy;
        let head = {x: snake[0].x + dx, y: snake[0].y + dy};
        
        // 충돌 체크
        if(head.x<0||head.x>=tileCount||head.y<0||head.y>=tileCount) { endGame("벽에 부딪혔습니다! 💥"); return; }
        for(let i=0; i<snake.length; i++) { if(head.x===snake[i].x && head.y===snake[i].y) { endGame("자기 꼬리를 물었습니다! 😵"); return; } }
        
        snake.unshift(head); // 머리 이동
        
        let ateIdx = foods.findIndex(f => f.x === head.x && f.y === head.y);
        if(ateIdx !== -1) {
            if(foods[ateIdx].isCorrect) {
                // 정답!
                if(isEventMode) {
                    // 이벤트 모드 보상: 꼬리 3개 증가! (현재 머리 위치에 2개 더 추가)
                    snake.unshift({...head}); snake.unshift({...head});
                    score += 3;
                } else {
                    score += 1;
                }
                document.getElementById("score").innerText = score;
                
                // 속도 재계산 및 적용
                calculateSpeed();
                if(!isBoosting) startGameLoop(); 

                stage++;
                if(stage > 2) { 
                    problemsSolved++;
                    nextProblem(); // 다음 문제로
                } else { 
                    updateUI(); spawnFoods(); // 다음 단계로
                }
            } else {
                endGame(`오답! [ ${foods[ateIdx].val} ] 을(를) 먹었습니다. 😭`); return;
            }
        } else {
            snake.pop(); // 먹이 안 먹었으면 꼬리 자르기
        }
        drawGame();
    }

    function drawGame() {
        ctx.fillStyle = "#1a1a2e"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        // 먹이 그리기
        foods.forEach(f => {
            ctx.fillStyle = isEventMode ? "#ffd60a" : "#ffb703"; // 이벤트 먹이 색상 다르게
            ctx.beginPath(); ctx.arc(f.x*gridSize+gridSize/2, f.y*gridSize+gridSize/2, gridSize/2-2, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = "#023047"; 
            ctx.font = (f.val==="+"||f.val==="-") ? "bold 26px Arial" : "bold 18px Arial";
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(f.val, f.x*gridSize+gridSize/2, f.y*gridSize+gridSize/2);
        });
        // 지렁이 그리기
        for(let i=0; i<snake.length; i++) {
            let s = snake[i];
            if(i === 0) { // 머리
                ctx.fillStyle = isEventMode ? "#9b5de5" : "#06d6a0"; // 이벤트 모드 머리색 변경
                ctx.fillRect(s.x*gridSize, s.y*gridSize, gridSize-1, gridSize-1);
                ctx.fillStyle = "white"; ctx.fillRect(s.x*gridSize+4, s.y*gridSize+4, 5, 5); ctx.fillRect(s.x*gridSize+15, s.y*gridSize+4, 5, 5);
            } else { // 몸통
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
        isBoosting = false;
        problemsSolved = 0;
        isEventMode = false;
        document.getElementById("warningOverlay").style.display = "none";
        document.getElementById("overlay").style.display = "none";
        
        calculateSpeed(); // 초기 속도 설정
        nextProblem();
        isGameOver = false;
        startGameLoop();
    }

    function endGame(msg) {
        isGameOver = true; clearInterval(gameLoop);
        document.getElementById("overTitle").innerText = "게임 오버! 💀";
        document.getElementById("overDesc").innerHTML = `${msg}<br>최종 길이: <b>${score}</b> 🐛<br>(길수록 빨라집니다!)`;
        document.getElementById("overlay").style.display = "flex";
        isBoosting = false; document.getElementById("btnBoost").classList.remove("active");
    }

    // === 컨트롤 ===
    function changeDir(newDx, newDy) {
        if (dx !== 0 && newDy !== 0) { nextDx = 0; nextDy = newDy; }
        if (dy !== 0 && newDx !== 0) { nextDx = newDx; nextDy = 0; }
        if (dx === 0 && dy === 0) { nextDx = newDx; nextDy = newDy; }
    }
    const bindBtn = (id, ndx, ndy) => document.getElementById(id).addEventListener("pointerdown", (e)=>{e.preventDefault();changeDir(ndx, ndy);});
    bindBtn("btnUp", 0, -1); bindBtn("btnDown", 0, 1); bindBtn("btnLeft", -1, 0); bindBtn("btnRight", 1, 0);

    const btnBoost = document.getElementById("btnBoost");
    const toggleBoost = (on) => {
        if(isGameOver) return;
        isBoosting = on;
        if(on) btnBoost.classList.add("active"); else btnBoost.classList.remove("active");
        startGameLoop();
    };
    btnBoost.addEventListener("pointerdown", (e)=>{e.preventDefault(); toggleBoost(true);});
    ["pointerup", "pointerleave", "pointercancel"].forEach(evt => btnBoost.addEventListener(evt, (e)=>{e.preventDefault(); toggleBoost(false);}));
    document.getElementById("startBtn").addEventListener("pointerdown", (e)=>{e.preventDefault(); resetGame();});

    // 초기 화면 설정
    generateNormalProblem();
</script>
</body>
</html>
"""

components.html(game_html, height=800)
