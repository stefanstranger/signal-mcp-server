# 📱 signal-mcp-server

MCP Server for retrieving Signal messages using signal-export logic.

## 🎯 Overview

This MCP server enables AI agents and tools to access Signal Desktop chat messages and attachments via the Model Context Protocol (MCP).

## 🛠️ Features

- Retrieve Signal messages from your local Signal Desktop database
- List all Signal chats with contact details and message counts
- Filter messages by chat/contact name
- Paginate through message history with offset and limit
- Support for multiple operating systems (Windows, macOS, Linux)
- Handle encrypted Signal databases

## 📋 Prerequisites

- Python 3.13 or higher
- UV package manager
- Signal Desktop installed with existing message database
- Node.js and npm (for MCP inspector tools)
- Windows, macOS, or Linux operating system

### 1. Signal Desktop

- **Official Download Page:**  
  [https://signal.org/download/](https://signal.org/download/)

- **Direct Download Links:**  
  - [Windows](https://signal.org/download/windows/)  
  - [Mac](https://signal.org/download/macos/)  
  - [Linux (Debian-based)](https://signal.org/download/linux/)

> **Note:** Signal Desktop requires Signal to be installed on your phone for initial setup.

---

### 2. Python

- **Official Download Page:**  
  [https://www.python.org/downloads/](https://www.python.org/downloads/)

- **Direct Download for Python 3.13.5:**  
  [Python 3.13.5 Release Page](https://www.python.org/downloads/release/python-3135/)

- Download the installer for your OS (Windows, macOS, Linux) and follow the setup instructions.

---

### 3. UV (Python Package Manager)

- **Official Documentation & Source:**  
  [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv)  
  [UV Documentation](https://docs.astral.sh/uv/)

- **Installation (Windows):**
  ```powershell
  irm https://astral.sh/uv/install.ps1 | iex
  ```
  Or, using pip (if you already have Python and pip installed):
  ```powershell
  pip install uv
  ```

- **Installation (macOS/Linux):**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

- **More Info:**  
  [UV Installation Guide](https://docs.astral.sh/uv/getting-started/installation/)

### 4. Claude Desktop

- **Official Download Page:**  
  [https://claude.ai/download](https://claude.ai/download)

- Download the installer for your OS (Windows, macOS) and follow the setup instructions.

## 🚀 Installation Signal MCP Server

1. Clone the repository:
   ```powershell
   git clone https://github.com/stefanstranger/signal-mcp-server.git
   cd signal-mcp-server
   ```

2. Create a virtual environment:
   ```powershell
   uv venv .venv --python 3.13
   ```

3. Activate the virtual environment:
   - **Windows PowerShell:**
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```powershell
   uv pip install fastmcp signal-export
   ```

## ⚙️ Configuration

### 🔧 Claude Desktop Setup

Usage with Claude Desktop
Add the following to your claude_desktop_config.json file:

```json
{
  "mcpServers": {
    "signal-mcp-server": {
         "type": "stdio",
         "command": "uv",
         "args": [
            "run",
            "--with",
            "mcp[cli]",
            "--with",
            "signal-export",
            "mcp",
            "run",
            "C:\\Github\\signal-mcp-server\\server.py"
         ]
    }
  }
}
```

### Signal Data Directory

The server automatically detects your Signal data directory based on your operating system:

- **Windows**: `%APPDATA%\Signal`
- **macOS**: `~/Library/Application Support/Signal`
- **Linux**: `~/.config/Signal` (or Flatpak: `~/.var/app/org.signal.Signal/config/Signal`)

### Encryption

If your Signal database is encrypted, you may need to provide:
- `password`: Database password (if set)
- `key`: Encryption key (if required)

## 🏃 Running the Server

### Start MCP Server

```powershell
uv run .\server.py
```

### Inspect MCP Server

Using the MCP Inspector:
```powershell
npx @modelcontextprotocol/inspector uv run --with mcp[cli] mcp run c://github//signal-mcp-server//server.py
```

Using mcptools:
```powershell
mcptools web cmd /c "uv.exe run --with mcp[cli] --with signal-export mcp run c:\\github\\signal-mcp-server\\server.py"
```

## 📖 Available Tools

### 1. `signal_list_chats`
Lists all Signal chats with their details.

**Parameters:**
- `source_dir` (optional): Custom Signal data directory path
- `password` (optional): Database password
- `key` (optional): Encryption key
- `include_empty` (optional): Include chats with no messages
- `include_disappearing` (optional): Include disappearing messages

**Example Response:**
```json
[
  {
    "name": "John Doe",
    "number": "+1234567890",
    "ServiceId": "abc123...",
    "total_messages": 150
  }
]
```

### 2. `signal_get_chat_messages`
Retrieves messages from a specific chat by name.

**Parameters:**
- `chat_name` (required): Name of the chat contact
- `limit` (optional): Maximum number of messages to return
- `offset` (optional): Number of messages to skip (for pagination)
- Other parameters same as `signal_list_chats`

**Example Response:**
```json
[
  {
    "date": "2025-07-31T10:30:00",
    "sender": "John Doe",
    "body": "Hello! How are you?",
    "quote": "",
    "reactions": [],
    "attachments": []
  }
]
```

### 3. `signal_search_chat`
Search for specific text within Signal chat messages.

**Parameters:**
- `chat_name` (required): Name of the chat to search within
- `query` (required): Text to search for in message bodies
- `limit` (optional): Maximum number of matching messages to return
- `source_dir` (optional): Custom Signal data directory path
- `password` (optional): Database password
- `key` (optional): Encryption key
- `include_empty` (optional): Include chats with no messages
- `include_disappearing` (optional): Include disappearing messages

**Example Response:**
```json
[
  {
    "date": "2025-07-31T10:30:00",
    "sender": "John Doe", 
    "body": "Let's meet at the coffee shop tomorrow",
    "quote": "",
    "reactions": [],
    "attachments": []
  }
]
```

## 🎯 Available Prompts

The server includes pre-built prompts for common analysis tasks:

### 1. `signal_summarize_chat_prompt`
Generate a summary prompt for recent messages in a specific chat.

### 2. `signal_chat_topic_prompt` 
Generate a prompt to analyze discussion topics in a chat.

### 3. `signal_chat_sentiment_prompt`
Generate a prompt to analyze message sentiment in a chat.

### 4. `signal_search_chat_prompt`
Generate a search prompt for finding specific text in a chat.

## 💡 Usage Examples

### List all chats
```
"List all Signal chats please"
```

### Get recent messages from a specific chat
```
"Show me the last 10 messages from the Family group chat"
```

### Search for topics in a chat
```
"What are the main topics discussed in the Work Team chat?"
```

### Summarize conversations
```
"Summarize the recent conversation with John Doe"
```

### Search within a chat
```
"Search for messages containing 'meeting' in the Work Team chat"
```

### Analyze chat sentiment
```
"Analyze the sentiment of recent messages with Sarah"
```

## 🔒 Security & Privacy

⚠️ **Important**: This server provides access to your personal Signal messages. Please:

- Only run this server locally
- Never expose it to the internet
- Be cautious about which AI agents you grant access
- Consider the privacy of others in your conversations
- Delete any exported data when no longer needed

## 🐛 Troubleshooting

### Common Issues

1. **"Signal database not found"**
   - Ensure Signal Desktop is installed
   - Check if the data directory path is correct
   - Verify you have read permissions

2. **"Database is encrypted"**
   - Signal databases may be encrypted on some systems
   - You may need to provide encryption credentials

3. **"No messages found"**
   - Verify the chat name is spelled correctly
   - Check if the chat has any messages
   - Try using `include_empty=True` parameter

4. **"Signal-MCP-Server does not want to start in Claude Desktop"**
   - Check if there are no other Python versions installed besides the recommended version 3.13.
   - You may need to uninstall older Python versions installed.

## 📚 References

- [signal-export](https://github.com/carderne/signal-export)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Create MCP Server](https://github.com/modelcontextprotocol/create-python-server)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [MCP Tools](https://github.com/mcptools/mcptools)

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚖️ Disclaimer

This tool is not affiliated with or endorsed by Signal. Use at your own risk and respect the privacy of your conversations.