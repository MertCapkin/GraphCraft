# React Native UI Core

GraphCraft design graph → React Native components.

## Components

| Design graph id | Source |
|-----------------|--------|
| `component:button-primary` | `src/components/ButtonPrimary.tsx` |
| `screen:login` | `src/screens/LoginScreen.tsx` |

## Usage

Copy or link this package into your Expo / RN app:

```tsx
import { ButtonPrimary, LoginScreen, tokens } from "@graphcraft/ui-core-rn";
```

## Token sync

```bash
graphcraft ui tokens emit rn
graphcraft ui validate rn
```

## Rules

- No hardcoded colors outside `tokens.ts`
- Each component file must include `@graphcraft component:…` or `@graphcraft implements screen:…`
- Min touch target: 44px (`TOUCH_TARGET_MIN`)
