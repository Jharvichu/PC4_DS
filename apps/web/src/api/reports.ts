import apiClient from './client'
import { Report, ReportCreateInput, ReportPublic, ReportStatus } from '../types'

export async function createReport(data: ReportCreateInput): Promise<Report> {
  const response = await apiClient.post<Report>('/reports/', data)
  return response.data
}

export async function getActiveReports(): Promise<ReportPublic[]> {
  const response = await apiClient.get<ReportPublic[]>('/reports/active')
  return response.data
}

export async function getMyReports(): Promise<Report[]> {
  const response = await apiClient.get<Report[]>('/reports/me')
  return response.data
}

export async function getReportPublic(reportId: string): Promise<ReportPublic> {
  const response = await apiClient.get<ReportPublic>(`/reports/${reportId}`)
  return response.data
}

export async function updateReportStatus(reportId: string, status: ReportStatus): Promise<Report> {
  const response = await apiClient.put<Report>(`/reports/${reportId}/status`, { status })
  return response.data
}
