import urllib.parse


def generate_attendee_connect_link(
    event_name: str,
    matched_display_name: str | None = None,
) -> str:
    """Generates a safe WhatsApp share deep-link to coordinate with a matched attendee."""
    greeting = f"Hey {matched_display_name}!" if matched_display_name else "Hey!"
    message = (
        f"{greeting} I found you on Raaso for {event_name}! "
        f"Looking for fellow dancers to form a squad and hit the Garba grounds together. "
        f"Let's connect!"
    )
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/?text={encoded}"


def generate_squad_invite_link(
    squad_name: str,
    event_name: str,
) -> str:
    """Generates a safe WhatsApp share deep-link to invite friends or teammates to a squad."""
    message = (
        f"Join my Garba squad '{squad_name}' for {event_name} on Raaso! "
        f"Find your people. Find your rhythm."
    )
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/?text={encoded}"

