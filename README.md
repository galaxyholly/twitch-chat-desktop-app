# Twitch Chat Desktop Monitor (Learning Project)

A real-time Twitch chat monitoring application built with Python and Qt, demonstrating async programming and threading concepts.

## Features
- Real-time chat monitoring with OAuth authentication
- Multi-threaded architecture (GUI + async chat handling)
- Color-coded usernames for better readability
- Auto-scrolling chat display
- Environment variable configuration

## Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Add your Twitch API credentials to `.env`
5. Run: `python bot.py`

## Learning Outcomes
This project taught me valuable lessons about async programming and thread management in GUI applications. Built during my exploration of real-time applications and API integration.

## Technical Stack
- Python 3.13+
- PySide6 (Qt for Python)
- TwitchAPI
- SQLite3
