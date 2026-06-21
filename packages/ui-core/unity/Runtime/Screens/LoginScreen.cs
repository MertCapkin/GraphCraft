using UnityEngine;
using UnityEngine.UI;

namespace GraphCraft.UI
{
    /// <summary>
    /// Login meta-UI screen — design/screens/login.example.yaml
    /// @graphcraft implements screen:login
    /// </summary>
    public class LoginScreen : MonoBehaviour
    {
        public ButtonPrimary signInButton;
        public ButtonPrimary forgotPasswordButton;

        void Start()
        {
            ApplySafeAreaPadding();

            if (signInButton != null)
            {
                signInButton.SetLabel("Sign in");
            }
            if (forgotPasswordButton != null)
            {
                forgotPasswordButton.SetLabel("Forgot password");
            }
        }

        void ApplySafeAreaPadding()
        {
            var padding = Screen.safeArea;
            var rect = GetComponent<RectTransform>();
            if (rect == null)
            {
                return;
            }
            rect.offsetMin = new Vector2(padding.xMin, padding.yMin);
            rect.offsetMax = new Vector2(-(Screen.width - padding.xMax), -(Screen.height - padding.yMax));
        }
    }
}
