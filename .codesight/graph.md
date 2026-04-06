# Dependency Graph

## Most Imported Files (change these carefully)

- `web-ui\src\types\messages.ts` — imported by **4** files
- `web-ui\src\store\actorState.ts` — imported by **3** files
- `web-ui\src\hooks\useAnimaSocket.ts` — imported by **1** files
- `web-ui\src\components\layout\AnimaLayout.tsx` — imported by **1** files
- `web-ui\src\components\panels\ActorPanel.tsx` — imported by **1** files
- `web-ui\src\components\panels\CentreCanvas.tsx` — imported by **1** files
- `web-ui\src\components\panels\ExpressionPanel.tsx` — imported by **1** files
- `web-ui\src\components\input\MessageInput.tsx` — imported by **1** files
- `web-ui\src\App.tsx` — imported by **1** files

## Import Map (who imports what)

- `web-ui\src\types\messages.ts` ← `web-ui\src\components\panels\ActorPanel.tsx`, `web-ui\src\components\panels\ExpressionPanel.tsx`, `web-ui\src\hooks\useAnimaSocket.ts`, `web-ui\src\store\actorState.ts`
- `web-ui\src\store\actorState.ts` ← `web-ui\src\components\layout\AnimaLayout.tsx`, `web-ui\src\hooks\useAnimaSocket.ts`, `web-ui\src\hooks\useAnimaSocket.ts`
- `web-ui\src\hooks\useAnimaSocket.ts` ← `web-ui\src\App.tsx`
- `web-ui\src\components\layout\AnimaLayout.tsx` ← `web-ui\src\App.tsx`
- `web-ui\src\components\panels\ActorPanel.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\panels\CentreCanvas.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\panels\ExpressionPanel.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\components\input\MessageInput.tsx` ← `web-ui\src\components\layout\AnimaLayout.tsx`
- `web-ui\src\App.tsx` ← `web-ui\src\main.tsx`
