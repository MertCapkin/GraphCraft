# Mobile App Pack

`profile: mobile-app` in `graphcraft.config.yaml`

## Supported stacks

| Stack | UI lib path | Notes |
|-------|-------------|-------|
| react-native | packages/ui-core/rn/ | StyleSheet + tokens |
| expo | packages/ui-core/expo/ | Expo Router screens |
| flutter | packages/ui-core/flutter/ | ThemeData from tokens.json |
| swiftui | packages/ui-core/swiftui/ | Asset catalog + SwiftUI Theme |
| jetpack-compose | packages/ui-core/compose/ | Material3 + custom tokens |
| kotlin-multiplatform | packages/ui-core/kmp/ | Shared theme module |
| ionic | packages/ui-core/ionic/ | CSS variables from tokens |
| capacitor | packages/ui-core/capacitor/ | Web + native shell |

## Builder rules

- Consume tokens from `design-system/tokens.json`
- Map design graph `component:*` to package components
- Navigation follows `navigates_to` edges in design graph

## Design graph query

```bash
python -m graphcraft design query "screens"
```
