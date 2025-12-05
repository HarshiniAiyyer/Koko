import React, { useState, useEffect, useRef } from 'react';
import {
    Brain, Zap, BookOpen, History, Activity, Sparkles,
    ChevronRight, Shield, Heart, TrendingUp, X, Menu,
    AlertCircle, HelpCircle, ArrowRight, Sliders,
    RotateCcw, Copy, Check, Diamond, Club, Spade, Star, ThumbsUp
} from 'lucide-react';
import axios from 'axios';

// --- Card Theme Constants ---

const TONES = {
    MENTOR: {
        id: 'mentor',
        label: 'The Mentor',
        suit: '♦',
        rank: 'K',
        icon: Diamond,
        color: 'text-blue-700',
        border: 'border-blue-200',
        realColor: 'text-red-600'
    },
    HYPE: {
        id: 'hype',
        label: 'The Hype',
        suit: '♣',
        rank: 'J',
        icon: Club,
        color: 'text-slate-800',
        border: 'border-slate-300',
        realColor: 'text-slate-900'
    },
    THERAPIST: {
        id: 'therapist',
        label: 'The Healer',
        suit: '♥',
        rank: 'Q',
        icon: Heart,
        color: 'text-red-600',
        border: 'border-red-200',
        realColor: 'text-red-600'
    },
    WITTY: {
        id: 'witty',
        label: 'The Joker',
        suit: '★',
        rank: 'Jkr',
        icon: Sparkles,
        color: 'text-purple-700',
        border: 'border-purple-200',
        realColor: 'text-purple-700'
    },
    DEBATE: {
        id: 'debate',
        label: 'The Critic',
        suit: '♠',
        rank: '10',
        icon: Spade,
        color: 'text-slate-900',
        border: 'border-slate-400',
        realColor: 'text-slate-900'
    }
};

// Map UI tone IDs to Backend Persona IDs
const TONE_MAPPING = {
    'mentor': 'calm_mentor',
    'hype': 'witty_friend',
    'therapist': 'therapist',
    'witty': 'witty_friend',
    'debate': 'calm_mentor'
};

// --- Card Stack Component ---
const CardStack = ({ children, className = "", suit = "♠", rank = "A", color = "text-slate-900" }) => (
    <div className={`relative group w-full h-full min-h-[500px] ${className}`}>
        {/* Stack Layer 2 */}
        <div className="absolute inset-0 bg-white rounded-[1rem] transform translate-x-3 translate-y-3 rotate-1 border border-slate-300 shadow-xl z-0 transition-transform group-hover:translate-x-4 group-hover:translate-y-4 group-hover:rotate-2 opacity-60"></div>

        {/* Stack Layer 1 */}
        <div className="absolute inset-0 bg-white rounded-[1rem] transform translate-x-1.5 translate-y-1.5 rotate-[0.5deg] border border-slate-300 shadow-xl z-10 transition-transform group-hover:translate-x-2 group-hover:translate-y-2 group-hover:rotate-1 opacity-80"></div>

        {/* Main Top Card */}
        <div className="absolute inset-0 bg-white text-slate-900 rounded-[1rem] shadow-2xl border border-slate-200 overflow-hidden flex flex-col z-20 transition-transform group-hover:-translate-y-0.5">

            {/* --- HEADER CORNER --- */}
            <div className={`absolute top-6 left-6 flex flex-col items-center leading-none select-none ${color} z-40 opacity-50`}>
                <span className="font-serif font-bold text-2xl" style={{ fontFamily: 'Georgia, serif' }}>{rank}</span>
                <span className="text-xl leading-none mt-1">{suit}</span>
            </div>

            {/* Content Area */}
            <div className="flex-1 p-10 pt-12 z-30 flex flex-col relative overflow-hidden">
                {children}
            </div>
        </div>
    </div>
);

// --- Draft Input Component (Isolated State) ---
const DraftInput = ({ onAnalyze, isAnalyzing }) => {
    const [localText, setLocalText] = useState("Should I quit my job to start a business?");

    return (
        <CardStack suit="♣" rank="J" color="text-slate-700">
            <div className="border-b border-slate-200 pb-4 mb-6 ml-8">
                <h3 className="font-playfair font-bold text-3xl text-slate-800 tracking-tight">The Draft</h3>
                <p className="text-slate-500 text-sm font-serif mt-1">Place your text on the table.</p>
            </div>

            <textarea
                className="flex-1 w-full bg-transparent border-none focus:ring-0 text-slate-800 text-xl font-playfair leading-relaxed resize-none placeholder-slate-300 outline-none px-2"
                placeholder="Type your cards here..."
                value={localText}
                onChange={(e) => setLocalText(e.target.value)}
            />

            <div className="mt-4 pt-8 border-t border-transparent flex justify-center pb-2">
                <button
                    onClick={() => onAnalyze(localText)}
                    disabled={isAnalyzing || !localText.trim()}
                    className="px-8 py-3 bg-[#1a2e22] hover:bg-[#264030] text-[#fdfbf7] rounded-full font-cinzel font-bold tracking-[0.1em] text-xs transition-all shadow-xl hover:-translate-y-1 disabled:opacity-50 disabled:translate-y-0"
                >
                    {isAnalyzing ? 'SHUFFLING...' : 'DEAL CARDS'}
                </button>
            </div>
        </CardStack>
    );
};

// --- Shuffle Deck Animation Component ---
const ShuffleDeck = () => (
    <div className="relative w-full h-full flex items-center justify-center">
        <div className="absolute w-48 h-72 bg-white rounded-xl border border-slate-300 shadow-2xl" style={{ animation: 'shuffle-left 1s infinite ease-in-out' }}></div>
        <div className="absolute w-48 h-72 bg-white rounded-xl border border-slate-300 shadow-2xl" style={{ animation: 'shuffle-right 1s infinite ease-in-out' }}></div>
        <div className="absolute w-48 h-72 bg-[#1a2e22] rounded-xl border border-slate-600 shadow-2xl flex items-center justify-center z-20" style={{ animation: 'shuffle-center 1s infinite ease-in-out' }}>
            <span className="text-white font-cinzel font-bold text-2xl animate-pulse">SHUFFLING</span>
        </div>
    </div>
);

export default function App() {
    // --- State ---
    const [inputText, setInputText] = useState("Should I quit my job to start a business?");
    const [status, setStatus] = useState('idle');
    const [pendingResponse, setPendingResponse] = useState(null);
    const [finalOutput, setFinalOutput] = useState(null);
    const [showToneSelector, setShowToneSelector] = useState(false);

    // "The Brain" State
    const [emotions, setEmotions] = useState({ current: 'Neutral', intensity: 0.1 });
    const [preferences, setPreferences] = useState([]);
    const [patterns, setPatterns] = useState([]);
    const [facts, setFacts] = useState([]);
    const [analysisLog, setAnalysisLog] = useState([]);
    const [stats, setStats] = useState({ anxiety: 0, paralysis: 0, optimism: 0, stress: 0 });
    const [selectedTone, setSelectedTone] = useState('mentor');

    // Raw vs Persona toggle
    const [showRawReply, setShowRawReply] = useState(false);
    const [neutralReply, setNeutralReply] = useState("");

    // Sidebar visibility
    const [sidebarOpen, setSidebarOpen] = useState(false);

    // --- Logic ---

    // Helper to render markdown bold syntax
    const renderMarkdown = (text) => {
        if (!text) return '';
        // Convert **text** to <strong>text</strong>
        const withBold = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        return withBold;
    };

    // Fetch memory on mount
    useEffect(() => {
        axios.get('/api/memory')
            .then(res => {
                const formatItems = (items) => items.map((item, i) => ({
                    id: Date.now() + i + Math.random(),
                    text: item.content,
                    confidence: item.confidence === 'high' ? 0.9 : 0.7
                }));

                if (res.data.preferences?.length > 0) {
                    setPreferences(formatItems(res.data.preferences).slice(0, 5));
                }
                if (res.data.patterns?.length > 0) {
                    setPatterns(formatItems(res.data.patterns).slice(0, 5));
                }
                if (res.data.facts?.length > 0) {
                    setFacts(formatItems(res.data.facts).slice(0, 5));
                }
                if (res.data.stats) {
                    setStats(res.data.stats);
                }
            })
            .catch(err => console.error("Failed to load memory", err));
    }, []);

    const analyzeInput = async (textToAnalyze) => {
        setInputText(textToAnalyze);
        if (!textToAnalyze.trim()) return;
        setStatus('analyzing');
        setShowToneSelector(false);
        setFinalOutput(null);
        setNeutralReply("");
        setShowRawReply(false);

        try {
            // 1. Analyze Emotion
            const emotionRes = await axios.post('/api/emotion/analyze', {
                text: textToAnalyze
            });
            const emotionData = emotionRes.data;

            // 2. Extract Memory - now categorized
            axios.post('/api/memory/extract', {
                messages: [textToAnalyze]
            }).then(res => {
                const formatItems = (items) => items.map((item, i) => ({
                    id: Date.now() + i + Math.random(),
                    text: item.content,
                    confidence: item.confidence === 'high' ? 0.9 : 0.7
                }));

                if (res.data.preferences?.length > 0) {
                    setPreferences(prev => [...formatItems(res.data.preferences), ...prev].slice(0, 5));
                }
                if (res.data.patterns?.length > 0) {
                    setPatterns(prev => [...formatItems(res.data.patterns), ...prev].slice(0, 5));
                }
                if (res.data.facts?.length > 0) {
                    setFacts(prev => [...formatItems(res.data.facts), ...prev].slice(0, 5));
                }
                if (res.data.stats) {
                    setStats(res.data.stats);
                }
            }).catch(err => console.error("Memory extraction failed", err));

            // Determine suggested tone based on emotion
            let suggestedTone = 'mentor';
            let reasoning = "Standard flow.";

            const state = emotionData.state.toLowerCase();
            if (state === 'stressed' || state === 'fear') {
                suggestedTone = 'mentor';
                reasoning = "Detected stress/anxiety. Suggesting stable guidance.";
            } else if (state === 'sadness' || state === 'grief') {
                suggestedTone = 'therapist';
                reasoning = "Detected sadness. Suggesting empathetic support.";
            } else if (state === 'excited' || state === 'joy') {
                suggestedTone = 'hype';
                reasoning = "Detected excitement. Suggesting high energy.";
            } else {
                suggestedTone = 'witty';
                reasoning = "Neutral state. Suggesting casual conversation.";
            }

            setEmotions({
                current: emotionData.state,
                intensity: emotionData.confidence
            });

            setPendingResponse({
                triggerText: textToAnalyze,
                emotion: emotionData.state,
                suggestedTone: suggestedTone,
                reasoning: reasoning
            });

            setSelectedTone(suggestedTone);
            setStatus('review');

            setAnalysisLog(prev => [{
                time: new Date().toLocaleTimeString(),
                trigger: "Analysis",
                decision: `Emotion: ${emotionData.state}`
            }, ...prev]);

        } catch (error) {
            console.error("Analysis failed:", error);
            setStatus('idle');
            alert("Failed to connect to the brain.");
        }
    };

    const confirmResponse = async (toneOverride = null) => {
        const toneToUse = toneOverride || selectedTone;
        const backendPersona = TONE_MAPPING[toneToUse] || 'calm_mentor';

        setStatus('generating');

        try {
            const chatRes = await axios.post('/api/chat', {
                message: inputText,
                requested_persona: backendPersona
            });

            const data = chatRes.data;

            // Capture neutral reply for Raw vs Persona toggle
            setNeutralReply(data.neutral_reply || "");

            setFinalOutput({
                tone: toneToUse,
                content: data.reply,
                variants: {}
            });

            setStatus('result');

            setAnalysisLog(prev => [{
                time: new Date().toLocaleTimeString(),
                trigger: "Response",
                decision: `Persona: ${data.persona_used}`
            }, ...prev]);

        } catch (error) {
            console.error("Generation failed:", error);
            alert("Failed to generate response.");
            setStatus('review');
        }
    };

    const switchFinalTone = async (newTone) => {
        if (!finalOutput) return;
        setSelectedTone(newTone);
        await confirmResponse(newTone);
    };

    return (
        <div className="flex h-screen w-full overflow-hidden font-serif bg-[#1a2e22] text-[#fdfbf7] selection:bg-yellow-900/50">
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Roboto+Mono:wght@400;500&display=swap');
                .font-cinzel { font-family: 'Cinzel', serif; }
                .font-playfair { font-family: 'Playfair Display', serif; }
                .font-mono { font-family: 'Roboto Mono', monospace; }
                
                /* Polka Dot Texture Pattern */
                .felt-bg {
                    background-color: #1a2e22;
                    background-image: radial-gradient(#264030 15%, transparent 16%);
                    background-size: 40px 40px;
                }
                /* Shuffling Animation */
                @keyframes shuffle-left {
                    0%, 100% { transform: translateX(0) rotate(-5deg); z-index: 1; }
                    50% { transform: translateX(-60px) rotate(-15deg); z-index: 1; }
                    51% { z-index: 10; }
                }
                @keyframes shuffle-right {
                    0%, 100% { transform: translateX(0) rotate(5deg); z-index: 1; }
                    50% { transform: translateX(60px) rotate(15deg); z-index: 1; }
                    51% { z-index: 10; }
                }
                @keyframes shuffle-center {
                    0%, 100% { transform: translateY(0); z-index: 5; }
                    50% { transform: translateY(-20px); z-index: 5; }
                }
            `}</style>

            {/* --- SIDEBAR TOGGLE BUTTON --- */}
            {!sidebarOpen && (
                <button
                    onClick={() => setSidebarOpen(true)}
                    className="fixed left-4 top-4 z-[100] bg-yellow-500 hover:bg-yellow-400 text-black font-bold px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 transition-all duration-300 hover:scale-105 xl:hidden"
                >
                    <Menu size={20} />
                    <span className="font-cinzel tracking-wider text-sm">STATS</span>
                </button>
            )}

            {/* --- LEFT PANEL: THE DEALER (Memory & Stats) --- */}
            <div className={`fixed xl:relative left-0 top-0 h-full w-72 flex-shrink-0 border-r border-[#3a5a45] bg-[#14241b]/95 font-sans backdrop-blur-sm flex flex-col shadow-2xl z-[90] transition-transform duration-300 ease-in-out ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} xl:translate-x-0`}>
                <div className="p-6 border-b border-[#3a5a45] flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded bg-yellow-600/20 border border-yellow-600 flex items-center justify-center text-yellow-500">
                            <Spade size={16} fill="currentColor" />
                        </div>
                        <div>
                            <h2 className="font-cinzel font-bold text-lg tracking-wider text-yellow-500">The Dealer</h2>
                            <p className="text-sm text-slate-400 font-mono tracking-widest uppercase">Memory Engine</p>
                        </div>
                    </div>

                    <button onClick={() => setSidebarOpen(false)} className="xl:hidden w-12 h-12 rounded-full bg-red-600 hover:bg-red-500 border-2 border-red-400 flex items-center justify-center text-white shadow-lg transition-all duration-300 hover:scale-110 hover:rotate-90" title="Minimize">
                        <X size={28} strokeWidth={3} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-5">
                    {/* Emotion / Table Read */}
                    <div className="space-y-2">
                        <h3 className="text-base font-bold uppercase tracking-widest text-[#5d8c70] flex items-center gap-2">
                            <Activity size={12} /> Table Read
                        </h3>
                        <div className="bg-[#1e3326] p-3 rounded border border-[#3a5a45]">
                            <div className="flex justify-between items-center mb-1">
                                <span className="text-sm text-slate-300">State</span>
                                <span className="text-yellow-400 font-cinzel font-bold">{emotions.current}</span>
                            </div>
                            <div className="w-full bg-[#14241b] h-1.5 rounded-full overflow-hidden">
                                <div className="bg-yellow-500 h-full transition-all duration-500" style={{ width: `${emotions.intensity * 100}%` }}></div>
                            </div>
                        </div>
                    </div>

                    {/* Preferences */}
                    <div className="space-y-2">
                        <h3 className="text-base font-bold uppercase tracking-widest text-[#5d8c70] flex items-center gap-2">
                            <Heart size={12} /> Player Tells
                        </h3>
                        {preferences.length === 0 ? (
                            <p className="text-sm text-slate-400">No tells detected yet...</p>
                        ) : (
                            <ul className="space-y-2">
                                {preferences.map(p => (
                                    <li key={p.id} className="text-sm bg-[#1e3326] p-3 rounded border border-[#3a5a45] text-slate-200 flex items-start gap-2 leading-relaxed">
                                        <span className="text-yellow-500 mt-0.5">•</span>
                                        {p.text}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Emotional Patterns */}
                    <div className="space-y-2">
                        <h3 className="text-base font-bold uppercase tracking-widest text-[#5d8c70] flex items-center gap-2">
                            <Activity size={12} /> Emotional Patterns
                        </h3>
                        <div className="bg-[#1e3326] p-4 rounded border border-[#3a5a45]">
                            <div className="flex items-end justify-between h-24 gap-2">
                                {/* Anxiety - Blue */}
                                <div className="flex flex-col items-center gap-1 flex-1 group">
                                    <div className="w-full bg-blue-900/30 rounded-t relative h-full flex items-end overflow-hidden">
                                        <div className="w-full bg-blue-600 transition-all duration-500" style={{ height: `${Math.max(15, stats.anxiety)}%` }}></div>
                                    </div>
                                    <span className="text-[10px] text-slate-400 uppercase tracking-wider group-hover:text-blue-400">Anx</span>
                                </div>
                                {/* Paralysis - Purple */}
                                <div className="flex flex-col items-center gap-1 flex-1 group">
                                    <div className="w-full bg-purple-900/30 rounded-t relative h-full flex items-end overflow-hidden">
                                        <div className="w-full bg-purple-600 transition-all duration-500" style={{ height: `${Math.max(10, stats.paralysis)}%` }}></div>
                                    </div>
                                    <span className="text-[10px] text-slate-400 uppercase tracking-wider group-hover:text-purple-400">Par</span>
                                </div>
                                {/* Optimism - Green */}
                                <div className="flex flex-col items-center gap-1 flex-1 group">
                                    <div className="w-full bg-green-900/30 rounded-t relative h-full flex items-end overflow-hidden">
                                        <div className="w-full bg-green-600 transition-all duration-500" style={{ height: `${Math.max(40, stats.optimism)}%` }}></div>
                                    </div>
                                    <span className="text-[10px] text-slate-400 uppercase tracking-wider group-hover:text-green-400">Opt</span>
                                </div>
                                {/* Stress - Yellow */}
                                <div className="flex flex-col items-center gap-1 flex-1 group">
                                    <div className="w-full bg-yellow-900/30 rounded-t relative h-full flex items-end overflow-hidden">
                                        <div className="w-full bg-yellow-600 transition-all duration-500" style={{ height: `${Math.max(25, stats.stress)}%` }}></div>
                                    </div>
                                    <span className="text-[10px] text-slate-400 uppercase tracking-wider group-hover:text-yellow-400">Str</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Extracted Facts */}
                    <div className="space-y-2">
                        <h3 className="text-base font-bold uppercase tracking-widest text-[#5d8c70] flex items-center gap-2">
                            <BookOpen size={12} /> Extracted Facts
                        </h3>
                        {facts.length === 0 ? (
                            <p className="text-sm text-slate-400">No facts yet...</p>
                        ) : (
                            <ul className="space-y-2">
                                {facts.map(f => (
                                    <li key={f.id} className="text-sm bg-[#1e3326] p-3 rounded border border-[#3a5a45] text-slate-200 flex items-start gap-2 leading-relaxed">
                                        <span className="text-blue-500 mt-0.5">•</span>
                                        {f.text}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    {/* Hand Log */}
                    <div className="space-y-2">
                        <h3 className="text-base font-bold uppercase tracking-widest text-[#5d8c70] flex items-center gap-2">
                            <History size={12} /> Hand Log
                        </h3>
                        <div className="text-sm text-slate-400">
                            No history available.
                        </div>
                    </div>
                </div>
            </div>

            {/* --- MAIN TABLE AREA --- */}
            <div className="flex-1 flex flex-col relative felt-bg">
                {/* Header */}
                <header className="h-20 flex items-center justify-between px-8 border-b border-[#3a5a45] bg-[#1a2e22]/90 backdrop-blur-md z-50">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-yellow-500 rounded-full flex items-center justify-center shadow-lg shadow-yellow-500/20">
                            <Brain className="text-[#1a2e22]" size={24} />
                        </div>
                        <div className="flex flex-col">
                            <h1 className="font-cinzel font-bold text-2xl tracking-[0.15em] text-yellow-500 leading-none">
                                KOKO
                            </h1>
                            <p className="text-sm text-yellow-500/85 tracking-[0.15em] font-cinzel uppercase mt-1">
                                The Personality Engine
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <div className="px-3 py-1 rounded-full bg-[#14241b] border border-[#3a5a45] text-xs text-slate-400 flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                            System Online
                        </div>
                    </div>
                </header>

                {/* Main Content Grid */}
                {/* Personality Engine Pill */}
                <div className="absolute top-6 left-1/2 -translate-x-1/2 z-40">
                    <div className="px-6 py-2 bg-[#14241b] border border-[#3a5a45] rounded-full shadow-xl flex items-center gap-3">
                        <span className="text-yellow-600">♠</span>
                        <span className="font-cinzel font-bold text-xs tracking-[0.2em] text-slate-200">PERSONALITY ENGINE</span>
                        <span className="text-red-600">♦</span>
                    </div>
                </div>

                <main className="flex-1 overflow-hidden relative flex items-center justify-center p-8">
                    <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 h-[600px]">

                        {/* LEFT: INPUT AREA */}
                        <div className="flex flex-col justify-center relative">
                            <div className="absolute -top-16 left-0 w-full flex justify-center">
                                <div className="flex items-center gap-4 text-[#8ab090]">
                                    <div className="h-[1px] w-12 bg-[#8ab090]"></div>
                                    <span className="font-cinzel font-bold text-xs tracking-[0.2em]">YOUR HAND</span>
                                    <div className="h-[1px] w-12 bg-[#8ab090]"></div>
                                </div>
                            </div>
                            <DraftInput onAnalyze={analyzeInput} isAnalyzing={status === 'analyzing'} />
                        </div>

                        {/* RIGHT: OUTPUT AREA */}
                        <div className="flex flex-col justify-center relative">
                            <div className="absolute -top-16 left-0 w-full flex justify-center">
                                <div className="flex items-center gap-4 text-[#8ab090]">
                                    <div className="h-[1px] w-12 bg-[#8ab090]"></div>
                                    <span className="font-cinzel font-bold text-xs tracking-[0.2em]">THE REVEAL</span>
                                    <div className="h-[1px] w-12 bg-[#8ab090]"></div>
                                </div>
                            </div>
                            {status === 'idle' && (
                                <div className="w-full h-full rounded-[1rem] border-2 border-dashed border-[#3a5a45] bg-[#14241b]/50 flex flex-col items-center justify-center relative group">
                                    <div className="w-24 h-32 border border-[#3a5a45] rounded opacity-20 flex items-center justify-center mb-4">
                                        <span className="text-4xl text-[#3a5a45]">?</span>
                                    </div>
                                    <p className="font-cinzel tracking-[0.2em] text-[#3a5a45] text-sm font-bold">WAITING FOR DEAL</p>
                                </div>
                            )}

                            {status === 'analyzing' && (
                                <ShuffleDeck />
                            )}

                            {status === 'review' && pendingResponse && (
                                <CardStack
                                    suit={TONES[pendingResponse.suggestedTone.toUpperCase()]?.suit}
                                    rank={TONES[pendingResponse.suggestedTone.toUpperCase()]?.rank}
                                    color={TONES[pendingResponse.suggestedTone.toUpperCase()]?.color}
                                >
                                    <div className="border-b border-slate-200 pb-4 mb-6 ml-8">
                                        <h3 className="font-playfair font-bold text-3xl text-slate-800 tracking-tight">The Read</h3>
                                        <p className="text-slate-500 text-sm font-serif mt-1">I've analyzed your hand.</p>
                                    </div>

                                    <div className="space-y-6">
                                        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Activity size={16} className="text-slate-400" />
                                                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Detected Emotion</span>
                                            </div>
                                            <p className="text-lg font-playfair text-slate-800 capitalize">{pendingResponse.emotion}</p>
                                        </div>

                                        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                                            <div className="flex items-center gap-2 mb-2">
                                                <Sparkles size={16} className="text-yellow-600" />
                                                <span className="text-xs font-bold uppercase tracking-wider text-yellow-700">Suggested Approach</span>
                                            </div>
                                            <p className="text-lg font-playfair text-slate-800">{pendingResponse.reasoning}</p>
                                        </div>

                                        <div className="pt-4">
                                            <button
                                                onClick={() => confirmResponse()}
                                                className="w-full py-4 bg-[#1a2e22] hover:bg-[#264030] text-[#fdfbf7] rounded-xl font-cinzel font-bold tracking-widest shadow-xl hover:-translate-y-1 transition-all flex items-center justify-center gap-3"
                                            >
                                                <span>REVEAL THE CARD</span>
                                                <ArrowRight size={18} />
                                            </button>
                                        </div>
                                    </div>
                                </CardStack>
                            )}

                            {(status === 'generating' || status === 'result') && finalOutput && (
                                <CardStack
                                    suit={TONES[finalOutput.tone.toUpperCase()]?.suit}
                                    rank={TONES[finalOutput.tone.toUpperCase()]?.rank}
                                    color={TONES[finalOutput.tone.toUpperCase()]?.color}
                                >
                                    <div className="border-b border-slate-200 pb-4 mb-6 ml-8 flex justify-between items-end">
                                        <div>
                                            <h3 className="font-playfair font-bold text-3xl text-slate-800 tracking-tight">{TONES[finalOutput.tone.toUpperCase()]?.label}</h3>
                                            <p className="text-slate-500 text-sm font-serif mt-1">Your companion's response.</p>
                                        </div>
                                        <div className="flex gap-2">
                                            <button
                                                onClick={() => setShowRawReply(!showRawReply)}
                                                className="text-xs uppercase tracking-wider font-bold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 px-4 py-2 rounded transition-all shadow-sm hover:shadow"
                                            >
                                                {showRawReply ? "Show Persona" : "Show Raw"}
                                            </button>
                                        </div>
                                    </div>

                                    <div className="flex-1 prose prose-slate max-w-none font-serif text-lg leading-relaxed text-slate-700 overflow-y-auto pr-2 custom-scrollbar">
                                        {showRawReply ? (
                                            <div className="opacity-70 italic border-l-2 border-slate-300 pl-4">
                                                {neutralReply}
                                            </div>
                                        ) : (
                                            <div dangerouslySetInnerHTML={{ __html: renderMarkdown(finalOutput.content) }} />
                                        )}
                                    </div>

                                    <div className="mt-4 pt-6 border-t border-slate-100 flex flex-col items-center gap-6 pb-2">
                                        <div className="flex gap-6 justify-center w-full">
                                            {Object.values(TONES).map(tone => (
                                                <button
                                                    key={tone.id}
                                                    onClick={() => switchFinalTone(tone.id)}
                                                    className={`w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all duration-300 shadow-sm ${selectedTone === tone.id ? 'bg-white border-slate-900 scale-110 shadow-xl ring-2 ring-slate-900 z-10' : 'bg-white border-slate-200 hover:border-slate-400 hover:scale-105'}`}
                                                    title={tone.label}
                                                >
                                                    <tone.icon size={28} className={tone.realColor} fill="currentColor" strokeWidth={1.5} />
                                                </button>
                                            ))}
                                        </div>
                                        <button
                                            onClick={() => {
                                                setStatus('idle');
                                                setInputText("");
                                            }}
                                            className="px-6 py-3 bg-[#8b0000] hover:bg-[#a00000] text-[#fdfbf7] rounded-full font-cinzel font-bold tracking-widest text-xs transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5 flex items-center gap-2"
                                        >
                                            <RotateCcw size={16} /> NEW DEAL
                                        </button>
                                    </div>
                                </CardStack>
                            )}
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}