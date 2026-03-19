"use client";
import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

type Msg = {
    role: "user" | "ai";
    text: string;
    resumeUrl?: string | null;
};

function TypingIndicator() {
    return (
        <div className="flex justify-start">
            <div className="px-4 py-3 rounded-2xl">
                <div className="flex items-center gap-1.5">
                    {[0, 1, 2].map((i) => (
                        <span
                            key={i}
                            className="w-1.5 h-1.5 rounded-full bg-[#262626] opacity-40"
                            style={{
                                animation: "typing-bounce 1.2s ease-in-out infinite",
                                animationDelay: `${i * 0.2}s`,
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );
}

export default function ChatBox() {
    const bottomRef = useRef<HTMLDivElement | null>(null);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Msg[]>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);

    const exampleQuestions = [
        "Tell me about yourself",
        "Give resume link",
        "List Pridhu's experience",
    ];
    const inputRef = useRef<HTMLInputElement>(null);
    const hasMessages = messages.length > 0;
    const isBusy = isTyping || isStreaming;

    async function send() {
        if (!input.trim() || isBusy) return;

        const userText = input;
        setInput("");
        setMessages((m) => [...m, { role: "user", text: userText }]);
        setIsTyping(true);

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userText }),
            });

            if (!res.ok || !res.body) {
                setMessages((m) => [...m, { role: "ai", text: "Something went wrong. Please try again." }]);
                return;
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let firstToken = true;
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() ?? "";

                for (const line of lines) {
                    if (!line.startsWith("data: ")) continue;
                    const jsonStr = line.slice(6).trim();
                    if (!jsonStr) continue;

                    let parsed: Record<string, unknown>;
                    try { parsed = JSON.parse(jsonStr); } catch { continue; }

                    // Error from backend
                    if (parsed.error) {
                        setMessages((m) => [...m, { role: "ai", text: String(parsed.error) }]);
                        setIsTyping(false);
                        setIsStreaming(false);
                        return;
                    }

                    // Streaming token
                    if (typeof parsed.token === "string" && parsed.token.length > 0) {
                        if (firstToken) {
                            firstToken = false;
                            setIsTyping(false);
                            setIsStreaming(true);
                            // Create the AI message slot with first token
                            setMessages((m) => [...m, { role: "ai", text: parsed.token as string }]);
                        } else {
                            // Safe: always append to the last message
                            setMessages((prev) => {
                                const copy = [...prev];
                                const last = copy[copy.length - 1];
                                if (last && last.role === "ai") {
                                    copy[copy.length - 1] = {
                                        ...last,
                                        text: last.text + (parsed.token as string),
                                    };
                                }
                                return copy;
                            });
                        }
                    }

                    // Stream finished
                    if (parsed.done === true) {
                        const resumeUrl = (parsed.resume_url as string | null) ?? null;
                        if (resumeUrl) {
                            setMessages((prev) => {
                                const copy = [...prev];
                                const last = copy[copy.length - 1];
                                if (last && last.role === "ai") {
                                    copy[copy.length - 1] = { ...last, resumeUrl };
                                }
                                return copy;
                            });
                        }
                        setIsStreaming(false);
                    }
                }
            }

        } catch {
            setMessages((m) => [...m, { role: "ai", text: "Connection error. Please try again." }]);
        } finally {
            setIsTyping(false);
            setIsStreaming(false);
        }
    }

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isTyping]);

    return (
        <>
            <style>{`
                @keyframes typing-bounce {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                    30%           { transform: translateY(-4px); opacity: 1; }
                }
            `}</style>

            <div className={`min-h-screen w-full flex flex-col items-center px-4 ${hasMessages ? "justify-start" : "justify-center"}`}>

                <h1 className={`
                    w-full max-w-3xl fixed left-1/2 -translate-x-1/2
                    text-5xl md:text-[96px] text-center font-normal text-[#262626] z-20
                    transition-all duration-500 ease-in-out px-4
                    ${hasMessages ? "top-6 md:top-18 text-left" : "top-32 md:top-44 text-left"}
                `}>
                    Hi, I'm{" "}
                    <span className="bg-linear-to-r from-red-600 via-orange-600 to-yellow-400 bg-clip-text text-transparent tracking-tight">
                        Sofy
                    </span>
                </h1>

                <div className="w-full max-w-3xl h-160 flex items-start flex-col relative">

                    {/* Messages */}
                    {hasMessages && (
                        <div className="w-full h-160 flex flex-col">
                            <div className="w-full h-[calc(100vh-220px)] md:h-85 max-w-3xl fixed bottom-40 md:bottom-60 overflow-y-auto text-sm chat-scroll pr-4">
                                {messages.map((m, i) => (
                                    <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                                        <div className="max-w-[85%] md:max-w-[75%] px-4 py-3 rounded-2xl space-y-2">
                                            <div className="prose prose-sm max-w-none text-[#262626] text-justify leading-normal">
                                                <ReactMarkdown>{m.text}</ReactMarkdown>
                                            </div>
                                            {m.role === "ai" && m.resumeUrl && (
                                                <a
                                                    href={m.resumeUrl}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-sm text-blue-600 underline inline-block"
                                                >
                                                    Download Resume (PDF)
                                                </a>
                                            )}
                                        </div>
                                    </div>
                                ))}

                                {isTyping && <TypingIndicator />}
                                <div ref={bottomRef} />
                            </div>
                        </div>
                    )}

                    {/* Example questions */}
                    {hasMessages && (
                        <div className={`
                            w-full max-w-3xl fixed left-1/2 -translate-x-1/2 z-20
                            flex justify-start flex-wrap gap-2 md:gap-3 px-4
                            transition-all duration-500 ease-in-out
                            ${hasMessages ? "bottom-24 md:bottom-40" : "hidden"}
                        `}>
                            {exampleQuestions.map((q, i) => (
                                <button
                                    key={i}
                                    onClick={() => { setInput(q); inputRef.current?.focus(); }}
                                    className="px-3 py-1.5 md:px-4 md:py-2 border rounded-full text-xs md:text-sm text-[#262626] bg-[#ECECEC] hover:bg-[#dedede] transition"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Input bar */}
                    <div className={`
                        fixed left-1/2 -translate-x-1/2 z-30
                        h-12 md:h-15 w-[90%] max-w-3xl bg-[#ECECEC] px-2 rounded-full
                        flex items-center
                        shadow-[0_24px_36px_rgba(140,140,140,.42)]
                        transition-all duration-1 ease-in-out
                        ${hasMessages ? "bottom-8 md:bottom-20" : "top-1/2 -translate-y-1/2"}
                    `}>
                        <div className="h-8 w-8 md:w-10 flex items-center justify-center">
                            <img src="/sparkle.svg" alt="Sparkle" className="w-5 h-5 md:w-6 md:h-6" />
                        </div>

                        <input
                            ref={inputRef}
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            className="h-full px-2 flex-1 bg-[#ECECEC] text-[#262626] rounded-full outline-none border-none text-sm md:text-base"
                            placeholder={isBusy ? "Sofy is typing..." : "Ask about something"}
                            onKeyDown={(e) => e.key === "Enter" && send()}
                            disabled={isBusy}
                        />

                        <button
                            onClick={send}
                            disabled={isBusy}
                            className={`h-9 md:h-13 w-20 md:w-28 text-sm md:text-base font-medium rounded-full transition-opacity
                                ${isBusy
                                    ? "bg-[#555] text-[#aaa] opacity-60 cursor-not-allowed"
                                    : "bg-[#262626] text-[#ECECEC]"
                                }`}
                        >
                            {isBusy ? "..." : "Send"}
                        </button>
                    </div>
                </div>

                <p className="fixed bottom-8 left-1/2 -translate-x-1/2 text-[12px] text-[#9C9DA4] font-medium z-10">
                    Pridhu © 2026 All rights reserved.
                </p>
            </div>
        </>
    );
}
