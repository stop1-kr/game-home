import streamlit as st
import streamlit.components.v1 as components

# Streamlit 페이지 기본 설정
st.set_page_config(
    page_title="Square Root Drop",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 기본 여백을 줄여 게임 화면을 최대한 크게 만들기 위한 CSS
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
        }
        iframe {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# 제작하신 게임의 전체 HTML/CSS/JS 코드를 문자열로 담습니다.
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Square Root Drop</title>
    
    <!-- 폰트 불러오기 -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS (CDN) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Nunito', 'sans-serif'],
                        mono: ['Nunito', 'monospace'],
                    },
                    animation: {
                        rainbow: 'rainbow 3s linear infinite',
                        shake: 'shake 0.1s ease-in-out infinite',
                        pop: 'pop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards',
                    },
                    keyframes: {
                        rainbow: {
                            '0%': { backgroundPosition: '0% 50%' },
                            '50%': { backgroundPosition: '100% 50%' },
                            '100%': { backgroundPosition: '0% 50%' },
                        },
                        shake: {
                            '0%, 100%': { transform: 'translate(0, 0) rotate(0deg)' },
                            '25%': { transform: 'translate(8px, 8px) rotate(2deg)' },
                            '50%': { transform: 'translate(-8px, -8px) rotate(-2deg)' },
                            '75%': { transform: 'translate(-8px, 8px) rotate(2deg)' },
                        },
                        pop: {
                            '0%': { transform: 'scale(0.5)', opacity: '0' },
                            '50%': { transform: 'scale(1.2)', opacity: '1' },
                            '100%': { transform: 'scale(1)', opacity: '0' },
                        }
                    }
                }
            }
        }
    </script>

    <!-- React & ReactDOM (CDN) -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    
    <!-- Babel (JSX 컴파일용 CDN) -->
    <!-- ★ 수정: 버전 고정(7.22.5)으로 동작 안정화 -->
    <script src="https://unpkg.com/@babel/standalone@7.22.5/babel.min.js"></script>

    <!-- ★ 수정: classic JSX runtime을 쓰는 커스텀 프리셋 등록 -->
    <!-- 이게 있어야 Babel이 변환 결과에 import 문을 넣지 않습니다. -->
    <script>
        Babel.registerPreset('react-classic', {
            presets: [
                [Babel.availablePresets['react'], { runtime: 'classic' }]
            ]
        });
    </script>

    <style>
        body { margin: 0; padding: 0; background-color: #0a0a0a; overflow: hidden; }
    </style>
</head>
<body>
    <div id="root"></div>

    <!-- ★ 수정: data-presets="react-classic" 속성 추가 -->
    <script type="text/babel" data-presets="react-classic">
        const { useState, useEffect, useRef, useCallback } = React;

        // 아이콘 SVG 컴포넌트
        const Heart = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>);
        const HeartCrack = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="m12 13-1-1 2-2-3-3 2-2"/></svg>);
        const Play = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><polygon points="6 3 20 12 6 21 6 3"/></svg>);
        const RotateCcw = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>);
        const Delete = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><path d="M20 5H9l-7 7 7 7h11a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2Z"/><line x1="18" x2="12" y1="9" y2="15"/><line x1="12" x2="18" y1="9" y2="15"/></svg>);
        const Bomb = ({ className }) => (<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><circle cx="11" cy="13" r="9"/><path d="M14.35 4.65 16.3 2.7a2.41 2.41 0 0 1 3.4 0l1.6 1.6a2.4 2.4 0 0 1 0 3.4l-1.95 1.95"/><path d="m22 2-1.5 1.5"/></svg>);

        const B_VALUES = [2, 3, 5, 6, 7, 10, 11, 13];

        const generateExpression = () => {
            const b = B_VALUES[Math.floor(Math.random() * B_VALUES.length)];
            const numTerms = Math.random() > 0.5 ? 2 : 3;
            
            let terms = [];
            let totalA = 0;
            
            for (let i = 0; i < numTerms; i++) {
                let c = Math.floor(Math.random() * 4) + 1;
                let sign = Math.random() > 0.3 ? 1 : -1;
                
                if (totalA + sign * c <= 0) {
                    sign = 1;
                }
                
                totalA += sign * c;
                
                let formatType = Math.random();
                let termStr = "";
                if (formatType < 0.5 && c > 1) {
                    termStr = `√${c * c * b}`;
                } else {
                    if (c === 1) {
                        termStr = `√${b}`;
                    } else {
                        termStr = `${c}√${b}`;
                    }
                }
                
                if (i === 0) {
                    terms.push(sign === -1 ? `-${termStr}` : termStr);
                } else {
                    terms.push(sign === -1 ? `- ${termStr}` : `+ ${termStr}`);
                }
            }
            
            return {
                expression: terms.join(" "),
                a: totalA,
                b: b
            };
        };

        const getRandomType = () => {
            const r = Math.random();
            if (r < 0.80) return 'NORMAL';
            
            const specialR = Math.random();
            if (specialR < 0.1) return 'SPECIAL_RESET';
            if (specialR < 0.4) return 'SPECIAL_500';
            if (specialR < 0.7) return 'SPECIAL_X2';
            return 'SPECIAL_X3';
        };

        function App() {
            const [gameState, setGameState] = useState('START');
            const [score, setScore] = useState(0);
            const [health, setHealth] = useState(3);
            const [timeLeft, setTimeLeft] = useState(90);
            const [blocks, setBlocks] = useState([]);
            const [activeEffect, setActiveEffect] = useState(null);
            
            const blocksRef = useRef([]);
            const effectTimeoutRef = useRef(null);
            
            useEffect(() => {
                blocksRef.current = blocks;
            }, [blocks]);
            
            const [inputA, setInputA] = useState('');
            const [inputB, setInputB] = useState('');
            const [inputStep, setInputStep] = useState('A');

            const requestRef = useRef(null);
            const lastTimeRef = useRef(null);
            const spawnTimerRef = useRef(0);

            const startGame = () => {
                setGameState('PLAYING');
                setScore(0);
                setHealth(3);
                setTimeLeft(90);
                setBlocks([]);
                setActiveEffect(null);
                setInputA('');
                setInputB('');
                setInputStep('A');
                lastTimeRef.current = performance.now();
                spawnTimerRef.current = 2000; 
            };

            const endGame = useCallback(() => {
                setGameState('GAMEOVER');
                setActiveEffect(null);
                if (effectTimeoutRef.current) clearTimeout(effectTimeoutRef.current);
                if (requestRef.current) cancelAnimationFrame(requestRef.current);
            }, []);

            const triggerEffect = (type) => {
                if (effectTimeoutRef.current) clearTimeout(effectTimeoutRef.current);
                setActiveEffect(type);
                const duration = type === 'BOMB' ? 2000 : 500;
                effectTimeoutRef.current = setTimeout(() => {
                    setActiveEffect(null);
                }, duration);
            };

            const handleAnswerSubmit = useCallback(() => {
                if (!inputA || !inputB) return;
                
                const numA = parseInt(inputA, 10);
                const numB = parseInt(inputB, 10);
                
                const targetBlock = blocksRef.current.find(b => b.a === numA && b.b === numB);
                
                if (targetBlock) {
                    setScore(prev => {
                        let newScore = prev;
                        switch (targetBlock.type) {
                            case 'NORMAL': 
                                newScore += 100; 
                                break;
                            case 'SPECIAL_500': 
                                newScore += 500; 
                                triggerEffect('+500');
                                break;
                            case 'SPECIAL_X2': 
                                newScore *= 2; 
                                triggerEffect('X2');
                                break;
                            case 'SPECIAL_X3': 
                                newScore *= 3; 
                                triggerEffect('X3');
                                break;
                            case 'SPECIAL_RESET': 
                                newScore = 0; 
                                triggerEffect('BOMB');
                                break;
                        }
                        return newScore;
                    });
                    
                    setBlocks(prev => prev.filter(b => b.id !== targetBlock.id));
                } else {
                    setHealth(prev => {
                        const newHealth = prev - 1;
                        if (newHealth <= 0) {
                            endGame();
                        }
                        return newHealth;
                    });
                }
                
                setInputA('');
                setInputB('');
                setInputStep('A');
            }, [inputA, inputB, endGame]);

            const handleActionClick = useCallback(() => {
                if (inputStep === 'A') {
                    if (inputA) setInputStep('B');
                } else {
                    if (inputB) handleAnswerSubmit();
                }
            }, [inputStep, inputA, inputB, handleAnswerSubmit]);

            const handleKeyPress = useCallback((e) => {
                if (gameState !== 'PLAYING') return;
                
                if (e.key >= '0' && e.key <= '9') {
                    if (inputStep === 'A') {
                        setInputA(prev => (prev + e.key).slice(0, 3));
                    } else {
                        setInputB(prev => (prev + e.key).slice(0, 3));
                    }
                } else if (e.key === 'Backspace') {
                    if (inputStep === 'A') {
                        setInputA(prev => prev.slice(0, -1));
                    } else {
                        if (inputB === '') {
                            setInputStep('A');
                        } else {
                            setInputB(prev => prev.slice(0, -1));
                        }
                    }
                } else if (e.key === 'Enter') {
                    handleActionClick();
                }
            }, [gameState, inputStep, inputA, inputB, handleActionClick]);

            useEffect(() => {
                window.addEventListener('keydown', handleKeyPress);
                return () => window.removeEventListener('keydown', handleKeyPress);
            }, [handleKeyPress]);

            const update = useCallback((time) => {
                if (gameState !== 'PLAYING') return;
                
                if (!lastTimeRef.current) lastTimeRef.current = time;
                const deltaTime = time - lastTimeRef.current;
                lastTimeRef.current = time;
                
                setBlocks(prev => {
                    return prev.map(b => ({ ...b, y: b.y + b.speed * (deltaTime / 16) })).filter(b => b.y < 90);
                });
                
                spawnTimerRef.current += deltaTime;
                if (spawnTimerRef.current > 2666) {
                    spawnTimerRef.current = 0;
                    const expr = generateExpression();
                    const newBlock = {
                        id: Math.random().toString(36).substring(2, 9),
                        ...expr,
                        type: getRandomType(),
                        x: Math.random() * 70 + 15,
                        y: -10,
                        speed: ((Math.random() * 0.1 + 0.15) / 2) * 0.7
                    };
                    setBlocks(prev => [...prev, newBlock]);
                }
                
                requestRef.current = requestAnimationFrame(update);
            }, [gameState]);

            useEffect(() => {
                if (gameState === 'PLAYING') {
                    requestRef.current = requestAnimationFrame(update);
                }
                return () => {
                    if (requestRef.current) cancelAnimationFrame(requestRef.current);
                };
            }, [gameState, update]);

            useEffect(() => {
                if (gameState === 'PLAYING') {
                    const timer = setInterval(() => {
                        setTimeLeft(prev => {
                            if (prev <= 1) {
                                clearInterval(timer);
                                endGame();
                                return 0;
                            }
                            return prev - 1;
                        });
                    }, 1000);
                    return () => clearInterval(timer);
                }
            }, [gameState, endGame]);

            const renderHearts = () => {
                const hearts = [];
                for (let i = 0; i < 3; i++) {
                    if (i < health) {
                        hearts.push(<Heart key={i} className="w-6 h-6 text-red-500" />);
                    } else {
                        hearts.push(<HeartCrack key={i} className="w-6 h-6 text-neutral-600" />);
                    }
                }
                return hearts;
            };

            return (
                <div className={`min-h-screen bg-neutral-950 text-white font-sans overflow-hidden flex relative selection:bg-indigo-500/30 ${activeEffect === 'BOMB' ? 'animate-shake' : ''}`}>
                    <div className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f2e_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f2e_1px,transparent_1px)] bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_0%,#000_70%,transparent_110%)] pointer-events-none" />

                    {activeEffect && (
                        <div className="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
                            {activeEffect === 'BOMB' ? (
                                <Bomb className="w-64 h-64 text-red-500 drop-shadow-[0_0_50px_rgba(255,0,0,1)]" />
                            ) : (
                                <div className="text-[120px] font-black text-transparent bg-clip-text bg-gradient-to-br from-yellow-300 to-red-500 drop-shadow-[0_0_50px_rgba(255,0,0,0.8)] animate-pop">
                                    {activeEffect}
                                </div>
                            )}
                        </div>
                    )}

                    {gameState === 'START' && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 backdrop-blur-sm bg-black/40">
                            <h1 className="text-7xl font-black tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-neutral-500 text-center drop-shadow-lg">
                                SQUARE ROOT
                                <br />
                                <span className="text-indigo-500">DROP</span>
                            </h1>
                            <p className="text-neutral-300 mb-12 max-w-md text-center text-lg leading-relaxed font-bold">
                                떨어지는 제곱근 식을 계산하여<br/>알맞은 a√b 형태로 입력하세요.
                            </p>
                            <button
                                onClick={startGame}
                                className="group relative px-12 py-6 bg-white text-black font-black text-3xl rounded-full overflow-hidden transition-transform hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(255,255,255,0.3)]"
                            >
                                <div className="absolute inset-0 bg-indigo-500 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out" />
                                <span className="relative flex items-center gap-3 group-hover:text-white transition-colors duration-300">
                                    <Play className="w-8 h-8 fill-current" />
                                    START
                                </span>
                            </button>
                            
                            <div className="absolute bottom-6 right-8 text-neutral-500 font-black text-lg tracking-widest opacity-70">
                                made by stop1
                            </div>
                        </div>
                    )}

                    {gameState === 'GAMEOVER' && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center z-50 backdrop-blur-md bg-black/60">
                            <h2 className="text-6xl font-black mb-4 text-red-500 tracking-tight drop-shadow-lg">GAME OVER</h2>
                            <div className="text-4xl font-bold mb-12 text-white bg-white/10 px-8 py-4 rounded-3xl border border-white/20">
                                점수 : {score}점
                            </div>
                            <button
                                onClick={() => setGameState('START')}
                                className="flex items-center gap-3 px-10 py-5 bg-white text-black rounded-full font-black text-2xl hover:bg-neutral-200 transition-colors shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:scale-105 active:scale-95"
                            >
                                <RotateCcw className="w-7 h-7" />
                                RETRY
                            </button>
                        </div>
                    )}

                    <div className="flex-1 flex flex-col relative z-10">
                        <header className="flex justify-between items-center p-6">
                            <div className="flex gap-2 bg-black/30 p-3 rounded-2xl backdrop-blur-sm border border-white/10">
                                {renderHearts()}
                            </div>
                            
                            {gameState === 'PLAYING' && (
                                <div className="absolute left-1/2 -translate-x-1/2 text-3xl font-black text-neutral-200 bg-black/30 px-6 py-2 rounded-2xl backdrop-blur-sm border border-white/10">
                                    {Math.floor(timeLeft / 60).toString().padStart(2, '0')}:{(timeLeft % 60).toString().padStart(2, '0')}
                                </div>
                            )}

                            <div className="text-2xl font-bold text-indigo-300 bg-indigo-950/80 px-6 py-3 rounded-2xl border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.3)] backdrop-blur-sm">
                                점수 : {score}점
                            </div>
                        </header>

                        <main className="flex-1 relative w-full overflow-hidden">
                            <div className="absolute top-[90%] left-0 right-0 h-[3px] bg-red-500 shadow-[0_0_15px_rgba(239,68,68,1)] z-0" />
                            <div className="absolute top-[90%] left-0 right-0 h-12 bg-gradient-to-b from-red-500/30 to-transparent z-0" />
                            <div className="absolute top-[90%] left-4 text-red-400 font-black text-sm tracking-widest -mt-6 opacity-80">DANGER ZONE</div>

                            {gameState === 'PLAYING' && blocks.map(block => (
                                <div
                                    key={block.id}
                                    className={`absolute px-6 py-4 rounded-full text-2xl font-black shadow-xl transition-transform whitespace-nowrap z-10 ${
                                        block.type === 'NORMAL' 
                                            ? 'bg-neutral-800 border-2 border-neutral-600 text-white' 
                                            : 'bg-[linear-gradient(45deg,#ff0000,#ff8000,#ffff00,#00ff00,#0000ff,#8000ff,#ff0000)] bg-[length:200%_200%] animate-rainbow border-4 border-white shadow-[0_0_30px_rgba(255,255,255,0.5)] text-white'
                                    }`}
                                    style={{
                                        left: `${block.x}%`,
                                        top: `${block.y}%`,
                                        transform: 'translate(-50%, -50%)',
                                    }}
                                >
                                    {block.expression}
                                </div>
                            ))}
                        </main>
                    </div>

                    {gameState === 'PLAYING' && (
                        <div className="w-[420px] relative z-10 border-l border-white/10 bg-neutral-900/80 backdrop-blur-xl p-8 flex flex-col justify-center shadow-[-20px_0_50px_rgba(0,0,0,0.5)]">
                            <div className="flex items-center justify-center gap-4 mb-10 text-5xl font-black">
                                <div 
                                    className={`w-24 h-24 flex items-center justify-center rounded-3xl border-4 transition-all cursor-pointer ${
                                        inputStep === 'A' ? 'border-indigo-500 bg-indigo-500/20 text-indigo-300 shadow-[0_0_25px_rgba(99,102,241,0.4)] scale-110' : 'border-neutral-700 bg-neutral-800 text-white hover:border-neutral-500'
                                    }`}
                                    onClick={() => setInputStep('A')}
                                >
                                    {inputA}
                                </div>
                                <div className="text-neutral-400 font-bold">√</div>
                                <div 
                                    className={`w-24 h-24 flex items-center justify-center rounded-3xl border-4 transition-all cursor-pointer ${
                                        inputStep === 'B' ? 'border-indigo-500 bg-indigo-500/20 text-indigo-300 shadow-[0_0_25px_rgba(99,102,241,0.4)] scale-110' : 'border-neutral-700 bg-neutral-800 text-white hover:border-neutral-500'
                                    }`}
                                    onClick={() => setInputStep('B')}
                                >
                                    {inputB}
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-4">
                                {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(num => (
                                    <button
                                        key={num}
                                        onClick={() => {
                                            if (inputStep === 'A') setInputA(prev => (prev + num).slice(0, 3));
                                            else setInputB(prev => (prev + num).slice(0, 3));
                                        }}
                                        className="h-20 bg-neutral-800 hover:bg-neutral-700 rounded-3xl text-3xl font-black transition-all active:scale-95 shadow-lg border border-white/5"
                                    >
                                        {num}
                                    </button>
                                ))}
                                <button
                                    onClick={() => {
                                        if (inputStep === 'A') setInputA(prev => prev.slice(0, -1));
                                        else setInputB(prev => prev.slice(0, -1));
                                    }}
                                    className="h-20 bg-neutral-800 hover:bg-red-900/40 hover:text-red-400 rounded-3xl flex items-center justify-center transition-all active:scale-95 shadow-lg border border-white/5"
                                >
                                    <Delete className="w-8 h-8" />
                                </button>
                                <button
                                    onClick={() => {
                                        if (inputStep === 'A') setInputA(prev => (prev + '0').slice(0, 3));
                                        else setInputB(prev => (prev + '0').slice(0, 3));
                                    }}
                                    className="h-20 bg-neutral-800 hover:bg-neutral-700 rounded-3xl text-3xl font-black transition-all active:scale-95 shadow-lg border border-white/5"
                                >
                                    0
                                </button>
                                <button
                                    onClick={handleActionClick}
                                    className={`h-20 rounded-3xl text-2xl font-black transition-all active:scale-95 shadow-lg ${
                                        inputStep === 'A' 
                                            ? 'bg-neutral-700 hover:bg-neutral-600 text-white border border-white/10' 
                                            : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-[0_0_25px_rgba(79,70,229,0.5)] border border-indigo-400/50'
                                    }`}
                                >
                                    {inputStep === 'A' ? '다음' : '확인'}
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            );
        }

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

# HTML을 Streamlit 앱 상에 렌더링 (height를 넉넉하게 주어 스크롤 바를 없앱니다)
components.html(html_code, height=850, scrolling=False)
