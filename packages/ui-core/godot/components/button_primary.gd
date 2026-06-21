extends Button
class_name ButtonPrimary

## Primary CTA — design-system/components/button.example.yaml
## @graphcraft component:button-primary

func _ready() -> void:
	custom_minimum_size.y = DesignTokens.TOUCH_TARGET_MIN
	add_theme_color_override("font_color", DesignTokens.COLOR_TEXT_PRIMARY)
	add_theme_stylebox_override("normal", _make_style(DesignTokens.COLOR_ACTION_PRIMARY))
	add_theme_stylebox_override("hover", _make_style(DesignTokens.COLOR_ACTION_SECONDARY))
	add_theme_stylebox_override("pressed", _make_style(DesignTokens.COLOR_ACTION_SECONDARY))


func _make_style(color: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.corner_radius_top_left = int(DesignTokens.RADIUS_DEFAULT)
	box.corner_radius_top_right = int(DesignTokens.RADIUS_DEFAULT)
	box.corner_radius_bottom_left = int(DesignTokens.RADIUS_DEFAULT)
	box.corner_radius_bottom_right = int(DesignTokens.RADIUS_DEFAULT)
	box.content_margin_left = DesignTokens.SPACING_BUTTON_PADDING
	box.content_margin_right = DesignTokens.SPACING_BUTTON_PADDING
	box.content_margin_top = DesignTokens.SPACING_BUTTON_PADDING
	box.content_margin_bottom = DesignTokens.SPACING_BUTTON_PADDING
	return box
