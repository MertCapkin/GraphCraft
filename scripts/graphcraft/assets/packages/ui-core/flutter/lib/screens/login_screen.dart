import 'package:flutter/material.dart';

import '../components/button_primary.dart';
import '../tokens.dart';

/// Login screen — design/screens/login.example.yaml
/// @graphcraft implements screen:login
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key, this.onLogin, this.onForgotPassword});

  final VoidCallback? onLogin;
  final VoidCallback? onForgotPassword;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: DesignTokens.colorBgDefault,
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(DesignTokens.spacingScreenPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Login',
                style: TextStyle(
                  color: DesignTokens.colorTextPrimary,
                  fontSize: 24,
                  fontWeight: FontWeight.w600,
                ),
              ),
              SizedBox(height: DesignTokens.spacingScreenPadding),
              ButtonPrimary(label: 'Sign in', onPressed: onLogin),
              const SizedBox(height: 12),
              ButtonPrimary(label: 'Forgot password', onPressed: onForgotPassword),
            ],
          ),
        ),
      ),
    );
  }
}
