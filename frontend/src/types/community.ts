/** Community types. */

export type Platform = 'vk' | 'telegram';

export interface Community {
  id: string;
  platform: Platform;
  external_id: string;
  name: string;
  is_active: boolean;
  token_expires_at: string | null;
  last_sync_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface CommunityCreate {
  platform: Platform;
  external_id: string;
  name: string;
  access_token?: string;
  refresh_token?: string;
  bot_token?: string;
}

export interface CommunityUpdate {
  name?: string;
}
