# ADR-0001: Use Multiprocessing for PyWebView

**Status**: Accepted

**Date**: 2024-01-15

**Deciders**: Development Team

## Context

Terminal Portfolio Optimizer needs to display interactive Plotly charts using PyWebView while maintaining a responsive Textual TUI. Both frameworks have strict main thread requirements:

1. **Textual** runs an async event loop on the main thread for terminal rendering and event handling
2. **PyWebView** requires `webview.start()` to run on the main thread due to macOS Cocoa/NSWindow constraints

Initial attempts to call `webview.start()` from Textual's event loop or worker threads resulted in:
- **Deadlock**: PyWebView blocks waiting for window close, freezing the TUI
- **Threading errors**: PyWebView crashes when called from non-main threads on macOS
- **Poor UX**: No way to return control to TUI while chart window is open

## Decision

We will run PyWebView in a **separate process** rather than a thread, using Python's `subprocess` module:

1. Create standalone script `src/webview_process.py` that runs PyWebView
2. Launch this script using `subprocess.Popen()` from a Textual worker thread
3. Pass HTML content via base64-encoded command-line argument
4. Worker thread calls `process.wait()` (non-blocking for worker, doesn't block main TUI thread)
5. When user closes chart window, subprocess terminates and worker resumes

## Consequences

### Positive

- **Main thread isolation**: PyWebView gets its own main thread in separate process, satisfying macOS Cocoa requirements
- **No deadlock**: Textual's main thread remains free to handle UI events
- **Clean lifecycle**: Window close automatically terminates subprocess, no manual cleanup
- **Process isolation**: Chart rendering crashes won't crash the main TUI application
- **Scalability**: Could launch multiple chart windows concurrently if needed

### Negative

- **Process spawn overhead**: ~1-2 seconds to launch subprocess (acceptable for user workflow)
- **No direct memory sharing**: Must serialize HTML data for inter-process communication
- **Platform differences**: Process behavior differs slightly between macOS/Linux (generally acceptable)
- **Debugging complexity**: Two separate processes make debugging slightly harder

### Risks

- **Process zombies**: If parent process crashes, child might not terminate
  - *Mitigation*: Use context managers and proper signal handling
- **Memory usage**: Separate process has its own memory space (~50MB overhead)
  - *Mitigation*: Acceptable for desktop application, terminates after use

## Alternatives Considered

### Option 1: Threading with `webview.create_window()` + `webview.start()` on main thread

**Approach**: Move Textual to a background thread, give PyWebView the main thread

**Pros**:
- No process spawn overhead
- Shared memory space

**Cons**:
- Textual also requires main thread for terminal control
- Would require major architectural refactor
- Still results in deadlock (both need main thread)

**Reason for rejection**: Both frameworks need main thread - threading cannot solve this

### Option 2: Use Tkinter or PyQt for chart display

**Approach**: Replace PyWebView with native GUI toolkit

**Pros**:
- Better thread control
- More mature libraries

**Cons**:
- Tkinter has poor Plotly integration (no native HTML rendering)
- PyQt is heavyweight dependency (~100MB)
- Would require rewriting visualization layer
- Less web-native (Plotly optimized for browsers)

**Reason for rejection**: PyWebView is lightweight and Plotly-optimized

### Option 3: Save chart to HTML file and open in browser

**Approach**: Write HTML to temp file, use `webbrowser.open()`

**Pros**:
- No additional dependencies
- Works on all platforms

**Cons**:
- Poor UX: Opens external browser, leaves tabs open
- No control over window lifecycle
- Clutters user's browser history
- Temporary file management required

**Reason for rejection**: Suboptimal user experience

### Option 4: Export chart as static image (PNG/SVG)

**Approach**: Use Plotly's `.write_image()` and display in terminal

**Pros**:
- No GUI framework needed
- Simpler architecture

**Cons**:
- Loss of interactivity (no zoom, hover, pan)
- Terminal image display is limited (sixel/iTerm2 only)
- Static images less useful for portfolio analysis

**Reason for rejection**: Interactive charts are core value proposition

## Implementation Details

### Subprocess Architecture

```python
# src/visualizer.py:381-416
def display_charts(html_content: str) -> None:
    html_b64 = base64.b64encode(html_content.encode()).decode()

    process = subprocess.Popen([
        sys.executable,
        str(webview_process_path),
        html_b64
    ])

    process.wait()  # Non-blocking for worker thread
```

```python
# src/webview_process.py:1-25
def main():
    html_b64 = sys.argv[1]
    html = base64.b64decode(html_b64).decode()

    webview.create_window('Portfolio Optimization', html=html)
    webview.start()  # Runs on subprocess's main thread
```

### Threading Model

```
Main Thread (Textual)
  ↓
Spawn Worker Thread (@work decorator)
  ↓
Worker Thread calls subprocess.Popen()
  ↓
Subprocess gets own Main Thread
  ↓
webview.start() runs on subprocess main thread
  ↓
User closes window → subprocess exits → worker resumes
  ↓
Worker updates UI via call_from_thread()
  ↓
Main Thread shows success message
```

## References

- PyWebView threading requirements: https://pywebview.flowrl.com/guide/api.html#start
- Textual async architecture: https://textual.textualize.io/guide/workers/
- Python subprocess documentation: https://docs.python.org/3/library/subprocess.html
- Related: [ADR-0002: Worker Thread Pattern](./0002-worker-thread-pattern.md)
- Related: [ADR-0003: Base64 Encoding for Subprocess Communication](./0003-base64-subprocess-communication.md)
