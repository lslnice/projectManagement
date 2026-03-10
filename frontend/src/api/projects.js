import request from './request'

export function getProjects(params) {
  return request.get('/projects', { params })
}

export function getProject(id) {
  return request.get(`/projects/${id}`)
}

export function createProject(data) {
  return request.post('/projects', data)
}

export function updateProject(id, data) {
  return request.put(`/projects/${id}`, data)
}

export function deleteProject(id) {
  return request.delete(`/projects/${id}`)
}

export function getProjectStats() {
  return request.get('/projects/stats/overview')
}

export function toggleRemoteStatus(projectId, status) {
  return request.post(`/projects/${projectId}/remote/toggle`, { status })
}

export function getRemoteStatus(projectId) {
  return request.get(`/projects/${projectId}/remote/status`)
}
