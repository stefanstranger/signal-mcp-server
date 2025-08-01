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
def signal_list_chats(
    source_dir: Path = get_default_signal_dir(),
    password: Optional[str] = None,
    key: Optional[str] = None,
    chats: str = "",
    include_empty: bool = False,
    include_disappearing: bool = True,
) -> List[Dict[str, Any]]:
    """
    List all Signal chats with their details.
    Args:
        source_dir (Path): Path to the Signal data directory.
        password (Optional[str]): Password for encrypted data, if applicable.
        key (Optional[str]): Key for encrypted data, if applicable.
        chats (str): Comma-separated list of chat IDs to filter.
        include_empty (bool): Whether to include empty chats.
        include_disappearing (bool): Whether to include disappearing messages.

        Returns:
        List[Dict[str, Any]]: A list of dictionaries containing Signal chat details.
    """
    convos, contacts, self_contact = sigexport.data.fetch_data(
        source_dir=source_dir,
        password=password,
        key=key,
        chats=chats,
        include_empty=include_empty,
        include_disappearing=include_disappearing,
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
def signal_get_chat_messages(
    chat_name: str,
    limit: Optional[int] = None,
    offset: int = 0,  # Add offset for pagination
    source_dir: Path = get_default_signal_dir(),
    password: Optional[str] = None,
    key: Optional[str] = None,
    chats: str = "",
    include_empty: bool = False,
    include_disappearing: bool = True,
) -> List[Dict[str, Any]]:
    """
    Get Signal messages from a specific chat by name.
    Args:
        chat_name (str): The name of the chat to retrieve messages from.
        limit (Optional[int]): Maximum number of messages to return.
        offset (int): Number of messages to skip before starting to collect results.
        source_dir (Path): Path to the Signal data directory.
        password (Optional[str]): Password for encrypted data, if applicable.
        key (Optional[str]): Key for encrypted data, if applicable.
        chats (str): Comma-separated list of chat IDs to filter.
        include_empty (bool): Whether to include empty chats.
        include_disappearing (bool): Whether to include disappearing messages.
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing messages from the specified Signal chat.
    """
    convos, contacts, self_contact = sigexport.data.fetch_data(
        source_dir=source_dir,
        password=password,
        key=key,
        chats=chats,
        include_empty=include_empty,
        include_disappearing=include_disappearing,
    )

    chat_messages = []
    for chat_id, messages in convos.items():
        contact = contacts.get(chat_id)
        if contact and contact.name == chat_name:
            # Sort messages by timestamp (newest first)
            sorted_messages = sorted(messages, key=lambda m: m.get_ts(), reverse=True)

            # Apply offset and limit
            start_idx = offset
            end_idx = offset + limit if limit else len(sorted_messages)
            paginated_messages = sorted_messages[start_idx:end_idx]

            for msg in paginated_messages:
                msg_dict = asdict(msg)
                # ... rest of your formatting code
                date = msg_dict.get("sent_at") or msg_dict.get("timestamp")
                if isinstance(date, (int, float)):
                    date = datetime.fromtimestamp(date / 1000)
                elif isinstance(date, str):
                    date = datetime.fromisoformat(date)
                sender = (
                    "Me"
                    if msg_dict.get("source") == self_contact.serviceId
                    else (contact.name or contact.number or "Unknown")
                )

                chat_messages.append(
                    {
                        "date": date.isoformat() if isinstance(date, datetime) else "",
                        "sender": sender,
                        "body": msg_dict.get("body", ""),
                        "quote": msg_dict.get("quote", "") or "",
                        "sticker": msg_dict.get("sticker", "") or "",
                        "reactions": msg_dict.get("reactions", []) or [],
                        "attachments": msg_dict.get("has_attachments", "") or "",
                    }
                )
            break

    return chat_messages


@mcp.tool()
def signal_search_chat(
    chat_name: str,
    query: str,
    limit: Optional[int] = None,
    source_dir: Path = get_default_signal_dir(),
    password: Optional[str] = None,
    key: Optional[str] = None,
    chats: str = "",
    include_empty: bool = False,
    include_disappearing: bool = True,
) -> List[Dict[str, Any]]:
    """
    Search for specific text within a Signal chat.
    Args:
        chat_name (str): The name of the chat to search within.
        query (str): The text to search for in messages.
        limit (Optional[int]): Maximum number of matching messages to return.
        source_dir (Path): Path to the Signal data directory.
        password (Optional[str]): Password for encrypted data, if applicable.
        key (Optional[str]): Key for encrypted data, if applicable.
        chats (str): Comma-separated list of chat IDs to filter.
        include_empty (bool): Whether to include empty chats.
        include_disappearing (bool): Whether to include disappearing messages.
    Returns:
        List[Dict[str, Any]]: A list of messages that match the search query.
    """
    convos, contacts, self_contact = sigexport.data.fetch_data(
        source_dir=source_dir,
        password=password,
        key=key,
        chats=chats,
        include_empty=include_empty,
        include_disappearing=include_disappearing,
    )

    matched_messages = []
    for chat_id, messages in convos.items():
        contact = contacts.get(chat_id)
        if contact and contact.name == chat_name:
            # Sort messages by timestamp (newest first)
            sorted_messages = sorted(messages, key=lambda m: m.get_ts(), reverse=True)

            for msg in sorted_messages:
                msg_dict = asdict(msg)
                body = msg_dict.get("body", "") or ""

                # Search in message body
                if query.lower() in body.lower():
                    date = msg_dict.get("sent_at") or msg_dict.get("timestamp")
                    if isinstance(date, (int, float)):
                        date = datetime.fromtimestamp(date / 1000)
                    elif isinstance(date, str):
                        date = datetime.fromisoformat(date)

                    sender = (
                        "Me"
                        if msg_dict.get("source") == self_contact.serviceId
                        else (contact.name or contact.number or "Unknown")
                    )

                    matched_messages.append(
                        {
                            "date": (
                                date.isoformat() if isinstance(date, datetime) else ""
                            ),
                            "sender": sender,
                            "body": body,
                            "quote": msg_dict.get("quote", "") or "",
                            "sticker": msg_dict.get("sticker", "") or "",
                            "reactions": msg_dict.get("reactions", []) or [],
                            "attachments": msg_dict.get("has_attachments", "") or "",
                        }
                    )

                    # Apply limit if specified
                    if limit and len(matched_messages) >= limit:
                        break
            break

    return matched_messages


@mcp.prompt()
def signal_summarize_chat_prompt(chat_name: str) -> str:
    return f"Summarize the recent messages in the Signal chat named '{chat_name}'."


@mcp.prompt()
def signal_chat_topic_prompt(chat_name: str) -> str:
    return f"What are the topics of discussion in the Signal chat named '{chat_name}'?"


@mcp.prompt()
def signal_chat_sentiment_prompt(chat_name: str) -> str:
    return f"Analyze the sentiment of messages in the Signal chat named '{chat_name}'."


@mcp.prompt()
def signal_search_chat_prompt(chat_name: str, query: str) -> str:
    return f"Search for the text '{query}' in the Signal chat named '{chat_name}'."


if __name__ == "__main__":
    mcp.run()
