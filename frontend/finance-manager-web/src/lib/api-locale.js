const normalize = (value) =>
  typeof value === 'string'
    ? value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    : value

const TYPE_MAP = {
  receita: 'receita',
  despesa: 'despesa',
  transferencia: 'transferencia',
  income: 'receita',
  expense: 'despesa',
  transfer: 'transferencia',
}

const STATUS_MAP = {
  pendente: 'pendente',
  compensada: 'compensada',
  conciliada: 'conciliada',
  pending: 'pendente',
  cleared: 'compensada',
  reconciled: 'conciliada',
}

const METHOD_MAP = {
  dinheiro: 'dinheiro',
  pix: 'pix',
  cartao_debito: 'cartao_debito',
  cartao_credito: 'cartao_credito',
  boleto: 'boleto',
  transferencia: 'transferencia',
  cheque: 'cheque',
  outros: 'outros',
  cash: 'dinheiro',
  debit: 'cartao_debito',
  credit: 'cartao_credito',
  transfer: 'transferencia',
  check: 'cheque',
  other: 'outros',
}

export const transactionTypeOptions = [
  { value: 'receita', label: 'Receita' },
  { value: 'despesa', label: 'Despesa' },
  { value: 'transferencia', label: 'Transferência' },
]

export const transactionStatusOptions = [
  { value: 'pendente', label: 'Pendente' },
  { value: 'compensada', label: 'Compensada' },
  { value: 'conciliada', label: 'Conciliada' },
]

export const paymentMethodOptions = [
  { value: 'dinheiro', label: 'Dinheiro' },
  { value: 'pix', label: 'PIX' },
  { value: 'cartao_debito', label: 'Cartão de Débito' },
  { value: 'cartao_credito', label: 'Cartão de Crédito' },
  { value: 'boleto', label: 'Boleto' },
  { value: 'transferencia', label: 'Transferência' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'outros', label: 'Outros' },
]

export const categoryTypeOptions = [
  { value: 'receita', label: 'Receita' },
  { value: 'despesa', label: 'Despesa' },
]

export function normalizeTransactionType(value) {
  if (!value) return value
  return TYPE_MAP[normalize(value)] ?? value
}

export function normalizeCategoryType(value) {
  const normalized = normalizeTransactionType(value)
  return normalized === 'transferencia' ? 'despesa' : normalized
}

export function normalizeTransactionStatus(value) {
  if (!value) return value
  return STATUS_MAP[normalize(value)] ?? value
}

export function normalizePaymentMethod(value) {
  if (!value) return value
  return METHOD_MAP[normalize(value)] ?? value
}

export function getField(entity, ...candidates) {
  if (!entity) return undefined
  for (const key of candidates) {
    if (entity[key] !== undefined && entity[key] !== null) {
      return entity[key]
    }
  }
  return undefined
}
