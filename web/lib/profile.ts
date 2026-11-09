// Port of src/model/profile.py - keep these two files in sync if either changes.
// See that file's docstring for the reasoning (CFA Institute risk-profiling
// guide, decisions D47/D48).

export const ASSETS = [
  "Savings",
  "Fixed deposits",
  "T-bills & bonds",
  "Unit trusts",
  "Shares (S&P SL20)",
] as const;

export type Asset = (typeof ASSETS)[number];
export type Split = Record<Asset, number>;

export const QUIZ: { question: string; options: string[] }[] = [
  {
    question: "Your investment drops 20% after three months. What do you do?",
    options: ["Sell everything", "Sell some", "Do nothing", "Buy a little more", "Buy a lot more"],
  },
  {
    question: "How long can you leave this money untouched?",
    options: ["Less than 1 year", "1-2 years", "3-5 years", "5-10 years", "More than 10 years"],
  },
  {
    question: "Which sounds best to you?",
    options: [
      "Keep my money exactly as it is, even if it earns little",
      "Small steady gains, tiny chance of loss",
      "Medium gains, some chance of loss",
      "Higher gains, real chance of loss",
      "Highest possible gains, big swings are fine",
    ],
  },
  {
    question: "Do you have about 6 months of expenses saved separately, outside this money?",
    options: ["No, none", "Less than 3 months", "About 3 months", "About 6 months", "More than 6 months"],
  },
];

export const PROFILES: Record<string, number[]> = {
  Cautious: [25, 40, 25, 10, 0],
  Conservative: [15, 30, 30, 15, 10],
  Balanced: [10, 20, 25, 20, 25],
  Growth: [5, 10, 20, 25, 40],
  Adventurous: [0, 5, 15, 25, 55],
};

for (const [name, split] of Object.entries(PROFILES)) {
  const total = split.reduce((a, b) => a + b, 0);
  if (total !== 100) throw new Error(`${name} split does not add to 100: ${split}`);
}

export function riskProfile(answers: number[]): { profile: string; score: number } {
  const score = answers.reduce((a, b) => a + b, 0);
  const names = Object.keys(PROFILES);
  let profile = names[Math.min(Math.floor((score * names.length) / (4 * QUIZ.length + 1)), names.length - 1)];
  if (answers[1] === 0) profile = "Cautious"; // needs the money within a year - override
  return { profile, score };
}

export function splitFor(profile: string): Split {
  const values = PROFILES[profile];
  return Object.fromEntries(ASSETS.map((a, i) => [a, values[i]])) as Split;
}

export const KNOWLEDGE_CHECK: { question: string; correctAnswer: boolean }[] = [
  { question: "Have you personally bought a government Treasury bill or bond before (not through someone else)?", correctAnswer: true },
  { question: "Have you personally bought shares or unit trust units before?", correctAnswer: true },
  { question: "If you break a fixed deposit early, you usually lose some of the interest as a penalty. True or false?", correctAnswer: true },
  { question: "A share's price can fall by more than 20% in a single week. True or false?", correctAnswer: true },
];

export const KNOWLEDGE_CAP: Record<number, number> = { 0: 10, 1: 15, 2: 25, 3: 40, 4: 100 };

export function knowledgeScore(correctFlags: boolean[]): number {
  return correctFlags.filter(Boolean).length;
}

export function applyKnowledgeCap(
  split: Split,
  kScore: number
): { finalSplit: Split; note: string | null } {
  const cap = KNOWLEDGE_CAP[kScore];
  const shares = split["Shares (S&P SL20)"];
  if (shares <= cap) return { finalSplit: { ...split }, note: null };
  const moved = shares - cap;
  const finalSplit: Split = { ...split, "Shares (S&P SL20)": cap, "Fixed deposits": split["Fixed deposits"] + moved };
  const note =
    `Your risk answers suggested ${shares}% in shares, but your knowledge check score ` +
    `(${kScore}/4) caps that at ${cap}% for now - the rest (${moved} points) went to fixed ` +
    `deposits instead. This limit can loosen as you get more familiar with how shares work.`;
  return { finalSplit, note };
}

export function recommend(quizAnswers: number[], knowledgeFlags: boolean[]) {
  const { profile, score } = riskProfile(quizAnswers);
  const split = splitFor(profile);
  const kScore = knowledgeScore(knowledgeFlags);
  const { finalSplit, note } = applyKnowledgeCap(split, kScore);
  return { profile, riskScore: score, knowledgeScore: kScore, targetSplit: split, finalSplit, capNote: note };
}

export type RecommendResult = ReturnType<typeof recommend>;
