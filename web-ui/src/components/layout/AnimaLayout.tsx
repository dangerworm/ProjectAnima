import { Box } from '@mui/material';
import type { AppState } from '../../store/actorState';
import { ActorPanel } from '../panels/ActorPanel';
import { CentreCanvas } from '../panels/CentreCanvas';
import { ExpressionPanel } from '../panels/ExpressionPanel';
import { MessageInput } from '../input/MessageInput';

interface Props {
  state: AppState;
  onSend: (content: string) => void;
}

// Panel height constants (vh-based to fill the viewport)
const TOP_ROW_H = '18vh';
const MAIN_ROW_H = '55vh';
const BOTTOM_ROW_H = '18vh';
const SIDE_COL_W = '140px';

export function AnimaLayout({ state, onSend }: Props) {
  const a = state.actors;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', p: 1, gap: 1, bgcolor: '#0d0d14' }}>

      {/* ── Top row: actor panels ── */}
      <Box sx={{ display: 'flex', gap: 1, height: TOP_ROW_H, flexShrink: 0 }}>
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0 }}>
          <ActorPanel actor={a.temporal_core} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <ActorPanel actor={a.global_workspace} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <ActorPanel actor={a.perception} />
        </Box>
        {/* Internal State + Motivation stacked in the top-right corner */}
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box sx={{ flex: 1 }}>
            <ActorPanel actor={a.internal_state} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <ActorPanel actor={a.motivation} />
          </Box>
        </Box>
      </Box>

      {/* ── Main row: side columns + centre canvas ── */}
      <Box sx={{ display: 'flex', gap: 1, flex: 1, minHeight: 0 }}>

        {/* Left column: Memory + Language */}
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Box sx={{ flex: 1 }}>
            <ActorPanel actor={a.memory} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <ActorPanel actor={a.language} />
          </Box>
        </Box>

        {/* Centre: Anima's reserved space */}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <CentreCanvas thinkingContent={state.thinkingContent} />
        </Box>

        {/* Right column: Self-Narrative */}
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0 }}>
          <ActorPanel actor={a.self_narrative} />
        </Box>
      </Box>

      {/* ── Bottom row: Expression panel + input ── */}
      <Box sx={{ display: 'flex', gap: 1, height: BOTTOM_ROW_H, flexShrink: 0 }}>
        {/* Spacer matching left column width */}
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0 }} />

        {/* Expression panel + input stacked */}
        <Box sx={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Box sx={{ flex: 1, minHeight: 0 }}>
            <ExpressionPanel conversation={state.conversation} />
          </Box>
          <MessageInput onSend={onSend} connectionStatus={state.connectionStatus} />
        </Box>

        {/* Spacer matching right column width */}
        <Box sx={{ width: SIDE_COL_W, flexShrink: 0 }} />
      </Box>

    </Box>
  );
}
