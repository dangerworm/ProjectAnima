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
  language: 'Language',
  self_narrative: 'Self-Narrative',
  expression: 'Expression',
};

const STATE_COLOURS: Record<string, 'success' | 'warning' | 'default'> = {
  active: 'success',
  chosen_silence: 'warning',
  dormant: 'default',
};

function formatEventType(eventType: string): string {
  return eventType.toLowerCase().replace(/_/g, ' ');
}

function formatSeconds(secs: number): string {
  if (secs >= 1e8) return '—';
  if (secs < 60) return `${Math.round(secs)}s`;
  if (secs < 3600) return `${Math.round(secs / 60)}m`;
  return `${(secs / 3600).toFixed(1)}h`;
}

function TemporalCoreStatus({ status }: { status: Record<string, unknown> }) {
  const state = status['state'] as string | undefined;
  const dormancySecs = status['dormancy_seconds'] as number | undefined;
  const colour = STATE_COLOURS[state ?? ''] ?? 'default';
  return (
    <>
      <Chip
        label={state?.replace('_', ' ') ?? 'unknown'}
        size="small"
        color={colour}
        variant="outlined"
        sx={{ fontSize: '0.6rem', height: 18 }}
      />
      {dormancySecs !== undefined && dormancySecs > 0 && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          dormant {formatSeconds(dormancySecs)}
        </Typography>
      )}
    </>
  );
}

function InternalStateStatus({ status }: { status: Record<string, unknown> }) {
  const timeSince = status['time_since_last_conversation_secs'] as number | undefined;
  const lag = status['consolidation_lag_secs'] as number | undefined;
  const depth = status['event_log_depth'] as number | undefined;
  return (
    <>
      {timeSince !== undefined && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          since conv: {formatSeconds(timeSince)}
        </Typography>
      )}
      {lag !== undefined && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          cons. lag: {formatSeconds(lag)}
        </Typography>
      )}
      {depth !== undefined && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          log depth: {depth}
        </Typography>
      )}
    </>
  );
}

function MotivationStatus({ status }: { status: Record<string, unknown> }) {
  const action = status['selected_action'] as string | undefined;
  const rests = status['consecutive_rests'] as number | undefined;
  const beliefs = status['beliefs'] as Record<string, number[]> | undefined;
  const topTension = beliefs
    ? beliefs['unresolved_tension'].indexOf(Math.max(...beliefs['unresolved_tension']))
    : null;
  const tensionLabels = ['none', 'low', 'moderate', 'high'];
  return (
    <>
      {action && (
        <Chip
          label={action.replace('_', ' ')}
          size="small"
          color="primary"
          variant="outlined"
          sx={{ fontSize: '0.6rem', height: 18 }}
        />
      )}
      {rests !== undefined && rests > 0 && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          rests: {rests}
        </Typography>
      )}
      {topTension !== null && (
        <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
          tension: {tensionLabels[topTension]}
        </Typography>
      )}
    </>
  );
}

export function ActorPanel({ actor }: Props) {
  const displayName = DISPLAY_NAMES[actor.name] ?? actor.name;
  const hasStatus = actor.status !== null;
  const hasEvent = actor.lastEventType !== null;
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

      {hasStatus && actor.name === 'temporal_core' && (
        <TemporalCoreStatus status={actor.status!} />
      )}

      {hasStatus && actor.name === 'internal_state' && (
        <InternalStateStatus status={actor.status!} />
      )}

      {hasStatus && actor.name === 'motivation' && (
        <MotivationStatus status={actor.status!} />
      )}

      {/* For actors without dedicated status rendering, fall back to last ignition event */}
      {!hasStatus && hasEvent && (
        <>
          <Chip
            label={formatEventType(actor.lastEventType!)}
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
      )}

      {!isActive && (
        <Typography variant="caption" color="text.disabled" sx={{ fontSize: '0.65rem' }}>
          idle
        </Typography>
      )}
    </Paper>
  );
}
