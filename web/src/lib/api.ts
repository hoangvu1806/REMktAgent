const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8282";

const AGENT_API_BASE_URL =
  process.env.NEXT_PUBLIC_AGENT_API_BASE_URL ?? "http://127.0.0.1:8181";

export type AgentStreamEvent = {
  author: string | null;
  type: string;
  partial: boolean | null;
  text: string;
};

export type StreamCallbacks = {
  onEvent: (event: AgentStreamEvent) => void;
  onDone: () => void;
  onError: (error: string) => void;
};

/**
 * XHR-based POST streaming client.
 *
 * Uses XMLHttpRequest.onprogress to read SSE chunks incrementally as they
 * arrive from the network layer. This avoids the fetch ReadableStream pitfall
 * where reader.read() can return multiple SSE events in a single call,
 * causing React 18 to batch all resulting state updates into one render.
 *
 * The processedIndex/buffer pattern handles TCP chunk fragmentation: if a
 * JSON line is split across two TCP packets, the incomplete tail is held in
 * `buffer` and prepended to the next onprogress payload.
 */
export function streamAgentChat(
  userId: string,
  sessionId: string,
  message: string,
  callbacks: StreamCallbacks,
): void {
  const url = `${AGENT_API_BASE_URL}/agents/chat/stream`;

  const xhr = new XMLHttpRequest();
  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "text/event-stream");
  xhr.setRequestHeader("Cache-Control", "no-cache");

  let processedIndex = 0;
  let buffer = "";
  let isDone = false;

  xhr.onprogress = () => {
    const currentResponse = xhr.responseText;
    const newText = currentResponse.substring(processedIndex);
    processedIndex = currentResponse.length;

    buffer += newText;
    const lines = buffer.split("\n");

    // Hold back the last element — it may be an incomplete line split
    // across TCP boundaries.
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;

      const raw = trimmed.substring(6);

      if (raw === "[DONE]") {
        isDone = true;
        callbacks.onDone();
        return;
      }

      try {
        const event = JSON.parse(raw) as AgentStreamEvent;
        callbacks.onEvent(event);
      } catch {
        // Incomplete JSON fragment; will be completed on next onprogress.
      }
    }
  };

  xhr.onload = () => {
    // Process any remaining data left in the buffer after the connection closes.
    if (buffer.trim()) {
      const trimmed = buffer.trim();
      if (trimmed.startsWith("data: ")) {
        const raw = trimmed.substring(6);
        if (raw !== "[DONE]") {
          try {
            const event = JSON.parse(raw) as AgentStreamEvent;
            callbacks.onEvent(event);
          } catch {
            // Final fragment was not valid JSON; discard.
          }
        }
      }
    }
    if (!isDone) {
      callbacks.onDone();
    }
  };

  xhr.onerror = () => {
    callbacks.onError("Network error during streaming.");
  };

  xhr.send(
    JSON.stringify({
      user_id: userId,
      session_id: sessionId,
      message,
    }),
  );
}
