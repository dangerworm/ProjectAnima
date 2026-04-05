import { Box, Paper, Typography, Chip } from '@mui/material';
import type { ActorState } from '../../types/messages';

interface Props {
  actor: ActorState;
}

const DISPLAY_NAMES: Record<string, string> = {
  temporal_core: 'Temporal Core',
  global_workspace: 'Global Workspace',
  perception: 'Perception',
  internal_state: 'Internal State',
  motivation: 'Motivation',
  memory: 'Memory',
  llm: 'LLM',
  self_narrative: 'Self-Narrative',
  expression: 'Expression',
};

function formatEventType(eventType: string): string {
  return eventType.toLowerCase().replace(/_/g, ' ');
}

export function ActorPanel({ actor }: Props) {
  const displayName = DISPLAY_NAMES[actor.name] ?? actor.name;
  const isActive = actor.lastUpdate !== null;

  return (
    <Paper
      variant="outlined"
      sx={{
        p: 1,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 0.5,
        borderColor: isActive ? 'primary.dark' : 'divider',
        bgcolor: isActive ? 'background.paper' : 'action.disabledBackground',
      }}
    >
      <Typography variant="caption" fontWeight="bold" noWrap>
        {displayName}
      </Typography>

      {actor.lastEventType ? (
        <>
          <Chip
            label={formatEventType(actor.lastEventType)}
            size="small"
            color="primary"
            variant="outlined"
            sx={{ fontSize: '0.6rem', height: 18 }}
          />
          {actor.lastSalience !== null && (
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
              salience {actor.lastSalience.toFixed(2)}
            </Typography>
          )}
        </>
      ) : (
        <Typography variant="caption" color="text.disabled" sx={{ fontSize: '0.65rem' }}>
          not yet connected
        </Typography>
      )}
    </Paper>
  );
}
