import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import * as client from "../api/client";
import { BOSS_TAUNT_MAPPING } from "../data/dialogueMapping";
import { ZONES } from "../data/game";

const GameContext = createContext(null);

export function GameProvider({ children }) {
  const [playerName, setPlayerName] = useState(() => window.localStorage.getItem(client.PLAYER_NAME_KEY) || "");
  const [runId, setRunId] = useState(() => window.localStorage.getItem(client.RUN_ID_KEY) || "");
  const [runLevel, setRunLevel] = useState(1);
  const [inHidden, setInHidden] = useState(false);
  const [hiddenLevel, setHiddenLevel] = useState(1);
  const [discovery, setDiscovery] = useState({ revealed: false, via: null, whispers: [] });
  const [report, setReport] = useState(null);
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(false);

  // Derive shards from profile
  const shards = report?.profile ? mapProfileToShards(report.profile) : [];

  // Derive journal
  const journal = report?.profile
    ? {
        mastered: (report.profile.strong_topics || []).map((t) => {
          const tObj = (report.topics || []).find((x) => x.name.toLowerCase() === t.toLowerCase());
          return { topic: t, accuracy: tObj ? tObj.weight : 0.85 };
        }),
        haunting: (report.profile.weak_topics || []).map((t) => {
          const tObj = (report.topics || []).find((x) => x.name.toLowerCase() === t.toLowerCase());
          return { topic: t, accuracy: tObj ? tObj.weight : 0.40 };
        }),
        zones: ZONES.map((z, idx) => {
          const zoneTopics = {
            0: ["arrays", "strings"],
            1: ["hashing", "two-pointers", "sliding-window"],
            2: ["stacks-queues", "linked-lists", "sorting"],
            3: ["binary-search", "recursion", "greedy"],
            4: ["trees", "graphs", "dynamic-programming"],
          }[idx] || [];
          let totalAcc = 0;
          let count = 0;
          zoneTopics.forEach((t) => {
            const tObj = (report.topics || []).find((x) => x.name.toLowerCase() === t.toLowerCase());
            if (tObj) {
              totalAcc += (1.0 - tObj.weight);
              count++;
            }
          });
          // Default to 1.0 (perfect) if the player hasn't failed any topics in this zone yet
          const accuracy = count > 0 ? totalAcc / count : 1.0;
          return { id: z.id, name: z.name, accuracy };
        }),
      }
    : { mastered: [], haunting: [], zones: ZONES.map((z) => ({ id: z.id, name: z.name, accuracy: 1.0 })) };

  // Derive threat gauge level
  const threatLevel = report?.threat_level ?? 0;
  const gaugeLevel = Math.round((threatLevel / 100) * 5); // out of 5 segments

  // Function to refresh memory report
  const refreshReport = useCallback(async (pName = playerName) => {
    if (!pName) return;
    try {
      const rep = await client.getMemoryReport(pName);
      setReport(rep);
    } catch (err) {
      console.warn("Failed to fetch memory report", err);
    }
  }, [playerName]);

  // Sync state if playerName exists on load
  useEffect(() => {
    if (playerName) {
      refreshReport(playerName);
      if (runId) {
        // Fetch current challenge to synchronize state
        client.nextChallenge(runId)
          .then((resp) => {
            setChallenge(resp.challenge);
            setRunLevel(resp.level);
            setInHidden(resp.in_hidden);
            setHiddenLevel(resp.hidden_level);
          })
          .catch((err) => {
            console.warn("Could not resume active run:", err);
          });
      }
    }
  }, [playerName, runId, refreshReport]);

  const startGameSession = async (name) => {
    setLoading(true);
    try {
      const started = await client.startGame(name);
      window.localStorage.setItem(client.PLAYER_NAME_KEY, name);
      window.localStorage.setItem(client.RUN_ID_KEY, started.run_id);
      setPlayerName(name);
      setRunId(started.run_id);
      setRunLevel(started.level);
      setInHidden(false);
      setHiddenLevel(1);
      setDiscovery(started.discovery);
      await refreshReport(name);
      
      // Load first challenge
      const resp = await client.nextChallenge(started.run_id);
      setChallenge(resp.challenge);
    } catch (err) {
      console.error("Failed to start game session", err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchNextChallenge = async () => {
    if (!runId) return null;
    try {
      const resp = await client.nextChallenge(runId);
      setChallenge(resp.challenge);
      setRunLevel(resp.level);
      setInHidden(resp.in_hidden);
      setHiddenLevel(resp.hidden_level);
      return resp;
    } catch (err) {
      console.warn("Failed to fetch next challenge", err);
      // Backend keeps runs in memory (uvicorn --reload wipes them): a
      // persisted run_id can go stale and 404 forever. Runs are ephemeral
      // but the Boss's memory is keyed by player name — so mint a fresh run
      // for the known player instead of silently doing nothing.
      if (String(err.message).includes(" 404 ")) {
        if (playerName) {
          try {
            const started = await client.startGame(playerName);
            window.localStorage.setItem(client.RUN_ID_KEY, started.run_id);
            setRunId(started.run_id);
            setRunLevel(started.level);
            setInHidden(false);
            setHiddenLevel(1);
            setDiscovery(started.discovery);
            const resp = await client.nextChallenge(started.run_id);
            setChallenge(resp.challenge);
            return resp;
          } catch (restartErr) {
            console.warn("Failed to restart run after stale run_id", restartErr);
          }
        }
        window.localStorage.removeItem(client.RUN_ID_KEY);
        setRunId("");
        setChallenge(null);
      }
      return null;
    }
  };

  const submitAnswerSession = async (payload) => {
    if (!runId || !challenge) return null;
    try {
      const resp = await client.submitAnswer(runId, challenge.question_id, payload);
      setRunLevel(resp.level);
      setInHidden(resp.in_hidden);
      setHiddenLevel(resp.hidden_level);
      setDiscovery(resp.discovery);
      await refreshReport();
      return resp;
    } catch (err) {
      console.error("Failed to submit answer", err);
      throw err;
    }
  };

  const exploreSession = async (action, target) => {
    if (!runId) return false;
    try {
      const resp = await client.explore(runId, action, target);
      if (resp.recorded) {
        await refreshReport();
      }
      return resp.recorded;
    } catch (err) {
      console.warn("Failed to record exploration", err);
      return false;
    }
  };

  const enterHiddenSession = async () => {
    if (!runId) return null;
    try {
      const resp = await client.enterHidden(runId);
      setDiscovery(resp.discovery);
      setInHidden(true);
      setHiddenLevel(resp.level);
      await fetchNextChallenge();
      return resp;
    } catch (err) {
      console.error("Failed to enter hidden dungeon", err);
      throw err;
    }
  };

  const forgetSession = async () => {
    if (!playerName) return;
    try {
      await client.forget(playerName);
      // Clean local storage and state
      window.localStorage.removeItem(client.PLAYER_NAME_KEY);
      window.localStorage.removeItem(client.RUN_ID_KEY);
      setPlayerName("");
      setRunId("");
      setRunLevel(1);
      setInHidden(false);
      setHiddenLevel(1);
      setDiscovery({ revealed: false, via: null, whispers: [] });
      setReport(null);
      setChallenge(null);
    } catch (err) {
      console.error("Failed to forget memory", err);
    }
  };

  // Helper to map profile attributes to shards
  function mapProfileToShards(profile) {
    const sList = [];
    if (!profile) return sList;

    if (profile.weak_topics) {
      profile.weak_topics.forEach((topic) => {
        sList.push({
          id: `shd-weak-${topic}`,
          type: "weakness",
          title: `Weak topic: ${topic}`,
          detail: "Repeated trial failures detected",
          source: "Dungeon Master Log",
          weight: 0.8,
        });
      });
    }

    if (profile.strong_topics) {
      profile.strong_topics.forEach((topic) => {
        sList.push({
          id: `shd-strong-${topic}`,
          type: "strength",
          title: `Strong topic: ${topic}`,
          detail: "High accuracy demonstrated",
          source: "Dungeon Master Log",
          weight: 0.9,
        });
      });
    }

    if (profile.weak_probes) {
      profile.weak_probes.forEach((probe) => {
        sList.push({
          id: `shd-probe-${probe}`,
          type: "behavior",
          title: `Vulnerable to: ${probe}`,
          detail: "Fails on this edge case",
          source: "Dungeon Master Log",
          weight: 0.75,
        });
      });
    }

    if (profile.explorer_score > 0) {
      sList.push({
        id: "shd-explorer",
        type: "behavior",
        title: "Exploration Behavior",
        detail: `Mapped ${Math.round(profile.explorer_score * 8)}/8 distinct areas`,
        source: "Dungeon Map",
        weight: profile.explorer_score,
      });
    }

    if (profile.hidden_discovered) {
      sList.push({
        id: "shd-hidden-reveal",
        type: "event",
        title: "Hidden Entrance Revealed",
        detail: "Found a seam in the ancient stone",
        source: "Discovery check",
        weight: 1.0,
      });
    }

    if (profile.whispers_heard > 0) {
      for (let i = 0; i < profile.whispers_heard; i++) {
        sList.push({
          id: `shd-whisper-${i}`,
          type: "event",
          title: `Whisper Heard #${i + 1}`,
          detail: "An echo from the deeper vault",
          source: "Dungeon Whispers",
          weight: 0.6,
        });
      }
    }

    return sList;
  }

  // Derive recalled boss taunt dialogue lines matching weaknesses
  const getRecalledDialogue = (newWhisper) => {
    const lines = [];
    if (!report?.profile) return lines;
    const profile = report.profile;

    if (profile.weak_topics) {
      profile.weak_topics.forEach((t) => {
        const text = BOSS_TAUNT_MAPPING.by_topic[t.toLowerCase()];
        if (text) {
          lines.push({
            id: `rd-topic-${t}`,
            speaker: "boss",
            name: "Vashkar",
            text,
            memory_ref: `shd-weak-${t}`,
          });
        }
      });
    }

    if (profile.weak_probes) {
      profile.weak_probes.forEach((p) => {
        const text = BOSS_TAUNT_MAPPING.by_probe[p];
        if (text) {
          lines.push({
            id: `rd-probe-${p}`,
            speaker: "boss",
            name: "Vashkar",
            text,
            memory_ref: `shd-probe-${p}`,
          });
        }
      });
    }

    if (newWhisper) {
      lines.push({
        id: "rd-new-whisper",
        speaker: "boss",
        name: "Vashkar",
        text: `I recall a whisper of your path: "${newWhisper}"`,
        memory_ref: "shd-whisper-new",
      });
    }

    return lines;
  };

  return (
    <GameContext.Provider
      value={{
        playerName,
        runId,
        runLevel,
        inHidden,
        hiddenLevel,
        discovery,
        report,
        challenge,
        loading,
        shards,
        journal,
        gaugeLevel,
        threatLevel,
        refreshReport,
        startGameSession,
        fetchNextChallenge,
        submitAnswerSession,
        exploreSession,
        enterHiddenSession,
        forgetSession,
        getRecalledDialogue,
      }}
    >
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error("useGame must be used within a GameProvider");
  }
  return context;
}
