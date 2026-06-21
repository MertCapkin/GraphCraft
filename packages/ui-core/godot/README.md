# Godot UI Core

Godot 4 GDScript meta-UI primitives. Enable as editor plugin or copy scripts into your project.

| Design graph | File |
|--------------|------|
| `component:button-primary` | `components/button_primary.gd` |
| `screen:login` | `screens/login_screen.gd` |

```bash
graphcraft ui tokens emit godot
graphcraft ui validate godot
```

Attach `LoginScreen` to a `MarginContainer` with child `VBox` containing `Title` (Label), `SignIn`, `ForgotPassword` (`ButtonPrimary`).
