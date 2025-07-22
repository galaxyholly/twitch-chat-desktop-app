# Twitch Chat Desktop Monitor (Learning Project)
## Overview

Built as an exploration into real-time applications and concurrent programming, this desktop monitor demonstrates async programming patterns with GUI frameworks.

<img width="375" height="668" alt="image" src="https://github.com/user-attachments/assets/e6311ede-f068-488a-9b51-de32f039a1d3" />

## Key Features

- **Real-time Chat Monitoring**: Live display of Twitch chat messages with OAuth authentication
- **Multi-threaded Architecture**: Separation of GUI rendering and async chat processing
- **Custom Qt Interface**: Scrolling chat display with color-coded usernames
- **Thread-Safe Communication**: Signal/slot pattern for cross-thread messaging
- **Environment Configuration**: Secure credential management with dotenv

## Technical Highlights

- **Async/Await Integration**: Coordinates Twitch API's async patterns with Qt's event loop
- **Threading Design**: GUI thread handles display while worker thread manages chat connection
- **Real-time Data Processing**: Handles continuous chat message streams
- **OAuth Flow Implementation**: Twitch API authentication and token management

## Architecture

**Main Thread (Qt GUI)**
- Handles user interface rendering and interactions
- Manages chat display with auto-scrolling message list
- Processes user input from message entry field
- Communicates with worker thread via Qt signals/slots

**Worker Thread (Async Chat)**
- Maintains persistent connection to Twitch chat servers
- Handles OAuth authentication flow and token management
- Processes incoming chat messages in real-time
- Emits signals to main thread for UI updates

**Data Layer**
- Environment variables manage API credentials securely
- Message objects passed between threads contain user/text/metadata

**Communication Pattern**
- Qt signals/slots provide thread-safe message passing
- Worker thread emits incoming message signals to GUI
- No shared state between threads, only signal-based communication

## Technical Stack
- Python 3.13+
- PySide6 (Qt for Python)
- TwitchAPI
- SQLite3
