"""
Step 2 of Model 1: a short quiz -> a risk profile -> a target split,
then a separate knowledge check that can cap how much goes into shares.

Grounded in the CFA Institute's professional risk-profiling guide
(rpc.cfainstitute.org, "Investment Risk Profiling: A Guide for Financial
Advisors"), which treats "risk tolerance/behaviour" and "financial knowledge/
experience" as separate things, and says ability/knowledge sets a ceiling
that a high risk-tolerance score should NOT override. We follow its wording
rules too: no self-labels ("are you risk tolerant?"), no jargon like
"aggressive", ask about real past behaviour/facts, not predictions.
"""
from assumptions import ASSETS

# ---- Part A: risk tolerance + capacity (decides the PROFILE) ----
QUIZ = [
    ("Your investment drops 20% after three months. What do you do?",
     ["Sell everything", "Sell some", "Do nothing", "Buy a little more", "Buy a lot more"]),
    ("How long can you leave this money untouched?",
     ["Less than 1 year", "1-2 years", "3-5 years", "5-10 years", "More than 10 years"]),
    ("Which sounds best to you?",
     ["Keep my money exactly as it is, even if it earns little",
      "Small steady gains, tiny chance of loss",
      "Medium gains, some chance of loss",
      "Higher gains, real chance of loss",
      "Highest possible gains, big swings are fine"]),
    ("Do you have about 6 months of expenses saved separately, outside this money?",
     ["No, none", "Less than 3 months", "About 3 months", "About 6 months", "More than 6 months"]),
]

PROFILES = {
    "Cautious":     [25, 40, 25, 10, 0],
    "Conservative": [15, 30, 30, 15, 10],
    "Balanced":     [10, 20, 25, 20, 25],
    "Growth":       [5, 10, 20, 25, 40],
    "Adventurous":  [0, 5, 15, 25, 55],
}
for _name, _split in PROFILES.items():
    assert sum(_split) == 100, f"{_name} split does not add to 100: {_split}"


def risk_profile(answers):
    """answers: a list of option positions (0-4), one per question in QUIZ."""
    score = sum(answers)
    names = list(PROFILES)
    profile = names[min(score * len(names) // (4 * len(QUIZ) + 1), len(names) - 1)]
    if answers[1] == 0:        # needs the money within a year
        profile = "Cautious"   # override: no shares, whatever the score says
    return profile, score


def split_for(profile):
    return dict(zip(ASSETS, PROFILES[profile]))


# ---- Part B: a SEPARATE knowledge/experience check (not self-rated) ----
# Each item has a right answer (True) or a "have you done this" fact.
# This is deliberately not "how much do you know, 1-5" - that is a self-label,
# which the CFA guide warns against.
KNOWLEDGE_CHECK = [
    ("Have you personally bought a government Treasury bill or bond before "
     "(not through someone else)?", True),
    ("Have you personally bought shares or unit trust units before?", True),
    ("If you break a fixed deposit early, you usually lose some of the interest "
     "as a penalty. True or false?", True),
    ("A share's price can fall by more than 20% in a single week. True or false?", True),
]

# How much of the Shares slice we allow through, by knowledge score (0-4).
# A low score doesn't change the PROFILE - it caps how much of it is acted on.
KNOWLEDGE_CAP = {0: 10, 1: 15, 2: 25, 3: 40, 4: 100}


def knowledge_score(correct_flags):
    """correct_flags: list of True/False, one per KNOWLEDGE_CHECK item,
    True meaning the user answered that item correctly / confirmed the fact."""
    return sum(1 for f in correct_flags if f)


def apply_knowledge_cap(split, k_score):
    """If Shares exceeds what this knowledge level allows, trim it and move
    the difference into Fixed deposits (simple, well understood, no risk of
    loss) instead. Returns (new split, note or None)."""
    cap = KNOWLEDGE_CAP[k_score]
    shares = split["Shares (S&P SL20)"]
    if shares <= cap:
        return dict(split), None
    moved = shares - cap
    new_split = dict(split)
    new_split["Shares (S&P SL20)"] = cap
    new_split["Fixed deposits"] += moved
    note = (f"Your risk answers suggested {shares}% in shares, but your knowledge check score "
           f"({k_score}/4) caps that at {cap}% for now - the rest ({moved} points) went to fixed "
           f"deposits instead. This limit can loosen as you get more familiar with how shares work.")
    return new_split, note


def recommend(quiz_answers, knowledge_flags):
    profile, score = risk_profile(quiz_answers)
    split = split_for(profile)
    k_score = knowledge_score(knowledge_flags)
    final_split, note = apply_knowledge_cap(split, k_score)
    return dict(profile=profile, risk_score=score, knowledge_score=k_score,
               target_split=split, final_split=final_split, cap_note=note)


if __name__ == "__main__":
    cases = [
        ("adventurous risk answers, knows nothing (all wrong)",
         [4, 4, 4, 4], [False, False, False, False]),
        ("adventurous risk answers, knows the basics (all correct)",
         [4, 4, 4, 4], [True, True, True, True]),
        ("balanced risk answers, some knowledge",
         [2, 2, 2, 2], [True, True, False, False]),
        ("cautious risk answers (shares already 0, cap can't matter)",
         [0, 0, 0, 0], [False, False, False, False]),
    ]
    for label, qa, kf in cases:
        r = recommend(qa, kf)
        print(f"\n{label}")
        print(f"  profile {r['profile']} (risk score {r['risk_score']}), knowledge {r['knowledge_score']}/4")
        print(f"  target split:", r["target_split"])
        print(f"  final split: ", r["final_split"])
        if r["cap_note"]:
            print(f"  note: {r['cap_note']}")
