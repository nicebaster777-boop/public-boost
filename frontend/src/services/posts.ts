/** Posts API service. */

import { apiGet, apiPost, apiPatch, apiDelete } from './api';
import type { Post, PostCreate, PostUpdate } from '../types/post';
import type { ApiListResponse } from '../types/api';

export interface PostsListParams {
  status?: string;
  community_id?: string;
  scheduled_from?: string;
  scheduled_to?: string;
  page?: number;
  page_size?: number;
}

/**
 * Get list of posts.
 */
export async function getPosts(params?: PostsListParams): Promise<ApiListResponse<Post>> {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.append('status', params.status);
  if (params?.community_id) queryParams.append('community_id', params.community_id);
  if (params?.scheduled_from) queryParams.append('scheduled_from', params.scheduled_from);
  if (params?.scheduled_to) queryParams.append('scheduled_to', params.scheduled_to);
  if (params?.page) queryParams.append('page', String(params.page));
  if (params?.page_size) queryParams.append('page_size', String(params.page_size));
  
  const query = queryParams.toString();
  return apiGet<ApiListResponse<Post>>(`/posts${query ? `?${query}` : ''}`);
}

/**
 * Get post by ID.
 */
export async function getPost(id: string): Promise<Post> {
  const response = await apiGet<{ data: Post }>(`/posts/${id}`);
  return response.data || (response as unknown as Post);
}

/**
 * Create new post.
 */
export async function createPost(data: PostCreate): Promise<Post> {
  const response = await apiPost<{ data: Post }>('/posts', data);
  return response.data || (response as unknown as Post);
}

/**
 * Update post.
 */
export async function updatePost(id: string, data: PostUpdate): Promise<Post> {
  const response = await apiPatch<{ data: Post }>(`/posts/${id}`, data);
  return response.data || (response as unknown as Post);
}

/**
 * Delete post.
 */
export async function deletePost(id: string): Promise<void> {
  await apiDelete(`/posts/${id}`);
}
