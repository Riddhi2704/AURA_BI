import type { BIReport } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export async function searchCompany(companyName: string): Promise<BIReport> {
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ company_name: companyName }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to search company');
  }

  return response.json();
}

export async function getRecentSearches(): Promise<string[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/recent`);
    if (!response.ok) return [];
    return response.json();
  } catch (error) {
    console.error('Error fetching recent searches:', error);
    return [];
  }
}

export async function exportPdf(report: BIReport): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/export/pdf`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(report),
  });

  if (!response.ok) {
    throw new Error('Failed to export PDF');
  }

  return response.blob();
}

export async function exportPpt(report: BIReport): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/export/ppt`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(report),
  });

  if (!response.ok) {
    throw new Error('Failed to export PPT');
  }

  return response.blob();
}
