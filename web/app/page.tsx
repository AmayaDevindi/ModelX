"use client";

import { useEffect, useState } from "react";
import Shell from "@/components/Shell";
import QuizModal from "@/components/QuizModal";
import ResultsPanel from "@/components/ResultsPanel";
import type { RecommendResult } from "@/lib/profile";

const STORAGE_KEY = "modelx_plan_v1";

export default function Home() {
  const [showQuiz, setShowQuiz] = useState(false);
  const [result, setResult] = useState<RecommendResult | null>(null);

  // First-time visitors (nothing saved yet in this browser) get the quiz
  // popup automatically. Returning visitors see their last result instead
  // and can retake it with the button below.
  useEffect(() => {
    let saved: string | null = null;
    try {
      saved = localStorage.getItem(STORAGE_KEY);
    } catch {
      // localStorage can throw in some contexts (private windows, etc.) -
      // just fall back to showing the quiz.
    }
    // One-time hydration from localStorage on mount - can't run during
    // render because localStorage isn't available during server rendering.
    if (saved) {
      try {
        // eslint-disable-next-line react-hooks/set-state-in-effect -- intentional
        setResult(JSON.parse(saved));
      } catch {
        setShowQuiz(true);
      }
    } else {
      setShowQuiz(true);
    }
  }, []);

  function handleComplete(r: RecommendResult) {
    setResult(r);
    setShowQuiz(false);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(r));
    } catch {
      // not fatal - just means it'll ask again next visit
    }
  }

  return (
    <Shell>
      <div className="flex-1 flex flex-col items-center justify-center gap-4 w-full">
        {result ? (
          <div className="w-full max-w-sm flex flex-col items-center gap-4">
            <p className="text-sm">
              Your profile: <span className="text-accent">{result.profile}</span>
            </p>
            {result.capNote && (
              <p className="text-xs text-muted leading-relaxed text-center">{result.capNote}</p>
            )}
            <ResultsPanel split={result.finalSplit} />
            <button
              onClick={() => setShowQuiz(true)}
              className="text-xs text-muted hover:text-accent underline"
            >
              retake the quiz
            </button>
          </div>
        ) : (
          <button
            onClick={() => setShowQuiz(true)}
            className="border border-accent text-accent rounded px-4 py-2"
          >
            Start the quiz
          </button>
        )}
      </div>

      {showQuiz && (
        <QuizModal
          onComplete={handleComplete}
          onClose={() => setShowQuiz(false)}
        />
      )}
    </Shell>
  );
}
