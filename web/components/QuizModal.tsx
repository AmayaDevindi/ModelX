"use client";

// The one-question-at-a-time popup: walks through the 4 risk questions,
// then the 4 knowledge-check questions, then shows the raw recommendation
// so we can confirm it's picking a sensible profile before wiring in the
// simulation (that comes next).

import { useState } from "react";
import { QUIZ, KNOWLEDGE_CHECK, recommend, type RecommendResult } from "@/lib/profile";
import SplitView from "@/components/SplitView";

type Props = {
  onComplete: (result: RecommendResult, quizAnswers: number[], knowledgeFlags: boolean[]) => void;
  onClose: () => void;
};

export default function QuizModal({ onComplete, onClose }: Props) {
  const totalSteps = QUIZ.length + KNOWLEDGE_CHECK.length;
  const [step, setStep] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<number[]>([]);
  const [knowledgeFlags, setKnowledgeFlags] = useState<boolean[]>([]);
  const [result, setResult] = useState<RecommendResult | null>(null);

  const isQuiz = step < QUIZ.length;
  const quizQuestion = isQuiz ? QUIZ[step] : null;
  const knowledgeItem = !isQuiz ? KNOWLEDGE_CHECK[step - QUIZ.length] : null;

  function finishIfLastElse(qa: number[], kf: boolean[]) {
    if (step + 1 < totalSteps) {
      setStep(step + 1);
      return;
    }
    const r = recommend(qa, kf);
    setResult(r);
  }

  function chooseQuizOption(optionIndex: number) {
    const next = [...quizAnswers, optionIndex];
    setQuizAnswers(next);
    finishIfLastElse(next, knowledgeFlags);
  }

  function chooseKnowledge(answer: boolean) {
    if (!knowledgeItem) return;
    const flag = answer === knowledgeItem.correctAnswer;
    const next = [...knowledgeFlags, flag];
    setKnowledgeFlags(next);
    finishIfLastElse(quizAnswers, next);
  }

  function goBack() {
    if (step === 0) return;
    if (isQuiz) {
      setQuizAnswers((prev) => prev.slice(0, -1));
    } else {
      setKnowledgeFlags((prev) => prev.slice(0, -1));
    }
    setStep((s) => s - 1);
  }

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
      <div className="bg-background border border-border rounded-lg w-full max-w-md p-6">
        {!result ? (
          <>
            <div className="text-muted text-xs mb-4">
              {isQuiz ? "Risk check" : "Knowledge check"} &middot; question {step + 1} of {totalSteps}
            </div>
            <p className="mb-5 leading-snug">
              {isQuiz ? quizQuestion!.question : knowledgeItem!.question}
            </p>
            <div className="flex flex-col gap-2">
              {isQuiz
                ? quizQuestion!.options.map((opt, i) => (
                    <button
                      key={i}
                      onClick={() => chooseQuizOption(i)}
                      className="text-left border border-border rounded px-3 py-2 hover:border-accent hover:text-accent transition-colors"
                    >
                      {opt}
                    </button>
                  ))
                : (
                    <div className="flex gap-2">
                      <button
                        onClick={() => chooseKnowledge(true)}
                        className="flex-1 border border-border rounded px-3 py-2 hover:border-accent hover:text-accent transition-colors"
                      >
                        Yes / True
                      </button>
                      <button
                        onClick={() => chooseKnowledge(false)}
                        className="flex-1 border border-border rounded px-3 py-2 hover:border-accent hover:text-accent transition-colors"
                      >
                        No / False
                      </button>
                    </div>
                  )}
            </div>
            <div className="flex justify-between mt-5 text-xs">
              <button onClick={goBack} disabled={step === 0} className="text-muted disabled:opacity-30">
                back
              </button>
              <button onClick={onClose} className="text-muted hover:text-foreground">
                close
              </button>
            </div>
          </>
        ) : (
          <>
            <div className="text-accent text-sm mb-1">Your profile: {result.profile}</div>
            <p className="text-muted text-xs mb-4">Here&apos;s how we&apos;d suggest splitting your money:</p>
            <SplitView split={result.finalSplit} />
            {result.capNote && (
              <p className="text-xs text-muted mt-4 leading-relaxed">{result.capNote}</p>
            )}
            <button
              onClick={() => onComplete(result, quizAnswers, knowledgeFlags)}
              className="w-full border border-accent text-accent rounded px-3 py-2 hover:bg-accent/10 transition-colors mt-5"
            >
              Continue
            </button>
          </>
        )}
      </div>
    </div>
  );
}
