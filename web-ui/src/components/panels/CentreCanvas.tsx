import { Box, Paper, Typography } from '@mui/material';

interface Props {
  thinkingContent: string | null;
}

export function CentreCanvas({ thinkingContent }: Props) {
  return (
    <Paper
      variant="outlined"
      sx={{
        height: '100%',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        bgcolor: '#0a0a0f',
        borderColor: 'divider',
      }}
    >
      <Typography
        variant="caption"
        color="text.disabled"
        sx={{ mb: 1, letterSpacing: 1, textTransform: 'uppercase', fontSize: '0.6rem' }}
      >
        Anima's reserved space
      </Typography>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {thinkingContent ? (
          <Typography
            variant="body2"
            component="pre"
            sx={{
              fontFamily: 'monospace',
              fontSize: '0.75rem',
              color: 'text.secondary',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              m: 0,
            }}
          >
            {thinkingContent}
          </Typography>
        ) : (
          <Typography variant="caption" color="text.disabled" sx={{ fontStyle: 'italic' }}>
            inner deliberation will appear here
          </Typography>
        )}
      </Box>
    </Paper>
  );
}
