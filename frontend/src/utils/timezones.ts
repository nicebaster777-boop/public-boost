/** Timezone utilities and list. */

/**
 * Get list of common timezones with their display names.
 */
export function getTimezones(): Array<{ value: string; label: string }> {
  // Common timezones for Russia and neighboring countries
  const commonTimezones = [
    { value: 'Europe/Moscow', label: 'Москва (UTC+3)' },
    { value: 'Europe/Kiev', label: 'Киев (UTC+2)' },
    { value: 'Europe/Minsk', label: 'Минск (UTC+3)' },
    { value: 'Asia/Yekaterinburg', label: 'Екатеринбург (UTC+5)' },
    { value: 'Asia/Omsk', label: 'Омск (UTC+6)' },
    { value: 'Asia/Krasnoyarsk', label: 'Красноярск (UTC+7)' },
    { value: 'Asia/Irkutsk', label: 'Иркутск (UTC+8)' },
    { value: 'Asia/Yakutsk', label: 'Якутск (UTC+9)' },
    { value: 'Asia/Vladivostok', label: 'Владивосток (UTC+10)' },
    { value: 'Asia/Magadan', label: 'Магадан (UTC+11)' },
    { value: 'Asia/Kamchatka', label: 'Камчатка (UTC+12)' },
  ];

  // Get all supported timezones
  let allTimezones: string[] = [];
  try {
    allTimezones = (Intl as any).supportedValuesOf?.('timeZone') || [];
  } catch {
    // Fallback list if Intl.supportedValuesOf is not available
    allTimezones = [
      'UTC',
      'Europe/London',
      'Europe/Paris',
      'Europe/Berlin',
      'Europe/Moscow',
      'America/New_York',
      'America/Chicago',
      'America/Denver',
      'America/Los_Angeles',
      'Asia/Tokyo',
      'Asia/Shanghai',
      'Asia/Dubai',
      'Australia/Sydney',
    ];
  }

  // Create full list: common first, then all others
  const commonValues = new Set(commonTimezones.map((tz) => tz.value));
  const otherTimezones = allTimezones
    .filter((tz) => !commonValues.has(tz))
    .sort()
    .map((tz) => ({
      value: tz,
      label: formatTimezoneLabel(tz),
    }));

  return [...commonTimezones, ...otherTimezones];
}

/**
 * Format timezone label for display.
 */
function formatTimezoneLabel(timezone: string): string {
  try {
    // Get UTC offset
    const offset = getTimezoneOffset(timezone);
    const offsetStr = formatOffset(offset);
    return `${timezone.replace(/_/g, ' ')} (${offsetStr})`;
  } catch {
    return timezone.replace(/_/g, ' ');
  }
}

/**
 * Get UTC offset in minutes for a timezone.
 */
function getTimezoneOffset(timezone: string): number {
  try {
    const now = new Date();
    const utc = new Date(now.toLocaleString('en-US', { timeZone: 'UTC' }));
    const tz = new Date(now.toLocaleString('en-US', { timeZone: timezone }));
    return (tz.getTime() - utc.getTime()) / (1000 * 60);
  } catch {
    return 0;
  }
}

/**
 * Format offset as +/-HH:MM.
 */
function formatOffset(minutes: number): string {
  const sign = minutes >= 0 ? '+' : '-';
  const absMinutes = Math.abs(minutes);
  const hours = Math.floor(absMinutes / 60);
  const mins = absMinutes % 60;
  return `UTC${sign}${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
}

/**
 * Get user's current timezone.
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}
