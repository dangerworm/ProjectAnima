// WebSocket message types — matches the protocol defined in core/main.py

export interface LanguageOutputMessage {
  type: 'language_output';
  content: string;
  thinking: string | null;
  in_response_to: string;
}

export interface ActorEventMessage {
  type: 'actor_event';
  actor: string;
  event_type: string;
  payload: Record<string, unknown>;
  final_salience: number;
}

export type ServerMessage = LanguageOutputMessage | ActorEventMessage;

export interface HumanInputMessage {
  type: 'human_input';
  content: string;
}

// Per-actor state maintained in the frontend store
export interface ActorState {
  name: string;
  lastEventType: string | null;
  lastSalience: number | null;
  lastUpdate: Date | null;
}

// The conversation feed
export interface ConversationTurn {
  role: 'human' | 'anima';
  content: string;
  timestamp: Date;
}
