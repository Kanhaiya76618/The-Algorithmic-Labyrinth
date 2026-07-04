export const BOSS_TAUNT_MAPPING = {
  generic: [
    "Back again? I never forget a challenger. Especially not one who fails like you.",
    "Every wrong answer you have ever given echoes in these halls. I collected them all.",
    "Descend as often as you like. My memory is deeper than this dungeon.",
    "You look confident. You looked confident last time, too."
  ],
  by_topic: {
    "arrays": "Rows of treasure, rows of failure. Arrays undid you before — they will again.",
    "strings": "Your incantations always fray at the edges. Letters are not your friends.",
    "hashing": "You reach for the same bucket every time. I remember every collision.",
    "two-pointers": "Two hands, and you still cannot hold both ends of a problem.",
    "sliding-window": "Your window slides; your mind does not. I have watched it stick before.",
    "stacks-queues": "Push, pop, panic. That is the order you always follow.",
    "linked-lists": "You lose the chain the moment it bends. I have seen you chase your own tail.",
    "recursion": "To understand your failure, first understand your smaller failure.",
    "sorting": "You put nothing in its right place. Not even last time's lesson.",
    "binary-search": "Half the answers gone, and you still search the wrong half.",
    "trees": "You always get lost past the second branch. The roots remember you.",
    "heaps": "The greatest of your errors always floats to the top.",
    "graphs": "So many paths, and you walk in circles. I mapped every wrong turn you took.",
    "dynamic-programming": "You solve the same subproblem over and over — and fail it over and over.",
    "greedy": "You grab the shiniest coin every time. That greed fed me well before.",
    "bit-manipulation": "One bit off. It is always one bit off with you.",
    "math": "The numbers whispered your weakness to me long ago.",
    "logic-puzzle": "No code to hide behind down here. Just your reasoning — and I have measured it."
  },
  by_probe: {
    "edge:empty": "Shall I hand you nothing again? Emptiness breaks you every single time.",
    "edge:single": "One lonely element. One lonely challenger. Both defeat you.",
    "edge:duplicates": "You assume everything is unique. I remember twice how wrong you are.",
    "edge:all-equal": "When everything looks the same, you fall apart. I made everything the same.",
    "edge:sorted": "Order itself defeats you — I have seen your code trip over tidiness.",
    "edge:reverse-sorted": "I will simply turn the line around. That was enough last time.",
    "edge:negative": "You always forget the numbers below zero. They never forgot you.",
    "edge:zero": "Zero. Such a small thing to die on. Again.",
    "edge:max-bounds": "I will push everything to the limit. Your limits arrive first.",
    "edge:overflow": "Your numbers burst their banks while mine flow on. Thirty-two bits of hubris.",
    "edge:no-solution": "Sometimes there is no answer — and you always insist on giving one.",
    "edge:cycle": "Round and round you went, chasing a loop you never checked for.",
    "edge:disconnected": "You forget the islands you cannot see. I count on it.",
    "edge:unbalanced": "One crooked branch and your whole plan topples. I grew this one crooked.",
    "perf:large_n": "Take your time. You always do — until the hourglass wins.",
    "adversarial:worst-case": "I built this floor from your textbook solution's blind spot."
  },
  on_correct: [
    "Adequate. I am adjusting my notes on you.",
    "Hm. You did not make that mistake this time. Noted.",
    "A cleared floor is only more material for my ledger."
  ],
  on_defeat: [
    "Remember this victory. I certainly will.",
    "You have grown past what my memory promised. It will not happen twice.",
    "Take the stairs down. I will be waiting — and I will be ready for who you are NOW."
  ]
};
