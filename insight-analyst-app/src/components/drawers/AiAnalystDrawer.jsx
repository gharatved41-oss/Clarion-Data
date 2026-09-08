import React, { useState, useRef, useEffect } from 'react';
import { useTelemetry } from '../../context/TelemetryContext';
import { api } from '../../services/api';

export const AiAnalystDrawer = () => {
  const { 
    isAiDrawerOpen, 
    setIsAiDrawerOpen, 
    aiMessages, 
    addAiMessage, 
    isAiThinking, 
    activeDatasetId, 
    overview,
    addAuditLog 
  } = useTelemetry();
  
  const [inputText, setInputText] = useState('');
  const [diffApplying, setDiffApplying] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isAiDrawerOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [aiMessages, isAiDrawerOpen, isAiThinking]);

  if (!isAiDrawerOpen) return null;

  const handleSend = (e) => {
    e?.preventDefault();
    if (!inputText.trim() || isAiThinking) return;
    addAiMessage(inputText.trim(), "user");
    setInputText('');
  };

  const handlePromptClick = (prompt) => {
    if (isAiThinking) return;
    addAiMessage(prompt, "user");
  };

  const handleApplyDiff = async (msgId, diffObj) => {
    try {
      setDiffApplying(msgId);
      const res = await api.applyDiff(activeDatasetId, diffObj);
      addAuditLog("CODE_DIFF_APPLIED", `Applied AI proposed transformation to codebase: ${JSON.stringify(res)}`);
      alert("Code modification successfully applied and verified!");
    } catch (err) {
      alert(`Failed to apply diff: ${err.message}`);
    } finally {
      setDiffApplying(null);
    }
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-surface-container-high border-l border-outline-variant/60 shadow-2xl flex flex-col font-body-md select-none">
      {/* Drawer Header */}
      <div className="h-14 px-4 bg-surface-container-highest border-b border-outline-variant/40 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-primary-container border border-primary/40 flex items-center justify-center">
            <span className="material-symbols-outlined text-primary text-[20px]">psychology</span>
          </div>
          <div className="flex flex-col">
            <span className="font-headline-sm text-sm font-semibold text-on-surface">AI Data Analyst</span>
            <span className="font-data-mono text-[10px] text-tertiary flex items-center gap-1">
              <span className="w-1.5 h-1.5 bg-tertiary rounded-full animate-pulse"></span>
              Dataset: {activeDatasetId} ({overview?.rows || 0} rows)
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsAiDrawerOpen(false)}
            className="w-8 h-8 flex items-center justify-center text-outline hover:text-on-surface hover:bg-surface-container transition-colors"
          >
            <span className="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>
      </div>

      {/* Suggested Prompt Chips */}
      <div className="px-4 py-2.5 bg-surface-container-low border-b border-outline-variant/30 flex items-center gap-2 overflow-x-auto">
        <button
          onClick={() => handlePromptClick("Summarize this dataset and key findings")}
          disabled={isAiThinking}
          className="px-2.5 py-1 bg-surface-container border border-outline-variant/40 hover:border-primary text-on-surface text-[11px] font-data-mono whitespace-nowrap transition-colors disabled:opacity-50"
        >
          📊 Dataset Summary
        </button>
        <button
          onClick={() => handlePromptClick("What are the strongest correlations?")}
          disabled={isAiThinking}
          className="px-2.5 py-1 bg-surface-container border border-outline-variant/40 hover:border-primary text-on-surface text-[11px] font-data-mono whitespace-nowrap transition-colors disabled:opacity-50"
        >
          ⚡ Strong Correlations
        </button>
        <button
          onClick={() => handlePromptClick("Which columns have missing values?")}
          disabled={isAiThinking}
          className="px-2.5 py-1 bg-surface-container border border-outline-variant/40 hover:border-primary text-on-surface text-[11px] font-data-mono whitespace-nowrap transition-colors disabled:opacity-50"
        >
          🔍 Missing Values
        </button>
        <button
          onClick={() => handlePromptClick("Show me top 5 rows with highest value")}
          disabled={isAiThinking}
          className="px-2.5 py-1 bg-surface-container border border-outline-variant/40 hover:border-primary text-on-surface text-[11px] font-data-mono whitespace-nowrap transition-colors disabled:opacity-50"
        >
          📈 Top Records
        </button>
      </div>

      {/* Chat Messages Body */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {aiMessages.map((msg) => {
          const isUser = msg.sender === 'user';
          return (
            <div
              key={msg.id}
              className={`flex flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'}`}
            >
              <div className="flex items-center gap-2 text-[10px] font-data-mono text-outline">
                <span>{isUser ? 'You' : 'AI Analyst'}</span>
                <span>•</span>
                <span>{msg.timestamp}</span>
              </div>

              <div
                className={`p-3 max-w-[92%] text-xs font-data-mono leading-relaxed ${
                  isUser
                    ? 'bg-primary-container text-on-surface border border-primary/50'
                    : 'bg-surface-container-lowest text-on-surface-variant border border-outline-variant/40'
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.text}</div>

                {/* Diff Review & Apply Action */}
                {msg.diff && (
                  <div className="mt-3 p-3 bg-surface-container border border-secondary/40 flex flex-col gap-2">
                    <div className="flex items-center justify-between text-[11px] text-secondary font-bold">
                      <div className="flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-[16px]">code</span>
                        <span>Code Modification Proposal</span>
                      </div>
                      <span className="text-[10px] text-outline font-mono">
                        {msg.diff.target_file || 'Service Patch'}
                      </span>
                    </div>

                    <pre className="p-2 bg-black/60 border border-outline-variant/30 text-[10px] text-tertiary overflow-x-auto max-h-40 font-mono">
                      {msg.diff.patch || JSON.stringify(msg.diff, null, 2)}
                    </pre>

                    <button
                      onClick={() => handleApplyDiff(msg.id, msg.diff)}
                      disabled={diffApplying === msg.id}
                      className="self-end px-3 py-1 bg-secondary text-on-secondary text-xs font-semibold hover:bg-secondary-fixed-dim transition-colors flex items-center gap-1"
                    >
                      <span className="material-symbols-outlined text-[14px]">check</span>
                      <span>{diffApplying === msg.id ? 'Applying Patch...' : 'Apply Diff to Project'}</span>
                    </button>
                  </div>
                )}

                {msg.codeSnippet && (
                  <div className="mt-2.5 bg-black/50 border border-outline-variant/40 p-2.5 text-[11px] text-tertiary overflow-x-auto">
                    <div className="flex justify-between items-center pb-1 mb-1 border-b border-outline-variant/20 text-outline text-[9px] uppercase font-label-caps">
                      <span>Generated Code Snippet</span>
                      <button
                        onClick={() => navigator.clipboard.writeText(msg.codeSnippet)}
                        className="text-primary hover:underline"
                      >
                        Copy
                      </button>
                    </div>
                    <pre className="font-mono">{msg.codeSnippet}</pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* AI Thinking Indicator */}
        {isAiThinking && (
          <div className="flex flex-col gap-1.5 items-start">
            <div className="flex items-center gap-2 text-[10px] font-data-mono text-outline">
              <span>AI Analyst</span>
              <span>•</span>
              <span>Thinking...</span>
            </div>
            <div className="p-3 bg-surface-container-lowest border border-outline-variant/40 text-xs font-data-mono flex items-center gap-2 text-outline">
              <span className="w-2 h-2 bg-primary rounded-full animate-ping"></span>
              <span>Querying analytical services and dataset context...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSend} className="p-3 bg-surface-container-low border-t border-outline-variant/30 flex flex-col gap-2">
        <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant/60 focus-within:border-primary px-3 py-2">
          <input
            type="text"
            placeholder={isAiThinking ? "Waiting for response..." : "Ask dataset question or request calculation..."}
            value={inputText}
            disabled={isAiThinking}
            onChange={(e) => setInputText(e.target.value)}
            className="flex-1 bg-transparent text-xs font-data-mono text-on-surface placeholder:text-outline outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!inputText.trim() || isAiThinking}
            className="w-7 h-7 bg-primary text-on-primary flex items-center justify-center disabled:opacity-30 transition-opacity"
          >
            <span className="material-symbols-outlined text-[16px]">send</span>
          </button>
        </div>
        <div className="flex items-center justify-between text-[10px] font-data-mono text-outline px-1">
          <span>Active Context: {overview?.filename || activeDatasetId}</span>
          <span>Shift + Enter for new line</span>
        </div>
      </form>
    </div>
  );
};
