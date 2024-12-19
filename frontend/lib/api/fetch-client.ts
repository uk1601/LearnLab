import { API_BASE_URL } from '@/config';

interface FetchOptions extends RequestInit {
  authRequired?: boolean;
}

export async function fetchClient(
  endpoint: string,
  options: FetchOptions = { authRequired: true }
) {
  const { authRequired = true, ...fetchOptions } = options;
  
  // Get token from cookie instead of localStorage
  const token = document.cookie
    .split('; ')
    .find(row => row.startsWith('access_token='))
    ?.split('=')[1];

    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

  if (authRequired) {
    if (!token) {
      throw new Error('No access token found');
    }
    headers['Authorization'] = `Bearer ${decodeURIComponent(token)}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(endpoint, {
      ...fetchOptions,
      headers,
    });

    // Handle 401 errors globally
    if (response.status === 401) {
      // Clear all auth data
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      
      // Redirect to auth page
      window.location.href = '/auth';
      throw new Error('Unauthorized');
    }

    return response;
  } catch (error) {
    // Re-throw fetch errors
    throw error;
  }
}