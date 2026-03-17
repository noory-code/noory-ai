"""Cross-platform notification utility for evonest phase completion."""

from __future__ import annotations

import platform
import subprocess


def notify(title: str, message: str) -> None:
    """Send a desktop notification. No-op if unsupported or unavailable."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(
                ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
                timeout=3,
                capture_output=True,
            )
        elif system == "Linux":
            subprocess.run(
                ["notify-send", title, message],
                timeout=3,
                capture_output=True,
            )
        elif system == "Windows":
            # PowerShell toast notification (built-in, no extra packages)
            ps_script = (
                "[Windows.UI.Notifications.ToastNotificationManager, "
                "Windows.UI.Notifications, ContentType = WindowsRuntime] > $null; "
                "$template = [Windows.UI.Notifications.ToastNotificationManager]::"
                "GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::"
                "ToastText02); "
                "$textNodes = $template.GetElementsByTagName('text'); "
                f"$textNodes.Item(0).AppendChild($template.CreateTextNode('{title}')) > $null; "
                f"$textNodes.Item(1).AppendChild($template.CreateTextNode('{message}')) > $null; "
                "$toast = [Windows.UI.Notifications.ToastNotification]::new($template); "
                "[Windows.UI.Notifications.ToastNotificationManager]::"
                "CreateToastNotifier('Evonest').Show($toast)"
            )
            subprocess.run(
                ["powershell", "-Command", ps_script],
                timeout=5,
                capture_output=True,
            )
    except Exception:
        pass  # never crash the main flow
