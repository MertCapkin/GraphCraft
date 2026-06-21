using UnityEngine;
using UnityEngine.UI;

namespace GraphCraft.UI
{
    /// <summary>
    /// Primary CTA — design-system/components/button.example.yaml
    /// @graphcraft component:button-primary
    /// </summary>
    [RequireComponent(typeof(Button))]
    [RequireComponent(typeof(LayoutElement))]
    public class ButtonPrimary : MonoBehaviour
    {
        public Text labelText;
        public Button button;

        void Reset()
        {
            button = GetComponent<Button>();
            var le = GetComponent<LayoutElement>();
            le.minHeight = DesignTokens.TouchTargetMin;

            if (ColorUtility.TryParseHtmlString(DesignTokens.ColorActionPrimary, out var primary))
            {
                var colors = button.colors;
                colors.normalColor = primary;
                button.colors = colors;
            }

            var image = GetComponent<Image>();
            if (image != null && ColorUtility.TryParseHtmlString(DesignTokens.ColorActionPrimary, out var bg))
            {
                image.color = bg;
            }
        }

        public void SetLabel(string text)
        {
            if (labelText != null)
            {
                labelText.text = text;
            }
        }
    }
}
