import 'package:flutter/material.dart';

import '../tokens.dart';

/// Primary CTA — max one per screen (design-system/components/button.example.yaml)
/// @graphcraft component:button-primary
class ButtonPrimary extends StatelessWidget {
  const ButtonPrimary({
    super.key,
    required this.label,
    this.onPressed,
    this.loading = false,
  });

  final String label;
  final VoidCallback? onPressed;
  final bool loading;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: loading ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: DesignTokens.colorActionPrimary,
          foregroundColor: DesignTokens.colorTextPrimary,
          minimumSize: Size(0, DesignTokens.touchTargetMin),
          padding: EdgeInsets.symmetric(
            horizontal: DesignTokens.spacingButtonPadding * 2,
            vertical: DesignTokens.spacingButtonPadding,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(DesignTokens.radiusDefault),
          ),
        ),
        child: loading
            ? SizedBox(
                height: 20,
                width: 20,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: DesignTokens.colorTextPrimary,
                ),
              )
            : Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
      ),
    );
  }
}
