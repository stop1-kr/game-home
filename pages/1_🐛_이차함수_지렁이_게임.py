import streamlit as st
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(page_title="✨이차함수 지렁이 대모험✨", page_icon="🐛", layout="wide")

st.markdown("""
    <style>
    /* 상단 여백 최소화 */
    .block-container {
        padding-top: 1.5rem;
        max-width: 1200px; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐛 ✨ 이차함수 지렁이 대모험! ✨ 🐛")
st.markdown("**목표:** 그래프 $y = a(x-p)^2 + q$ 를 보고, **a(부호) ➔ p ➔ q** 를 순서대로 맞추세요!")

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
            touch-action: none; /* 아이패드 스크롤, 확대 방지 */
            user-select: none;
            -webkit-user-select: none;
        }
        .container {
            position: relative; /* 워터마크 기준점 설정 */
            display: flex;
            flex-direction: row;
            gap: 30px;
            background: white;
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        /* 왼쪽: 게임 화면 + 목표 UI */
        .game-panel {
            position: relative;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        #gameCanvas {
            background-color: #1a1a2e;
            border-radius: 15px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
            border: 4px solid #4a4e69;
        }
        .status-box {
            background: #ffe3e3;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 1.4rem;
            font-weight: bold;
            color: #d90429;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: pulse 1.5s infinite;
        }
        
        /* 오른쪽: 그래프 & 컨트롤러 */
        .right-panel {
            display: flex;
            flex-direction: column;
            gap: 20px; /* 방향키가 잘 보이도록 간격 넉넉히 */
            width: 360px;
        }
        .graph-panel {
            background: white;
            border: 3px solid #dee2e6;
            border-radius: 15px;
            padding: 10px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        #graphCanvas {
            background-color: #ffffff;
            border-radius: 10px;
        }
        
        /* 십자 방향키(D-pad) 레이아웃 */
        .dpad-container {
            display: grid;
            grid-template-columns: 80px 80px 80px; /* 아이패드에 맞게 크기 최적화 */
            grid-template-rows: 80px 80px 80px;
            gap: 8px;
            justify-content: center;
            margin-top: 10px;
        }
        .btn {
            background: #457b9d;
            border: none;
            border-radius: 15px;
            color: white;
            font-size: 2.2rem;
            width: 100%;
            height: 100%;
            box-shadow: 0 6px 0 #1d3557;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            touch-action: manipulation;
        }
        .btn:active {
            transform: translateY(6px);
            box-shadow: 0 0 0 transparent;
            background: #1d3557;
        }
        
        /* 십자 배치 설정 */
        .btn.up { grid-column: 2; grid-row: 1; }
        .btn.left { grid-column: 1; grid-row: 2; }
        .btn.right { grid-column: 3; grid-row: 2; }
        .btn.down { grid-column: 2; grid-row: 3; }
        
        /* 부스트 버튼 (정중앙) */
        .btn.boost {
            grid-column: 2; grid-row: 2;
            background: #fca311;
            box-shadow: 0 6px 0 #d08c00;
            font-size: 1.8rem;
        }
        .btn.boost.active {
            background: #d90429;
            box-shadow: 0 6px 0 transparent;
            transform: translateY(6px);
        }
        
        /* 오버레이 (시작/종료) */
        .overlay {
            position: absolute;
            top: 0; left: 0; width: 500px; height: 500px;
            background: rgba(0,0,0,0.75);
            border-radius: 15px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 10;
        }
        .overlay h1 { font-size: 3rem; margin-bottom: 10px; text-shadow: 2px 2px 4px #000; }
        .overlay p { font-size: 1.5rem; margin-bottom: 30px; text-align: center; }
        .start-btn {
            padding: 15px 40px;
            font-size: 1.8rem;
            font-weight: bold;
            border: none;
            border-radius: 40px;
            background: #e63946;
            color: white;
            cursor: pointer;
            box-shadow: 0 6px 15px rgba(230, 57, 70, 0.5);
        }
        
        /* 제작자 마크 (왼쪽 구석, 희미하게, 터치 통과) */
        .watermark {
            position: absolute;
            bottom: 10px;
            left: 20px;
            font-size: 13px;
            color: #adb5bd;
            opacity: 0.5;
            font-weight: bold;
            pointer-events: none; /* 터치 방해 금지 */
            z-index: 5;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
    </style>
</head>
<body>

<div class="container">
    <!-- 워터마크 추가 -->
    <div class="watermark">stop1</div>

    <!-- 왼쪽: 게임 캔버스 + 현재 목표 UI -->
    <div class="game-panel">
        <canvas id="gameCanvas" width="500" height="500"></canvas>
        <div id="overlay" class="overlay">
            <h1 id="overTitle">🐍 지렁이 대모험</h1>
            <p id="overDesc">그래프를 보고<br>a(부호), p, q를 찾아 지렁이를 키우세요!</p>
            <button id="startBtn" class="start-btn">게임 시작 🚀</button>
        </div>
        
        <!-- 현재 목표 알림창을 게임화면 바로 아래로 이동 -->
        <div class="status-box" id="targetBox">
            🔥 현재 목표: <span id="targetVar" style="font-size:1.7rem;">a (부호)</span>
        </div>
    </div>

    <!-- 오른쪽: 그래프 및 방향키 -->
    <div class="right-panel">
        <div class="graph-panel">
            <h3 style="margin: 5px 0; color:#343a40;">y = a(x-p)² + q</h3>
            <canvas id="graphCanvas" width="340" height="340"></canvas>
        </div>
        
        <!-- 방향키 십자배열 및 중앙 부스트 (위로 당겨짐) -->
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
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");
    const graphCanvas = document.getElementById("graphCanvas");
    const graphCtx = graphCanvas.getContext("2d");
    
    const gridSize = 25;
    const tileCount = canvas.width / gridSize;
    
    let snake = [];
    let dx = 0; let dy = 0;
    let nextDx = 0; let nextDy = 0;
    
    let score = 3;
    let gameLoop;
    let isGameOver = true;
    
    // 속도 설정
    const SLOW_SPEED = 500;  // 0.5초 (기본)
    const FAST_SPEED = 120;  // 0.12초 (부스트 시)
    let currentSpeed = SLOW_SPEED;
    
    // 이차함수 관련 변수
    let currentA, currentP, currentQ;
    let targetStage = 0; // 0:a(부호), 1:p, 2:q
    const stageDesc = ['a (볼록 방향 +, -)', 'p (꼭짓점 x좌표)', 'q (꼭짓점 y좌표)'];
    let foods = [];

    // === 문제 생성 ===
    function generateProblem() {
        const aPool = [-2, -1, 1, 2];
        currentA = aPool[Math.floor(Math.random() * aPool.length)];
        currentP = Math.floor(Math.random() * 13) - 6;
        currentQ = Math.floor(Math.random() * 13) - 6;
        
        targetStage = 0;
        document.getElementById("targetVar").innerText = stageDesc[targetStage];
        drawMathGraph();
        spawnFoods();
    }

    // === 그래프 그리기 ===
    function drawMathGraph() {
        const w = graphCanvas.width; const h = graphCanvas.height;
        const limit = 10; const scale = w / (limit * 2); 
        
        graphCtx.clearRect(0, 0, w, h);
        graphCtx.lineWidth = 1;
        for(let i = -limit; i <= limit; i++) {
            graphCtx.strokeStyle = (i % 3 === 0) ? "#ced4da" : "#f1f3f5";
            let px = w/2 + i*scale; let py = h/2 - i*scale;
            graphCtx.beginPath(); graphCtx.moveTo(px, 0); graphCtx.lineTo(px, h); graphCtx.stroke();
            graphCtx.beginPath(); graphCtx.moveTo(0, py); graphCtx.lineTo(w, py); graphCtx.stroke();
        }
        
        graphCtx.strokeStyle = "#495057"; graphCtx.lineWidth = 2;
        graphCtx.beginPath();
        graphCtx.moveTo(0, h/2); graphCtx.lineTo(w, h/2);
        graphCtx.moveTo(w/2, 0); graphCtx.lineTo(w/2, h);
        graphCtx.stroke();

        graphCtx.fillStyle = "#212529"; graphCtx.font = "bold 13px Arial";
        graphCtx.textAlign = "center"; graphCtx.textBaseline = "middle";
        for(let i = -limit; i <= limit; i++) {
            if(i !== 0 && i % 3 === 0) {
                graphCtx.fillText(i, w/2 + i*scale, h/2 + 15);
                graphCtx.fillText(i, w/2 - 15, h/2 - i*scale);
            }
        }
        graphCtx.fillText("0", w/2 - 12, h/2 + 15);
        
        graphCtx.strokeStyle = "#e63946"; graphCtx.lineWidth = 4;
        graphCtx.beginPath();
        for(let px = 0; px <= w; px += 2) {
            let mathX = (px - w/2) / scale;
            let mathY = currentA * Math.pow(mathX - currentP, 2) + currentQ;
            let py = h/2 - mathY * scale;
            if(px === 0) graphCtx.moveTo(px, py);
            else graphCtx.lineTo(px, py);
        }
        graphCtx.stroke();
    }

    // === 블록 생성 로직 ===
    function spawnFoods() {
        foods = [];
        
        if (targetStage === 0) {
            // 1단계(a)일 때는 + 와 - 딱 2개의 블록
            const isPositive = currentA > 0;
            const vals = [
                {val: "+", isCorrect: isPositive},
                {val: "-", isCorrect: !isPositive}
            ];
            vals.forEach(item => {
                let fx, fy, occupied;
                do {
                    occupied = false;
                    fx = Math.floor(Math.random() * (tileCount - 2)) + 1;
                    fy = Math.floor(Math.random() * (tileCount - 2)) + 1;
                    for(let s of snake) if(s.x === fx && s.y === fy) occupied = true;
                    for(let f of foods) if(f.x === fx && f.y === fy) occupied = true;
                } while(occupied);
                foods.push({x: fx, y: fy, val: item.val, isCorrect: item.isCorrect});
            });
        } else {
            // 2단계, 3단계(p, q)일 때는 숫자 3개
            let correctVal = (targetStage === 1) ? currentP : currentQ;
            let wrong1, wrong2;
            do { wrong1 = Math.floor(Math.random() * 13) - 6; } while(wrong1 === correctVal);
            do { wrong2 = Math.floor(Math.random() * 13) - 6; } while(wrong2 === correctVal || wrong2 === wrong1);
            
            const vals = [
                {val: correctVal, isCorrect: true},
                {val: wrong1, isCorrect: false},
                {val: wrong2, isCorrect: false}
            ];
            
            vals.forEach(item => {
                let fx, fy, occupied;
                do {
                    occupied = false;
                    fx = Math.floor(Math.random() * (tileCount - 2)) + 1;
                    fy = Math.floor(Math.random() * (tileCount - 2)) + 1;
                    for(let s of snake) if(s.x === fx && s.y === fy) occupied = true;
                    for(let f of foods) if(f.x === fx && f.y === fy) occupied = true;
                } while(occupied);
                foods.push({x: fx, y: fy, val: item.val, isCorrect: item.isCorrect});
            });
        }
    }

    function resetGame() {
        snake = [ {x: 10, y: 10}, {x: 10, y: 11}, {x: 10, y: 12} ];
        score = 3; document.getElementById("score").innerText = score;
        dx = 0; dy = -1; nextDx = 0; nextDy = -1;
        
        generateProblem();
        isGameOver = false;
        document.getElementById("overlay").style.display = "none";
        
        startGameLoop();
    }

    function startGameLoop() {
        if(gameLoop) clearInterval(gameLoop);
        gameLoop = setInterval(updateGame, currentSpeed);
    }

    function updateGame() {
        if(isGameOver) return;
        dx = nextDx; dy = nextDy;
        let head = {x: snake[0].x + dx, y: snake[0].y + dy};
        
        if(head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
            endGame("앗! 벽에 부딪혔어요! 💥"); return;
        }
        for(let i=0; i<snake.length; i++) {
            if(head.x === snake[i].x && head.y === snake[i].y) {
                endGame("앗! 자기 꼬리를 물었어요! 😵"); return;
            }
        }
        
        snake.unshift(head);
        
        let ate = foods.findIndex(f => f.x === head.x && f.y === head.y);
        if(ate !== -1) {
            if(foods[ate].isCorrect) {
                score++; document.getElementById("score").innerText = score;
                targetStage++;
                if(targetStage > 2) { generateProblem(); } 
                else { 
                    document.getElementById("targetVar").innerText = stageDesc[targetStage];
                    spawnFoods(); 
                }
            } else {
                endGame(`오답입니다! [ ${foods[ate].val} ] 을(를) 먹었습니다 😭`); return;
            }
        } else {
            snake.pop();
        }
        drawGame();
    }

    function drawGame() {
        ctx.fillStyle = "#1a1a2e"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = "#27293d"; ctx.lineWidth = 1;
        for(let i=0; i<tileCount; i++) {
            ctx.beginPath();
            ctx.moveTo(i*gridSize, 0); ctx.lineTo(i*gridSize, canvas.height);
            ctx.moveTo(0, i*gridSize); ctx.lineTo(canvas.width, i*gridSize);
            ctx.stroke();
        }

        foods.forEach(f => {
            ctx.fillStyle = "#ffb703"; ctx.beginPath();
            ctx.arc(f.x*gridSize + gridSize/2, f.y*gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = "#023047"; 
            
            if(f.val === "+" || f.val === "-") {
                ctx.font = "bold 26px Arial"; // 부호는 큼직하게
            } else {
                ctx.font = "bold 16px Arial";
            }
            ctx.textAlign = "center"; ctx.textBaseline = "middle";
            ctx.fillText(f.val, f.x*gridSize + gridSize/2, f.y*gridSize + gridSize/2);
        });
        
        for(let i=0; i<snake.length; i++) {
            let s = snake[i];
            if(i === 0) {
                ctx.fillStyle = "#06d6a0";
                ctx.fillRect(s.x*gridSize, s.y*gridSize, gridSize-1, gridSize-1);
                ctx.fillStyle = "white";
                ctx.fillRect(s.x*gridSize + 4, s.y*gridSize + 4, 5, 5);
                ctx.fillRect(s.x*gridSize + 15, s.y*gridSize + 4, 5, 5);
            } else {
                ctx.fillStyle = `rgb(6, ${Math.max(100, 214 - i*4)}, 160)`;
                ctx.fillRect(s.x*gridSize+1, s.y*gridSize+1, gridSize-3, gridSize-3);
            }
        }
    }

    function endGame(msg) {
        isGameOver = true; clearInterval(gameLoop);
        document.getElementById("overTitle").innerText = "게임 오버! 💀";
        document.getElementById("overDesc").innerHTML = `${msg}<br><br>최종 길이: <b>${score}</b> 🐛`;
        document.getElementById("startBtn").innerText = "다시 도전하기 🔄";
        document.getElementById("overlay").style.display = "flex";
        
        currentSpeed = SLOW_SPEED;
        document.getElementById("btnBoost").classList.remove("active");
    }

    // === 방향키 조작 ===
    function changeDir(newDx, newDy) {
        if (dx !== 0 && newDy !== 0) { nextDx = 0; nextDy = newDy; }
        if (dy !== 0 && newDx !== 0) { nextDx = newDx; nextDy = 0; }
        if (dx === 0 && dy === 0) { nextDx = newDx; nextDy = newDy; }
    }

    const bindBtn = (id, ndx, ndy) => {
        document.getElementById(id).addEventListener("pointerdown", (e) => { 
            e.preventDefault(); changeDir(ndx, ndy); 
        });
    };
    bindBtn("btnUp", 0, -1); bindBtn("btnDown", 0, 1);
    bindBtn("btnLeft", -1, 0); bindBtn("btnRight", 1, 0);

    // === 부스트(로켓) 누르고 있을 때만 작동 ===
    const btnBoost = document.getElementById("btnBoost");
    
    const startBoost = (e) => {
        if(e) e.preventDefault();
        if(isGameOver) return;
        currentSpeed = FAST_SPEED;
        btnBoost.classList.add("active");
        startGameLoop(); 
    };
    
    const stopBoost = (e) => {
        if(e) e.preventDefault();
        if(isGameOver) return;
        currentSpeed = SLOW_SPEED;
        btnBoost.classList.remove("active");
        startGameLoop(); 
    };

    btnBoost.addEventListener("pointerdown", startBoost);
    btnBoost.addEventListener("pointerup", stopBoost);
    btnBoost.addEventListener("pointerleave", stopBoost);
    btnBoost.addEventListener("pointercancel", stopBoost);

    document.getElementById("startBtn").addEventListener("pointerdown", (e) => { 
        e.preventDefault(); resetGame(); 
    });

    drawMathGraph();
</script>
</body>
</html>
"""

# HTML 렌더링 (높이를 800으로 키워서 아래쪽 버튼 잘림 현상 원천 차단)
components.html(game_html, height=800)
