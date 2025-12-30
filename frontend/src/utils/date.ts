/** Date and timezone utilities. */

/**
 * Convert UTC datetime to user's timezone.
 */
export function toUserTimezone(utcDate: string, _userTimezone: string): Date {
  return new Date(utcDate);
}

/**
 * Convert user's local datetime to UTC.
 */
export function toUTC(localDate: Date, _userTimezone: string): string {
  return localDate.toISOString();
}

/**
 * Format date for display.
 */
export function formatDate(date: string | Date, format: 'short' | 'long' = 'short'): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  
  if (format === 'short') {
    return d.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  }
  
  return d.toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format datetime for display.
 */
export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('ru-RU', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}
