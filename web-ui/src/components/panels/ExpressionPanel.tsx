import { useEffect, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import type { ConversationTurn } from '../../types/messages';

interface Props {
  conversation: ConversationTurn[];
}

export function ExpressionPanel({ conversation }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation]);

  return (
    <Paper
      variant="outlined"
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        borderColor: 'divider',
      }}
    >
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 1.5,
          display: 'flex',
          flexDirection: 'column',
          gap: 1,
        }}
      >
        {conversation.length === 0 ? (
          <Typography variant="caption" color="text.disabled" sx={{ fontStyle: 'italic' }}>
            No messages yet.
          </Typography>
        ) : (
          conversation.map((turn, i) => (
            <Box key={i} sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}>
              <Typography
                variant="caption"
                color={turn.role === 'human' ? 'primary.light' : 'secondary.light'}
                fontWeight="bold"
                sx={{ textTransform: 'uppercase', fontSize: '0.6rem', letterSpacing: 1 }}
              >
                {turn.role === 'human' ? 'You' : 'Anima'}
              </Typography>
              <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>
                {turn.content}
              </Typography>
            </Box>
          ))
        )}
        <div ref={bottomRef} />
      </Box>
    </Paper>
  );
}
