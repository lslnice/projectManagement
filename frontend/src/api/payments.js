import request from './request'

export function getPayments(params) {
  return request.get('/payments', { params })
}

export function createPayment(data) {
  return request.post('/payments', data)
}

export function deletePayment(id) {
  return request.delete(`/payments/${id}`)
}

export function batchCreatePayments(data) {
  return request.post('/payments/batch', data)
}
