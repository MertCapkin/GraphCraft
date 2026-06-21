/**
 * Semantic design tokens — design-system/tokens.json
 * Regenerate: graphcraft ui tokens emit rn
 */
export const tokens = {
  color: {
    action: {
      primary: "#6366F1",
      secondary: "#8B5CF6",
    },
    bg: {
      default: "#0F172A",
      elevated: "#1E293B",
    },
    text: {
      primary: "#F8FAFC",
      muted: "#94A3B8",
    },
  },
  spacing: {
    screen: {
      padding: 16,
    },
    button: {
      padding: 12,
    },
  },
  radius: {
    default: 8,
  },
} as const;

export type DesignTokens = typeof tokens;

export const TOUCH_TARGET_MIN = 44;
