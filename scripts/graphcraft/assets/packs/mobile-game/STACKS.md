# Mobile Game Pack

`profile: mobile-game` in `graphcraft.config.yaml`

## Supported stacks

| Stack | Scope | Notes |
|-------|-------|-------|
| unity-ugui | Meta-UI | Canvas, RectTransform, ScriptableObject themes |
| unity-ui-toolkit | Meta-UI | USS/UXML from tokens |
| godot | Meta-UI | Control nodes + theme resource |
| unreal-umg | Meta-UI | Widget blueprints + styles |
| defold | Meta-UI | GUI scenes |
| cocos | Meta-UI | Prefab UI |

## Scope limit

Stitch/design graph targets **meta-UI**: menus, HUD overlays, shop, inventory, dialogs.

Gameplay canvas art is out of GraphCraft v0.1 scope.

## Builder rules

- `stitch.scope: meta-ui-only` recommended
- Visual reference mode: PNG from `.stitch/designs/`
- Token → USS / ScriptableObject theme pipeline

## Asset library

Place sprites in `packages/assets/` with manifest YAML linking to components.
