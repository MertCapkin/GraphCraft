import { SafeAreaView, Text, View } from "react-native";

import { ButtonPrimary } from "../components/ButtonPrimary";
import { baseStyles } from "../theme";

export type LoginScreenProps = {
  onLogin?: () => void;
  onForgotPassword?: () => void;
};

/**
 * Login screen — maps to design/screens/login.example.yaml
 * @graphcraft implements screen:login
 */
export function LoginScreen({ onLogin, onForgotPassword }: LoginScreenProps) {
  return (
    <SafeAreaView style={baseStyles.screen}>
      <Text style={baseStyles.screenTitle}>Login</Text>
      <View style={{ gap: 12 }}>
        <ButtonPrimary label="Sign in" onPress={onLogin} />
        <ButtonPrimary
          label="Forgot password"
          onPress={onForgotPassword}
          style={{ backgroundColor: "transparent" }}
        />
      </View>
    </SafeAreaView>
  );
}
