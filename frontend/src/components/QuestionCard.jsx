import React, { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Timer, Play } from "lucide-react";
import { CornerRune } from "./Atmosphere";
import { LANGUAGES } from "../api/client";

export const QuestionCard = ({
  question,
  monsterImg,
  onAnswer,
  onClose,
  testid = "question-card",
}) => {
  const [selected, setSelected] = useState(null);
  const [answerInput, setAnswerInput] = useState("");
  const [language, setLanguage] = useState("python3");
  const [code, setCode] = useState("");
  const [state, setState] = useState("asking"); // asking | submitting | correct | wrong
  const [timeLeft, setTimeLeft] = useState(100);
  const [verdictMessage, setVerdictMessage] = useState("");
  const [failedProbes, setFailedProbes] = useState([]);

  useEffect(() => {
    // Reset inputs when question changes
    setSelected(null);
    setAnswerInput("");
    setLanguage("python3");
    setCode(question?.starter_code?.python3 ?? "");
    setState("asking");
    setTimeLeft(100);
    setVerdictMessage("");
    setFailedProbes([]);
  }, [question?.question_id]);

  useEffect(() => {
    if (state !== "asking") return;
    const id = setInterval(() => setTimeLeft((t) => Math.max(0, t - 1.2)), 100);
    return () => clearInterval(id);
  }, [state]);

  const handleMCQPick = async (opt) => {
    if (state !== "asking") return;
    setSelected(opt.key);
    setState("submitting");
    try {
      if (onAnswer) {
        const resp = await onAnswer({ answer: opt.key });
        const ok = resp.result.correct;
        setState(ok ? "correct" : "wrong");
        setVerdictMessage(resp.result.message || "");
        setFailedProbes(resp.result.failed_probes || []);
      }
    } catch (err) {
      setState("wrong");
      setVerdictMessage(err.message || "Failed to submit answer");
    }
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    if (state !== "asking") return;
    setState("submitting");
    try {
      if (onAnswer) {
        const payload = question.question_type === "code" ? { code, language } : { answer: answerInput };
        const resp = await onAnswer(payload);
        const ok = resp.result.correct;
        setState(ok ? "correct" : "wrong");
        setVerdictMessage(resp.result.message || "");
        setFailedProbes(resp.result.failed_probes || []);
      }
    } catch (err) {
      setState("wrong");
      setVerdictMessage(err.message || "Failed to submit answer");
    }
  };

  const isCode = question.question_type === "code";
  const isShort = question.question_type === "short_answer";
  const isMCQ = question.options && question.options.length > 0;

  const canSubmit = isCode ? code.trim().length > 0 : answerInput.trim().length > 0;

  const handleLanguageChange = (lang) => {
    setLanguage(lang);
    if (question.starter_code?.[lang] !== undefined) {
      setCode(question.starter_code[lang]);
    }
  };

  return (
    <motion.div
      initial={{ y: 40, opacity: 0, scale: 0.95 }}
      animate={
        state === "wrong"
          ? { y: 0, opacity: 1, scale: 1, x: [-10, 10, -8, 8, 0] }
          : { y: 0, opacity: 1, scale: 1 }
      }
      exit={{ y: 40, opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="glass-panel relative p-4 w-full"
      data-testid={testid}
    >
      <CornerRune className="absolute -top-2 -left-2 w-6 h-6" />
      <CornerRune className="absolute -top-2 -right-2 w-6 h-6" flip />

      {onClose && (
        <button
          onClick={onClose}
          data-testid="question-close"
          className="absolute top-2 right-2 w-7 h-7 rounded-full bg-stone-dark/70 border border-cyan-mist/30 flex items-center justify-center hover:border-cyan-mist"
        >
          <X className="w-4 h-4 text-bone" />
        </button>
      )}

      {monsterImg && (
        <div className="absolute -top-14 left-1/2 -translate-x-1/2 w-24 h-24 pointer-events-none">
          <img
            src={monsterImg}
            alt=""
            className="w-full h-full object-contain animate-idle-bob drop-shadow-[0_8px_20px_rgba(0,229,255,0.35)]"
          />
        </div>
      )}

      {/* Vine timer */}
      <div className="flex items-center gap-2 mb-3 mt-2">
        <Timer className="w-3.5 h-3.5 text-cyan-mist" />
        <div className="vine-bar flex-1 h-2">
          <div
            className="vine-bar-fill transition-[width] duration-100"
            style={{
              width: `${timeLeft}%`,
              background:
                timeLeft < 30
                  ? "linear-gradient(90deg, #FF6B35, #B44420)"
                  : "linear-gradient(90deg, #3F5A42, #00E5FF)",
            }}
          />
        </div>
        <span className="font-mono text-[10px] text-cyan-mist tabular-nums w-6 text-right">
          {Math.ceil(timeLeft / 10)}
        </span>
      </div>

      {/* Prompt */}
      <p className="font-display text-sm md:text-base font-bold text-bone text-shadow-stone leading-tight mb-3">
        {question.prompt}
      </p>

      {/* Code visible test cases preview */}
      {isCode && question.visible_tests && question.visible_tests.length > 0 && (
        <div className="mb-3 space-y-1.5 p-2 rounded bg-stone-darkest/75 border border-cyan-mist/10">
          <p className="font-mono text-[9px] tracking-wider text-cyan-mist/85 uppercase">
            Visible Tests:
          </p>
          {question.visible_tests.map((test, index) => (
            <div key={index} className="font-mono text-[10px] text-stone-pale flex gap-2">
              <span className="text-cyan-mist/70">In:</span> {test.stdin.trim()}
              <span className="text-cyan-mist/70">Out:</span> {test.expected_stdout.trim()}
            </div>
          ))}
        </div>
      )}

      {/* Dynamic input templates based on question type */}
      {state === "asking" || state === "submitting" ? (
        <div>
          {isMCQ ? (
            <div className="grid grid-cols-1 gap-2" data-testid="question-options">
              {question.options.map((opt) => {
                const isPicked = selected === opt.key;
                let cls =
                  "border-cyan-mist/25 bg-moss-dark/60 hover:border-cyan-mist hover:bg-moss-mid/70";
                if (isPicked) cls = "border-cyan-mist bg-cyan-mist/25 shadow-cyan-glow";

                return (
                  <button
                    key={opt.key}
                    onClick={() => handleMCQPick(opt)}
                    disabled={state === "submitting"}
                    data-testid={`question-option-${opt.key}`}
                    className={`text-left px-3 py-2.5 rounded-lg border-2 transition-all flex items-center gap-3 ${cls}`}
                  >
                    <span
                      className="w-7 h-7 rounded-md carved-stone flex items-center justify-center font-heading font-bold text-cyan-mist text-sm shrink-0"
                      style={isPicked ? { color: "#0B120C", background: "#00E5FF" } : {}}
                    >
                      {opt.key}
                    </span>
                    <span className="font-body text-sm text-bone">{opt.text}</span>
                  </button>
                );
              })}
            </div>
          ) : isCode ? (
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-mono text-[9px] tracking-wider text-stone-pale uppercase">
                  Language
                </span>
                <select
                  value={language}
                  onChange={(e) => handleLanguageChange(e.target.value)}
                  disabled={state === "submitting"}
                  className="bg-stone-darkest text-bone border border-cyan-mist/30 rounded px-2 py-1 font-mono text-xs focus:outline-none focus:border-cyan-mist"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang} value={lang}>
                      {lang}
                    </option>
                  ))}
                </select>
              </div>
              <textarea
                value={code}
                onChange={(e) => setCode(e.target.value)}
                disabled={state === "submitting"}
                placeholder="Write your code here..."
                spellCheck={false}
                rows={6}
                className="w-full bg-stone-darkest text-bone border border-cyan-mist/30 rounded-lg p-2.5 font-mono text-xs focus:outline-none focus:border-cyan-mist resize-none"
              />
              <button
                onClick={handleSubmit}
                disabled={state === "submitting" || !canSubmit}
                className="btn-ember w-full flex items-center justify-center gap-2"
              >
                <Play className="w-4 h-4" />
                {state === "submitting" ? "CASTING SPELL..." : "RUN SUBMISSION"}
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <input
                type="text"
                value={answerInput}
                onChange={(e) => setAnswerInput(e.target.value)}
                disabled={state === "submitting"}
                placeholder="Type your answer here..."
                className="w-full bg-stone-darkest text-bone border border-cyan-mist/30 rounded-lg px-3 py-2 font-body text-sm focus:outline-none focus:border-cyan-mist"
                autoFocus
              />
              <button
                onClick={handleSubmit}
                disabled={state === "submitting" || !canSubmit}
                className="btn-ember w-full"
              >
                {state === "submitting" ? "SUBMITTING..." : "SUBMIT ANSWER"}
              </button>
            </div>
          )}
        </div>
      ) : null}

      {/* Result banner */}
      <AnimatePresence>
        {state === "correct" && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 py-2 px-3 rounded-lg bg-cyan-mist/15 border border-cyan-mist flex flex-col gap-1.5"
            data-testid="answer-correct"
          >
            <div className="flex items-center justify-between">
              <span className="font-heading text-xs font-bold tracking-widest text-cyan-mist">
                MEMORY RECALLED
              </span>
              <span className="font-mono text-xs text-cyan-mist">+ 12 XP</span>
            </div>
            {verdictMessage && (
              <p className="font-body text-xs text-stone-pale italic">{verdictMessage}</p>
            )}
          </motion.div>
        )}
        {state === "wrong" && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mt-3 py-2 px-3 rounded-lg bg-ember-orange/15 border border-ember-orange flex flex-col gap-1.5"
            data-testid="answer-wrong"
          >
            <div className="flex items-center justify-between">
              <span className="font-heading text-xs font-bold tracking-widest text-ember-orange">
                THE RUINS FORGET YOU
              </span>
              <span className="font-mono text-xs text-ember-orange">– 1 HP</span>
            </div>
            {failedProbes.length > 0 && (
              <p className="font-mono text-[9px] tracking-wide text-ember-orange/90 uppercase">
                Broke on probes: {failedProbes.join(", ")}
              </p>
            )}
            {verdictMessage && (
              <p className="font-body text-xs text-stone-pale italic">{verdictMessage}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
