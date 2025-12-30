/** Post types. */

export type PostStatus =
  | 'draft'
  | 'scheduled'
  | 'publishing'
  | 'published'
  | 'failed'
  | 'partially_published';

export type PublicationStatus = 'pending' | 'publishing' | 'published' | 'failed';

export interface PostPublication {
  id: string;
  community_id: string;
  community_name: string;
  platform: string;
  status: PublicationStatus;
  external_post_id: string | null;
  published_at: string | null;
  error_message: string | null;
}

export interface Post {
  id: string;
  content_text: string;
  image_url: string | null;
  scheduled_at: string | null;
  status: PostStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  publications: PostPublication[];
}

export interface PostCreate {
  content_text: string;
  image_url?: string | null;
  scheduled_at?: string | null;
  community_ids?: string[];
}

export interface PostUpdate {
  content_text?: string;
  image_url?: string | null;
  scheduled_at?: string | null;
  community_ids?: string[] | null;
}
