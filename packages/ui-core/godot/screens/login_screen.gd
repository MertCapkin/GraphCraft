extends MarginContainer
class_name LoginScreen

## Login meta-UI — design/screens/login.example.yaml
## @graphcraft implements screen:login

@onready var _title: Label = $VBox/Title
@onready var _sign_in: ButtonPrimary = $VBox/SignIn
@onready var _forgot: ButtonPrimary = $VBox/ForgotPassword


func _ready() -> void:
	_apply_safe_area()
	add_theme_constant_override("margin_left", int(DesignTokens.SPACING_SCREEN_PADDING))
	add_theme_constant_override("margin_right", int(DesignTokens.SPACING_SCREEN_PADDING))
	add_theme_constant_override("margin_top", int(DesignTokens.SPACING_SCREEN_PADDING))
	add_theme_constant_override("margin_bottom", int(DesignTokens.SPACING_SCREEN_PADDING))

	if _title:
		_title.text = "Login"
		_title.add_theme_color_override("font_color", DesignTokens.COLOR_TEXT_PRIMARY)
	if _sign_in:
		_sign_in.text = "Sign in"
	if _forgot:
		_forgot.text = "Forgot password"


func _apply_safe_area() -> void:
	var safe := DisplayServer.get_display_safe_area()
	add_theme_constant_override("margin_left", int(safe.position.x) + int(DesignTokens.SPACING_SCREEN_PADDING))
	add_theme_constant_override("margin_top", int(safe.position.y) + int(DesignTokens.SPACING_SCREEN_PADDING))
