from dataclasses import asdict
from pathlib import Path
from datetime import datetime
import sigexport.data
import sigexport
from typing import Optional, List, Dict, Any
import platform
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Signal MCP Server", "0.1.0")


def get_default_signal_dir() -> Path:
    home = Path.home()
    system = platform.system()
    if system == "Windows":
        return home / "AppData" / "Roaming" / "Signal"
    elif system == "Darwin":
        return home / "Library" / "Application Support" / "Signal"
    elif system == "Linux":
        # Check for Flatpak first
        flatpak_path = home / ".var" / "app" / "org.signal.Signal" / "config" / "Signal"
        if flatpak_path.exists():
            return flatpak_path
        return home / ".config" / "Signal"
    else:
        raise RuntimeError(f"Unsupported OS: {system}")


@mcp.tool()
def list_chats(
    source_dir: Path = get_default_signal_dir(),
    password: Optional[str] = None,
    key: Optional[str] = None,
    chats: str = "",
    include_empty: bool = False,
    include_disappearing: bool = True
) -> List[Dict[str, Any]]:
    """
    List all chats with their details.
    Args:
        source_dir (Path): Path to the Signal data directory.
        password (Optional[str]): Password for encrypted data, if applicable.
        key (Optional[str]): Key for encrypted data, if applicable.
        chats (str): Comma-separated list of chat IDs to filter.
        include_empty (bool): Whether to include empty chats.
        include_disappearing (bool): Whether to include disappearing messages.
       
        Returns:
        List[Dict[str, Any]]: A list of dictionaries containing chat details.
        """
    convos, contacts, self_contact = sigexport.data.fetch_data(
        source_dir=source_dir,
        password=password,
        key=key,
        chats=chats,
        include_empty=include_empty,
        include_disappearing=include_disappearing
    )
    output = []
    for chat_id in convos:
        contact = contacts.get(chat_id)
        if contact:
            contact_dict = asdict(contact)
            contact_dict["ServiceId"] = contact_dict.pop("serviceId")
            contact_dict["total_messages"] = len(convos[chat_id])
            output.append(contact_dict)
    return output


@mcp.tool()
def get_chat_messages(
    chat_name: str,
    source_dir: Path = get_default_signal_dir(),
    password: Optional[str] = None,
    key: Optional[str] = None,
    chats: str = "",
    include_empty: bool = False,
    include_disappearing: bool = True
) -> List[Dict[str, Any]]:
    """
    Get messages from a specific chat by name.
    Args:
        chat_name (str): The name of the chat to retrieve messages from.
        source_dir (Path): Path to the Signal data directory.
        password (Optional[str]): Password for encrypted data, if applicable.
        key (Optional[str]): Key for encrypted data, if applicable.
        chats (str): Comma-separated list of chat IDs to filter.
        include_empty (bool): Whether to include empty chats.
        include_disappearing (bool): Whether to include disappearing messages.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing messages from the specified chat. 
    """
    convos, contacts, self_contact = sigexport.data.fetch_data(
        source_dir=source_dir,
        password=password,
        key=key,
        chats=chats,
        include_empty=include_empty,
        include_disappearing=include_disappearing
    )

    chat_messages = []
    for chat_id, messages in convos.items():
        contact = contacts.get(chat_id)
        if contact and contact.name == chat_name:
            for msg in messages:
                msg_dict = asdict(msg)
                # Format date
                date = msg_dict.get("sent_at") or msg_dict.get("timestamp")
                if isinstance(date, (int, float)):
                    date = datetime.fromtimestamp(date / 1000)
                elif isinstance(date, str):
                    date = datetime.fromisoformat(date)
                # Sender logic
                is_self = msg_dict.get("source") == self_contact.serviceId
                sender = "Me" if is_self else (contact.name or contact.number or "Unknown")
                # Build output dict
                date_formatted = date.isoformat() if isinstance(date, datetime) else ""
                chat_messages.append({
                    "date": date_formatted,
                    "sender": sender,
                    "body": msg_dict.get("body", ""),
                    "quote": msg_dict.get("quote", "") or "",
                    "sticker": msg_dict.get("sticker", "") or "",
                    "reactions": msg_dict.get("reactions", []) or [],
                    "attachments": msg_dict.get("attachments", []) or []
                })
    return chat_messages


if __name__ == "__main__":
    mcp.run()
