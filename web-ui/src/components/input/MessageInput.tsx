import { useState, KeyboardEvent } from 'react';
import { Box, TextField, IconButton, Chip } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface Props {
  onSend: (content: string) => void;
  connectionStatus: 'connecting' | 'connected' | 'disconnected';
}

const STATUS_COLOR: Record<Props['connectionStatus'], 'default' | 'success' | 'error'> = {
  connecting: 'default',
  connected: 'success',
  disconnected: 'error',
};

export function MessageInput({ onSend, connectionStatus }: Props) {
  const [value, setValue] = useState('');
  const disabled = connectionStatus !== 'connected';

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  }

  function handleKeyDown(e: KeyboardEvent<HTMLDivElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, p: 1 }}>
      <Chip
        label={connectionStatus}
        size="small"
        color={STATUS_COLOR[connectionStatus]}
        variant="outlined"
        sx={{ fontSize: '0.6rem', minWidth: 90 }}
      />
      <TextField
        fullWidth
        size="small"
        placeholder="Say something to Anima…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        multiline
        maxRows={4}
        variant="outlined"
      />
      <IconButton onClick={handleSend} disabled={disabled || !value.trim()} color="primary">
        <SendIcon />
      </IconButton>
    </Box>
  );
}
