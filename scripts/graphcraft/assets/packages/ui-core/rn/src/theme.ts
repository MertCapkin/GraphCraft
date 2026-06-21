import { StyleSheet } from "react-native";

import { tokens } from "./tokens";

export const theme = {
  colors: tokens.color,
  spacing: tokens.spacing,
  radius: tokens.radius,
};

export const baseStyles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: tokens.color.bg.default,
    padding: tokens.spacing.screen.padding,
  },
  screenTitle: {
    color: tokens.color.text.primary,
    fontSize: 24,
    fontWeight: "600",
    marginBottom: tokens.spacing.screen.padding,
  },
});
