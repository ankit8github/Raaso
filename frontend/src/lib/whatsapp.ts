/**
 * Generates safe WhatsApp deep links without revealing phone numbers.
 * Opens WhatsApp share dialogue with a prefilled, friendly invitation.
 */
export function buildAttendeeWhatsAppLink(
  eventName: string,
  matchedName?: string
): string {
  const greeting = matchedName ? `Hey ${matchedName}!` : 'Hey!';
  const message = `${greeting} I saw you on Raaso for ${eventName}! Looking for fellow dancers to squad up and groove together. Let's connect!`;
  return `https://wa.me/?text=${encodeURIComponent(message)}`;
}

export function buildSquadWhatsAppLink(
  squadName: string,
  eventName: string
): string {
  const message = `Join my Garba squad '${squadName}' for ${eventName} on Raaso! "Find your people. Find your rhythm."`;
  return `https://wa.me/?text=${encodeURIComponent(message)}`;
}

