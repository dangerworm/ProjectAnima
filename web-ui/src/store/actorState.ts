import type { ActorState, ConversationTurn, ServerMessage } from '../types/messages';

// All known actor names — panels are shown in a fixed order
export const KNOWN_ACTORS = [
  'temporal_core',
  'global_workspace',
  'perception',
  'internal_state',
  'motivation',
  'memory',
  'llm',
  'self_narrative',
  'expression',
] as const;

export interface AppState {
  actors: Record<string, ActorState>;
  conversation: ConversationTurn[];
  thinkingContent: string | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
}

export type AppAction =
  | { type: 'SERVER_MESSAGE'; message: ServerMessage }
  | { type: 'HUMAN_SENT'; content: string }
  | { type: 'CONNECTION_STATUS'; status: AppState['connectionStatus'] };

export function initialState(): AppState {
  const actors: Record<string, ActorState> = {};
  for (const name of KNOWN_ACTORS) {
    actors[name] = { name, lastEventType: null, lastSalience: null, lastUpdate: null };
  }
  return {
    actors,
    conversation: [],
    thinkingContent: null,
    connectionStatus: 'connecting',
  };
}

export function reducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'CONNECTION_STATUS':
      return { ...state, connectionStatus: action.status };

    case 'HUMAN_SENT':
      return {
        ...state,
        conversation: [
          ...state.conversation,
          { role: 'human', content: action.content, timestamp: new Date() },
        ],
      };

    case 'SERVER_MESSAGE': {
      const msg = action.message;

      if (msg.type === 'language_output') {
        return {
          ...state,
          thinkingContent: msg.thinking,
          conversation: [
            ...state.conversation,
            { role: 'anima', content: msg.content, timestamp: new Date() },
          ],
        };
      }

      if (msg.type === 'actor_event') {
        const existing = state.actors[msg.actor] ?? {
          name: msg.actor,
          lastEventType: null,
          lastSalience: null,
          lastUpdate: null,
        };
        return {
          ...state,
          actors: {
            ...state.actors,
            [msg.actor]: {
              ...existing,
              lastEventType: msg.event_type,
              lastSalience: msg.final_salience,
              lastUpdate: new Date(),
            },
          },
        };
      }

      return state;
    }

    default:
      return state;
  }
}
