import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  ViewStyle,
} from "react-native";

import { TOUCH_TARGET_MIN, tokens } from "../tokens";

export type ButtonPrimaryProps = {
  label: string;
  onPress?: () => void;
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
};

/**
 * Primary CTA — max one per screen (see design-system/components/button.example.yaml)
 * @graphcraft component:button-primary
 */
export function ButtonPrimary({
  label,
  onPress,
  disabled = false,
  loading = false,
  style,
}: ButtonPrimaryProps) {
  const isDisabled = disabled || loading;

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      disabled={isDisabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.base,
        pressed && !isDisabled && styles.pressed,
        isDisabled && styles.disabled,
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={tokens.color.text.primary} />
      ) : (
        <Text style={styles.label}>{label}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: TOUCH_TARGET_MIN,
    paddingHorizontal: tokens.spacing.button.padding * 2,
    paddingVertical: tokens.spacing.button.padding,
    backgroundColor: tokens.color.action.primary,
    borderRadius: tokens.radius.default,
    alignItems: "center",
    justifyContent: "center",
  },
  pressed: {
    backgroundColor: tokens.color.action.secondary,
  },
  disabled: {
    opacity: 0.5,
  },
  label: {
    color: tokens.color.text.primary,
    fontSize: 16,
    fontWeight: "600",
  },
});
