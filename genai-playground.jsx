import { useState, useRef, useEffect } from "react";

const TECHNIQUES = {
  zero_shot: {
    label: "Zero-Shot",
    color: "#7F77DD",
    system: "You are a helpful assistant.",
    prompt: "Explain what machine learning is in 2 sentences.",
    description: "Direct ask — no examples given."
  },
  few_shot: {
    label: "Few-Shot",
    color: "#1D9E75",
    system: "You are a customer support classifier.",
    prompt: `Classify the following feedback:

Feedback: "App crashes on startup"
Category: Bug

Feedback: "Would love multi-language support"
Category: Feature Request

Feedback: "Your team helped me so fast!"
Category: Compliment

Feedback: "The export button doesn't work on Chrome"
Category:`,
    description: "Show examples before asking."
  },
  cot: {
    label: "Chain of Thought",
    color: "#D85A30",
    system: "You are a helpful problem solver.",
    prompt: "A product was sold for ₹750 after a 25% discount. What was the original price? Think step by step.",
    description: "Ask the model to reason aloud."
  },
  role_based: {
    label: "Role-Based (RBCFC)",
    color: "#378ADD",
    system: "You are a senior product manager at a B2B SaaS company with 10 years of experience.",
    prompt: "Our dashboard load time increased from 2s to 8s after a recent deploy. Write a short incident summary for stakeholders.",
    description: "Give the model a role/persona."
  }
};

const MODELS = [
  { id: "claude-opus-4-6", label: "Claude Opus 4.6" },
  { id: "claude-sonnet-4-6", label: "Claude Sonnet 4.6" },
  { id: "claude-haiku-4-5-20251001", label: "Claude Haiku 4.5" }
];

function estimateTokens(text) {
  return Math.ceil((text || "").split(/\s+/).length * 1.33);
}

export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [keyInput, setKeyInput] = useState("");
  const [showKeyPanel, setShowKeyPanel] = useState(false);
  const [model, setModel] = useState("claude-sonnet-4-6");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(500);
  const [systemPrompt, setSystemPrompt] = useState(TECHNIQUES.zero_shot.system);
  const [userPrompt, setUserPrompt] = useState(TECHNIQUES.zero_shot.prompt);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTech, setActiveTech] = useState("zero_shot");
  const [history, setHistory] = useState([]);
  const responseRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem("genai_api_key");
    if (saved) setApiKey(saved);
  }, []);

  const saveKey = () => {
    localStorage.setItem("genai_api_key", keyInput);
    setApiKey(keyInput);
    setShowKeyPanel(false);
  };

  const loadTechnique = (key) => {
    setActiveTech(key);
    setSystemPrompt(TECHNIQUES[key].system);
    setUserPrompt(TECHNIQUES[key].prompt);
    setResponse("");
    setError("");
  };

  const callAPI = async () => {
    if (!apiKey) { setShowKeyPanel(true); return; }
    setLoading(true);
    setError("");
    setResponse("");

    try {
      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          max_tokens: maxTokens,
          temperature,
          system: systemPrompt,
          messages: [{ role: "user", content: userPrompt }]
        })
      });
      const data = await res.json();
      if (data.error) throw new Error(data.error.message);
      const text = data.content?.[0]?.text || "";
      setResponse(text);
      setHistory(h => [{
        tech: activeTech, model, temperature, prompt: userPrompt, response: text,
        time: new Date().toLocaleTimeString()
      }, ...h].slice(0, 10));
    } catch (e) {
      setError(e.message || "Something went wrong");
    }
    setLoading(false);
  };

  const inputTokens = estimateTokens(systemPrompt + " " + userPrompt);
  const outputTokens = estimateTokens(response);
  const tempLabel = temperature <= 0.3 ? "Precise" : temperature <= 0.6 ? "Balanced" : temperature <= 0.9 ? "Creative" : "Wild";

  return (
    <div style={{ fontFamily: "var(--font-sans, sans-serif)", maxWidth: 900, margin: "0 auto", padding: "1.5rem 1rem" }}>
      <h2 style={{ sr: "only", position: "absolute", opacity: 0 }}>GenAI Playground — prompt engineering tool</h2>

      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 500, color: "var(--color-text-primary)" }}>GenAI Playground</h1>
          <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--color-text-secondary)" }}>Company GenAI Training — Sessions 1–3</p>
        </div>
        <button onClick={() => setShowKeyPanel(v => !v)} style={{ fontSize: 13, display: "flex", alignItems: "center", gap: 6, padding: "6px 12px" }}>
          <i className="ti ti-key" aria-hidden="true" style={{ fontSize: 15 }}></i>
          {apiKey ? "Key saved ✓" : "Add API Key"}
        </button>
      </div>

      {/* Key Panel */}
      {showKeyPanel && (
        <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-lg)", border: "0.5px solid var(--color-border-tertiary)", padding: "1rem 1.25rem", marginBottom: "1.25rem" }}>
          <p style={{ margin: "0 0 8px", fontSize: 13, fontWeight: 500 }}>Anthropic API Key</p>
          <p style={{ margin: "0 0 10px", fontSize: 12, color: "var(--color-text-secondary)" }}>Stored in your browser only. Never sent anywhere except api.anthropic.com.</p>
          <div style={{ display: "flex", gap: 8 }}>
            <input
              type="password"
              placeholder="sk-ant-..."
              value={keyInput}
              onChange={e => setKeyInput(e.target.value)}
              style={{ flex: 1, fontFamily: "var(--font-mono)" }}
            />
            <button onClick={saveKey} style={{ padding: "0 16px" }}>Save</button>
          </div>
          <p style={{ margin: "8px 0 0", fontSize: 11, color: "var(--color-text-secondary)" }}>
            Get your key at <a href="https://console.anthropic.com" target="_blank" rel="noreferrer">console.anthropic.com</a>
          </p>
        </div>
      )}

      {/* Technique Pills */}
      <div style={{ marginBottom: "1.25rem" }}>
        <p style={{ margin: "0 0 8px", fontSize: 12, color: "var(--color-text-secondary)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.05em" }}>Prompt Technique</p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {Object.entries(TECHNIQUES).map(([key, t]) => (
            <button
              key={key}
              onClick={() => loadTechnique(key)}
              style={{
                padding: "6px 14px",
                fontSize: 13,
                background: activeTech === key ? t.color : "transparent",
                color: activeTech === key ? "#fff" : "var(--color-text-primary)",
                border: activeTech === key ? `0.5px solid ${t.color}` : "0.5px solid var(--color-border-secondary)",
                borderRadius: "var(--border-radius-md)"
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
        <p style={{ margin: "8px 0 0", fontSize: 12, color: "var(--color-text-secondary)" }}>
          {TECHNIQUES[activeTech].description}
        </p>
      </div>

      {/* Main Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 260px", gap: 16, alignItems: "start" }}>

        {/* Left — Prompts */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div>
            <label style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", display: "block", marginBottom: 5 }}>
              System prompt
            </label>
            <textarea
              value={systemPrompt}
              onChange={e => setSystemPrompt(e.target.value)}
              rows={3}
              style={{ width: "100%", resize: "vertical", fontFamily: "var(--font-mono)", fontSize: 13, boxSizing: "border-box" }}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", display: "block", marginBottom: 5 }}>
              User prompt
            </label>
            <textarea
              value={userPrompt}
              onChange={e => setUserPrompt(e.target.value)}
              rows={7}
              style={{ width: "100%", resize: "vertical", fontFamily: "var(--font-mono)", fontSize: 13, boxSizing: "border-box" }}
            />
          </div>

          <button
            onClick={callAPI}
            disabled={loading}
            style={{ padding: "10px 0", fontSize: 14, fontWeight: 500, background: loading ? "transparent" : "var(--color-background-info)", color: loading ? "var(--color-text-secondary)" : "var(--color-text-info)", border: "0.5px solid var(--color-border-info)", borderRadius: "var(--border-radius-md)" }}
          >
            {loading ? "Running…" : apiKey ? "Run prompt ↗" : "Add API key to run ↗"}
          </button>

          {error && (
            <div style={{ background: "var(--color-background-danger)", border: "0.5px solid var(--color-border-danger)", borderRadius: "var(--border-radius-md)", padding: "10px 14px", fontSize: 13, color: "var(--color-text-danger)" }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {(response || loading) && (
            <div ref={responseRef} style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1rem 1.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)" }}>Response</span>
                <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>~{outputTokens} tokens out</span>
              </div>
              {loading ? (
                <p style={{ fontSize: 13, color: "var(--color-text-secondary)", margin: 0 }}>Thinking…</p>
              ) : (
                <pre style={{ margin: 0, fontSize: 13, whiteSpace: "pre-wrap", fontFamily: "var(--font-sans, sans-serif)", lineHeight: 1.7, color: "var(--color-text-primary)" }}>{response}</pre>
              )}
            </div>
          )}
        </div>

        {/* Right — Settings */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

          <div style={{ background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1rem" }}>
            <p style={{ margin: "0 0 12px", fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Model settings</p>

            <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 4 }}>Model</label>
            <select value={model} onChange={e => setModel(e.target.value)} style={{ width: "100%", fontSize: 13, marginBottom: 14 }}>
              {MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
            </select>

            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <label style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>Temperature</label>
              <span style={{ fontSize: 12, fontWeight: 500 }}>{temperature.toFixed(1)} — {tempLabel}</span>
            </div>
            <input type="range" min="0" max="1.5" step="0.1" value={temperature} onChange={e => setTemperature(parseFloat(e.target.value))} style={{ width: "100%", marginBottom: 6 }} />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--color-text-secondary)", marginBottom: 14 }}>
              <span>Precise</span><span>Balanced</span><span>Wild</span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <label style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>Max tokens</label>
              <span style={{ fontSize: 12, fontWeight: 500 }}>{maxTokens}</span>
            </div>
            <input type="range" min="100" max="2000" step="50" value={maxTokens} onChange={e => setMaxTokens(parseInt(e.target.value))} style={{ width: "100%" }} />
          </div>

          {/* Token Estimate */}
          <div style={{ background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1rem" }}>
            <p style={{ margin: "0 0 10px", fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Token estimate</p>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {[["Input", inputTokens, "var(--color-background-info)", "var(--color-text-info)"], ["Output", outputTokens, "var(--color-background-success)", "var(--color-text-success)"]].map(([label, val, bg, color]) => (
                <div key={label} style={{ background: bg, borderRadius: "var(--border-radius-md)", padding: "8px 10px" }}>
                  <p style={{ margin: 0, fontSize: 11, color }}>{label}</p>
                  <p style={{ margin: 0, fontSize: 20, fontWeight: 500, color }}>{val}</p>
                </div>
              ))}
            </div>
            <p style={{ margin: "8px 0 0", fontSize: 11, color: "var(--color-text-secondary)" }}>Approx. 1 token ≈ 0.75 words</p>
          </div>

          {/* Quick Reference */}
          <div style={{ background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1rem" }}>
            <p style={{ margin: "0 0 10px", fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Temperature guide</p>
            {[["0.0–0.3", "Code, extraction, facts"], ["0.4–0.6", "Q&A, summaries"], ["0.7–0.9", "Conversation, writing"], ["1.0–1.5", "Brainstorm, creativity"]].map(([range, use]) => (
              <div key={range} style={{ display: "flex", justifyContent: "space-between", padding: "3px 0", borderBottom: "0.5px solid var(--color-border-tertiary)" }}>
                <code style={{ fontSize: 11, color: "var(--color-text-primary)", fontFamily: "var(--font-mono)" }}>{range}</code>
                <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{use}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <p style={{ margin: "0 0 10px", fontSize: 12, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>Recent runs</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {history.map((h, i) => (
              <div key={i} style={{ background: "var(--color-background-secondary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-md)", padding: "10px 14px", cursor: "pointer" }}
                onClick={() => { setActiveTech(h.tech); setSystemPrompt(TECHNIQUES[h.tech].system); setUserPrompt(h.prompt); setResponse(h.response); }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                  <span style={{ fontSize: 12, fontWeight: 500, color: TECHNIQUES[h.tech]?.color || "var(--color-text-primary)" }}>{TECHNIQUES[h.tech]?.label}</span>
                  <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{h.time} · temp {h.temperature.toFixed(1)}</span>
                </div>
                <p style={{ margin: 0, fontSize: 12, color: "var(--color-text-secondary)", overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>
                  {h.response.substring(0, 100)}…
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
