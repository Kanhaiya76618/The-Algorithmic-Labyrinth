# The-Algorithmic-Labyrinth
AI-powered dungeon crawler where a self-improving Boss NPC adapts DSA, logic, and math challenges to each player using Cognee's memory lifecycle + RL.

Dungeon of Recall is a single-player dungeon-crawler built for the Cognee "Hangover Part AI" hackathon. Each floor gates progress behind a coding (DSA), logic, or math challenge that scales in difficulty as you descend — easy puzzle rooms, medium mini-bosses, and a hard final boss, plus a hidden side-dungeon of math/logic riddles.
The twist: the Boss/NPC AI actually remembers you. Using Cognee's full memory lifecycle — remember(), recall(), improve()/memify, and forget() — combined with a lightweight Sarsa(λ)-style reinforcement learning layer over the knowledge graph, the dungeon master tracks your patterns (weak topics, time-under-pressure, retry behavior) and adapts question selection and boss strategy across sessions. No more facing the same static difficulty curve twice.
