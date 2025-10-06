"""Standalone PyWebView process for displaying charts.

This module runs PyWebView in a separate process to avoid blocking
the Textual TUI event loop. PyWebView requires the main thread,
so we run it in its own process where it CAN be the main thread.
"""

import sys
import webview


def run_webview(html_content: str, title: str = "Portfolio Optimization Results") -> None:
    """
    Run PyWebView window in this process's main thread.

    Args:
        html_content: HTML string containing the visualization
        title: Window title
    """
    window = webview.create_window(
        title=title,
        html=html_content,
        width=1400,
        height=900,
        resizable=True,
        vibrancy=False,  # macOS: Disable for better performance
        background_color='#FFFFFF'
    )

    def on_loaded():
        """Confirm successful load."""
        print(f"[WebView Process] Visualization loaded")

    def on_closing():
        """Handle window closing."""
        print(f"[WebView Process] Closing visualization...")
        return True

    def on_closed():
        """Cleanup after close."""
        print(f"[WebView Process] Visualization closed")

    # Subscribe to events
    window.events.loaded += on_loaded
    window.events.closing += on_closing
    window.events.closed += on_closed

    # Start GUI loop (blocks until window closes)
    # This is fine because this entire PROCESS is dedicated to the webview
    webview.start()


if __name__ == "__main__":
    # This script is meant to be run as a separate process
    # Expects HTML content via stdin or as base64 encoded argument

    if len(sys.argv) > 1:
        # HTML content passed as argument (base64 encoded)
        import base64
        html_b64 = sys.argv[1]
        title = sys.argv[2] if len(sys.argv) > 2 else "Portfolio Optimization Results"
        html_content = base64.b64decode(html_b64).decode('utf-8')
        run_webview(html_content, title)
    else:
        # Read HTML from stdin
        print("[WebView Process] Reading HTML from stdin...", file=sys.stderr)
        html_content = sys.stdin.read()
        run_webview(html_content)
