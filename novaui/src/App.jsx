import React, { useState, useRef, useEffect } from 'react';
import { Send, Plus, FileText, Cpu, BookOpen, Upload, ShieldCheck, Copy, Check, Menu } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState("agent");
  const [documents, setDocuments] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [copiedStates, setCopiedStates] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchDocs();
  }, []);

  useEffect(() => {
    const onResize = () => {
      const mobile = window.innerWidth < 980;
      setIsMobile(mobile);
      setSidebarOpen(!mobile);
    };

    onResize();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const fetchDocs = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/docs");
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch (err) {
      console.error("Failed to fetch documents", err);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, mode: mode })
      });
      const data = await res.json();
      
      // Robust LaTeX and math block normalization for KaTeX & ReactMarkdown
      let cleanedResponse = data.response
        .replace(/\\\[/g, '$$')
        .replace(/\\\]/g, '$$')
        .replace(/\\\(/g, '$')
        .replace(/\\\)/g, '$');

      setMessages(prev => [...prev, { role: 'assistant', content: cleanedResponse }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Connection error: Failed to reach NOVA backend, Sir." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        alert(`Successfully indexed ${data.filename} (${data.chunks} chunks)!`);
        fetchDocs();
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      alert("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    try {
      await fetch("http://127.0.0.1:8000/api/clear", { method: "POST" });
      setMessages([]);
    } catch (err) {
      console.error("Failed to clear memory");
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [id]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [id]: false }));
    }, 2000);
  };

  const ui = {
    fontFamily: "-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'SF Pro Display', 'Helvetica Neue', sans-serif",
    black: '#000000',
    panel: '#0a0a0a',
    surface: '#111111',
    surfaceAlt: '#151515',
    border: '#202020',
    text: '#f5f5f7',
    muted: '#a1a1aa',
    accent: '#0a84ff',
    accentSoft: '#112136',
    success: '#32d74b'
  };

  const makeCodeId = (messageIndex, codeString) => {
    return `code-${messageIndex}-${codeString.length}-${codeString.slice(0, 16)}`;
  };

  return (
    <div style={{
      display: 'flex',
      height: '100vh',
      backgroundColor: ui.black,
      color: ui.text,
      overflow: 'hidden',
      fontFamily: ui.fontFamily,
      letterSpacing: '-0.01em'
    }}>

      {isMobile && sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.55)',
            zIndex: 19
          }}
        />
      )}
      
      {/* SIDEBAR */}
      <div style={{ 
        width: isMobile ? '82vw' : '280px',
        maxWidth: isMobile ? '320px' : 'none',
        backgroundColor: ui.panel,
        display: 'flex', 
        flexDirection: 'column', 
        justifyContent: 'space-between', 
        borderRight: `1px solid ${ui.border}`,
        padding: '16px',
        position: isMobile ? 'fixed' : 'relative',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 20,
        transform: isMobile && !sidebarOpen ? 'translateX(-100%)' : 'translateX(0)',
        transition: 'transform 0.22s ease'
      }}>
        <div>
          <button 
            onClick={handleNewChat}
            style={{ 
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              background: ui.surface,
              border: `1px solid ${ui.border}`,
              color: ui.text,
              cursor: 'pointer',
              padding: '12px 16px',
              borderRadius: '12px',
              width: '100%',
              fontSize: '14px',
              fontWeight: '600',
              marginBottom: '24px'
            }}
          >
            <Plus size={17} style={{ color: ui.accent }} />
            <span>New Chat</span>
          </button>

          <div style={{ marginBottom: '28px' }}>
            <p style={{
              fontSize: '11px',
              fontWeight: '600',
              color: ui.muted,
              paddingLeft: '4px',
              marginBottom: '10px',
              textTransform: 'uppercase',
              letterSpacing: '0.08em'
            }}>
              Operation Mode
            </p>
            <button 
              onClick={() => setMode("agent")}
              style={{ 
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '11px 12px',
                borderRadius: '10px',
                fontSize: '13px',
                fontWeight: '600',
                border: `1px solid ${mode === 'agent' ? '#1f3854' : ui.border}`,
                cursor: 'pointer',
                background: mode === 'agent' ? ui.accentSoft : 'transparent',
                color: mode === 'agent' ? '#cbe5ff' : '#d4d4d8',
                marginBottom: '4px'
              }}
            >
              <Cpu size={16} />
              <span>AI Chat Agent</span>
            </button>
            <button 
              onClick={() => setMode("pure_rag")}
              style={{ 
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                width: '100%',
                padding: '11px 12px',
                borderRadius: '10px',
                fontSize: '13px',
                fontWeight: '600',
                border: `1px solid ${mode === 'pure_rag' ? '#1f3854' : ui.border}`,
                cursor: 'pointer',
                background: mode === 'pure_rag' ? ui.accentSoft : 'transparent',
                color: mode === 'pure_rag' ? '#cbe5ff' : '#d4d4d8'
              }}
            >
              <BookOpen size={16} />
              <span>Pure Document RAG</span>
            </button>
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
              <span style={{ fontSize: '11px', fontWeight: '600', color: ui.muted, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Loaded Files
              </span>
              <label style={{ cursor: 'pointer', color: ui.accent, display: 'flex', alignItems: 'center' }} title="Upload File">
                <Upload size={16} />
                <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} accept=".pdf,.txt,.md" />
              </label>
            </div>
            <div style={{ maxHeight: '220px', overflowY: 'auto', paddingRight: '2px' }}>
              {documents.map((doc, idx) => (
                <div key={idx} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '9px 10px',
                  borderRadius: '10px',
                  background: ui.surface,
                  border: `1px solid ${ui.border}`,
                  fontSize: '12px',
                  marginBottom: '6px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                  color: '#d4d4d8'
                }}>
                  <FileText size={13} style={{ color: ui.accent, flexShrink: 0 }} />
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{doc.name}</span>
                </div>
              ))}
              {documents.length === 0 && (
                <p style={{ fontSize: '12px', color: '#71717a', paddingLeft: '2px', fontStyle: 'italic' }}>No files loaded yet.</p>
              )}
            </div>
          </div>
        </div>

        <div style={{ borderTop: `1px solid ${ui.border}`, paddingTop: '14px', display: 'flex', alignItems: 'center', gap: '10px', paddingLeft: '2px' }}>
          <div style={{
            width: '34px',
            height: '34px',
            borderRadius: '50%',
            background: '#0f1724',
            border: '1px solid #1d2b3f',
            display: 'flex',
            alignItems: 'center',
            fontWeight: '700',
            fontSize: '12px',
            justifyContent: 'center',
            color: '#dbeafe',
            flexShrink: 0
          }}>SN</div>
          <div style={{ overflow: 'hidden' }}>
            <p style={{ fontSize: '13px', fontWeight: '600', margin: 0, color: ui.text }}>Mr. Sandaru</p>
            <p style={{ fontSize: '10px', color: ui.muted, margin: 0, display: 'flex', alignItems: 'center', gap: '4px' }}><ShieldCheck size={10} style={{ color: ui.success }}/> NOVA Master</p>
          </div>
        </div>
      </div>

      {/* MAIN CHAT AREA */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between', backgroundColor: ui.black }}>
        
        <div style={{
          minHeight: '62px',
          borderBottom: `1px solid ${ui.border}`,
          display: 'flex',
          alignItems: 'center',
          padding: '0 28px',
          justifyContent: 'space-between',
          backgroundColor: ui.black
        }}>
          <h1 style={{ fontSize: '17px', fontWeight: '600', color: ui.text, margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
            {isMobile && (
              <button
                onClick={() => setSidebarOpen(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '30px',
                  height: '30px',
                  borderRadius: '8px',
                  border: `1px solid ${ui.border}`,
                  background: ui.surface,
                  color: ui.text,
                  cursor: 'pointer'
                }}
                aria-label="Open menu"
              >
                <Menu size={16} />
              </button>
            )}
            <span>NOVA AI</span>
            <span style={{
              fontSize: '11px',
              background: '#0f1724',
              color: '#bfdbfe',
              padding: '3px 9px',
              borderRadius: '999px',
              border: '1px solid #1d2b3f',
              fontWeight: '600'
            }}>Secured Copilot</span>
          </h1>
          <span style={{ fontSize: '12px', color: ui.muted, display: isMobile ? 'none' : 'inline' }}>
            Mode: <strong style={{ color: '#e4e4e7', fontWeight: '600' }}>{mode === 'agent' ? 'AI Chat Agent' : 'Pure Document RAG'}</strong>
          </span>
        </div>

        {/* Chat Messages */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '32px 22px',
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          maxWidth: '920px',
          width: '100%',
          margin: '0 auto'
        }}>
          {messages.length === 0 && (
            <div style={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              textAlign: 'center',
              color: ui.muted,
              padding: '0 16px'
            }}>
              <div style={{
                width: '62px',
                height: '62px',
                borderRadius: '18px',
                background: ui.surface,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '16px',
                color: ui.accent,
                fontWeight: '700',
                fontSize: '23px',
                border: `1px solid ${ui.border}`
              }}>N</div>
              <h2 style={{ fontSize: '28px', fontWeight: '600', color: ui.text, marginBottom: '10px', margin: 0 }}>How can I help today, Sir?</h2>
              <p style={{ fontSize: '14px', maxWidth: '460px', color: ui.muted, margin: 0 }}>Ask engineering questions, execute precision math, or upload files for grounded answers.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} style={{
              display: 'flex',
              gap: '14px',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              width: '100%'
            }}>
              {msg.role === 'assistant' && (
                <div style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  background: ui.surface,
                  border: `1px solid ${ui.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: ui.accent,
                  fontWeight: '700',
                  fontSize: '12px',
                  flexShrink: 0,
                  marginTop: '2px'
                }}>N</div>
              )}
              
              <div style={{ 
                padding: '18px 20px',
                borderRadius: '16px',
                maxWidth: '780px',
                width: '100%',
                fontSize: '14px',
                lineHeight: '1.7',
                background: msg.role === 'user' ? ui.surfaceAlt : ui.surface,
                border: `1px solid ${ui.border}`,
                color: ui.text,
                boxShadow: msg.role === 'user' ? 'none' : '0 4px 20px rgba(0,0,0,0.25)',
                borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px'
              }}>
                <ReactMarkdown 
                  remarkPlugins={[remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    code({node, inline, className, children, ...props}) {
                      const match = /language-(\w+)/.exec(className || '');
                      const codeString = String(children).replace(/\n$/, '');
                      const codeId = makeCodeId(index, codeString);
                      const isCopied = copiedStates[codeId];

                      if (!inline && match) {
                        return (
                          <div style={{ margin: '16px 0', borderRadius: '12px', overflow: 'hidden', border: `1px solid ${ui.border}`, background: ui.black }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#191919', padding: '10px 16px', fontSize: '12px', color: ui.muted }}>
                              <span style={{ textTransform: 'uppercase', fontWeight: '600', letterSpacing: '0.5px' }}>{match[1]}</span>
                              <button 
                                onClick={() => copyToClipboard(codeString, codeId)}
                                style={{ background: 'transparent', border: 'none', color: isCopied ? ui.success : ui.muted, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', padding: '4px 8px', borderRadius: '6px', transition: 'all 0.2s' }}
                              >
                                {isCopied ? <Check size={14} style={{ color: ui.success }} /> : <Copy size={14} />}
                                {isCopied ? 'Copied!' : 'Copy code'}
                              </button>
                            </div>
                            <SyntaxHighlighter
                              language={match[1]}
                              style={vscDarkPlus}
                              customStyle={{ margin: 0, padding: '16px', background: '#080808', fontSize: '13px' }}
                            >
                              {codeString}
                            </SyntaxHighlighter>
                          </div>
                        );
                      }
                      return (
                        <code {...props} style={{ background: '#1b1b1b', padding: '2px 6px', borderRadius: '5px', fontSize: '13px', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }} className={className}>
                          {children}
                        </code>
                      );
                    }
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              </div>

              {msg.role === 'user' && (
                <div style={{
                  width: '34px',
                  height: '34px',
                  borderRadius: '50%',
                  background: '#1a73e8',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontWeight: '700',
                  fontSize: '12px',
                  flexShrink: 0,
                  marginTop: '2px'
                }}>SN</div>
              )}
            </div>
          ))}

          {loading && (
            <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
              <div style={{ width: '34px', height: '34px', borderRadius: '50%', background: ui.surface, border: `1px solid ${ui.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', color: ui.accent, fontWeight: '700', fontSize: '12px' }}>N</div>
              <div style={{ fontSize: '13px', color: ui.muted, fontStyle: 'italic' }}>NOVA is thinking...</div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div style={{ padding: '16px 24px 26px 24px', backgroundColor: ui.black, borderTop: `1px solid ${ui.border}` }}>
          <form onSubmit={handleSend} style={{ maxWidth: '920px', margin: '0 auto', position: 'relative', display: 'flex', alignItems: 'center' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask anything or query loaded documents, Sir..."
              style={{
                width: '100%',
                backgroundColor: ui.surface,
                border: `1px solid ${ui.border}`,
                borderRadius: '16px',
                padding: '16px 56px 16px 20px',
                fontSize: '14px',
                color: ui.text,
                outline: 'none',
                boxShadow: '0 8px 28px rgba(0,0,0,0.35)'
              }}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              style={{
                position: 'absolute',
                right: '12px',
                background: ui.accent,
                border: 'none',
                borderRadius: '10px',
                width: '36px',
                height: '36px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                cursor: 'pointer',
                opacity: (loading || !input.trim()) ? 0.45 : 1
              }}
            >
              <Send size={16} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}