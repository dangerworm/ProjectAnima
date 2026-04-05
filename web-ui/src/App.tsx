import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import { useAnimaSocket } from './hooks/useAnimaSocket';
import { AnimaLayout } from './components/layout/AnimaLayout';

const theme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#0d0d14',
      paper: '#13131e',
    },
    primary: {
      main: '#7c8cff',
    },
    secondary: {
      main: '#9c6bcc',
    },
  },
  typography: {
    fontFamily: '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace',
  },
});

function App() {
  const [state, sendHumanInput] = useAnimaSocket();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AnimaLayout state={state} onSend={sendHumanInput} />
    </ThemeProvider>
  );
}

export default App;
