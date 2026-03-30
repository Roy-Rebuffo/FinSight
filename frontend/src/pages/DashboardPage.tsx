import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Layout from '../components/Layout'
import { portfoliosApi } from '../api/portfolios'
import type { Portfolio, Position } from '../types'

const COLORS = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe']

// ── Componente de gráfica de allocation ──────────────────────────────
function AllocationChart({ positions }: { positions: Position[] }) {
  if (positions.length === 0) return null

  const data = positions.map((p) => ({
    name: p.ticker,
    value: parseFloat(p.quantity) * parseFloat(p.avg_cost),
  }))

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">
        Distribución del portfolio
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip
            formatter={(value) => {
                const num = typeof value === 'number' ? value : parseFloat(String(value))
                return [`$${num.toLocaleString('en-US', { minimumFractionDigits: 2 })}`, '']
            }}
            />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}

// ── Componente de tabla de posiciones ─────────────────────────────────
function PositionsTable({
  portfolioId,
  onAddPosition,
}: {
  portfolioId: string
  onAddPosition: () => void
}) {
  const { data: positions = [], isLoading } = useQuery({
    queryKey: ['positions', portfolioId],
    queryFn: () => portfoliosApi.getPositions(portfolioId),
  })

  const totalInvested = positions.reduce(
    (acc, p) => acc + parseFloat(p.quantity) * parseFloat(p.avg_cost),
    0
  )

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <p className="text-sm text-gray-500">Cargando posiciones...</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AllocationChart positions={positions} />

      <div className="bg-white rounded-xl border border-gray-200">
        <div className="flex items-center justify-between p-6 border-b border-gray-100">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Posiciones</h3>
            {positions.length > 0 && (
              <p className="text-xs text-gray-500 mt-0.5">
                Total invertido:{' '}
                <span className="font-medium text-gray-900">
                  ${totalInvested.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </span>
              </p>
            )}
          </div>
          <button
            onClick={onAddPosition}
            className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-indigo-700 transition-colors"
          >
            + Añadir posición
          </button>
        </div>

        {positions.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-400 text-sm">
              No hay posiciones en este portfolio
            </p>
            <button
              onClick={onAddPosition}
              className="mt-3 text-indigo-600 text-sm hover:underline"
            >
              Añadir primera posición
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100">
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ticker
                  </th>
                  <th className="text-left px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tipo
                  </th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Cantidad
                  </th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Precio medio
                  </th>
                  <th className="text-right px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Total invertido
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {positions.map((position) => {
                  const total =
                    parseFloat(position.quantity) * parseFloat(position.avg_cost)
                  const pct = (total / totalInvested) * 100
                  return (
                    <tr key={position.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-gray-900">
                            {position.ticker}
                          </span>
                          <span className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">
                            {pct.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-500 capitalize">
                        {position.asset_type}
                      </td>
                      <td className="px-6 py-4 text-right text-gray-900">
                        {parseFloat(position.quantity).toLocaleString('en-US')}
                      </td>
                      <td className="px-6 py-4 text-right text-gray-900">
                        ${parseFloat(position.avg_cost).toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-6 py-4 text-right font-medium text-gray-900">
                        ${total.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Modal para añadir posición ────────────────────────────────────────
function AddPositionModal({
  portfolioId,
  onClose,
}: {
  portfolioId: string
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    ticker: '',
    asset_type: 'stock',
    quantity: '',
    avg_cost: '',
  })
  const [error, setError] = useState('')

  const mutation = useMutation({
    mutationFn: () => portfoliosApi.createPosition(portfolioId, form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['positions', portfolioId] })
      onClose()
    },
    onError: () => {
      setError('Error al añadir la posición. Verifica los datos.')
    },
  })

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 className="text-base font-medium text-gray-900 mb-4">
          Añadir posición
        </h3>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Ticker
            </label>
            <input
              type="text"
              value={form.ticker}
              onChange={(e) =>
                setForm({ ...form, ticker: e.target.value.toUpperCase() })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="AAPL"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Tipo de activo
            </label>
            <select
              value={form.asset_type}
              onChange={(e) => setForm({ ...form, asset_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="stock">Acción</option>
              <option value="etf">ETF</option>
              <option value="crypto">Crypto</option>
              <option value="bond">Bono</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Cantidad
              </label>
              <input
                type="number"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="10"
                step="0.00000001"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                Precio medio ($)
              </label>
              <input
                type="number"
                value={form.avg_cost}
                onChange={(e) => setForm({ ...form, avg_cost: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="150.00"
                step="0.01"
              />
            </div>
          </div>

          {error && (
            <p className="text-xs text-red-600 bg-red-50 px-3 py-2 rounded-lg">
              {error}
            </p>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Añadiendo...' : 'Añadir'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Modal para crear portfolio ────────────────────────────────────────
function CreatePortfolioModal({ onClose }: { onClose: () => void }) {
  const queryClient = useQueryClient()
  const [form, setForm] = useState({
    name: '',
    description: '',
    benchmark_ticker: '^GSPC',
  })

  const mutation = useMutation({
    mutationFn: () => portfoliosApi.create(form),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
      onClose()
    },
  })

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl">
        <h3 className="text-base font-medium text-gray-900 mb-4">
          Nuevo portfolio
        </h3>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Nombre
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Mi portfolio"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Descripción (opcional)
            </label>
            <input
              type="text"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Portfolio de largo plazo"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Benchmark
            </label>
            <select
              value={form.benchmark_ticker}
              onChange={(e) =>
                setForm({ ...form, benchmark_ticker: e.target.value })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="^GSPC">S&P 500</option>
              <option value="^IBEX">IBEX 35</option>
              <option value="^STOXX50E">Euro Stoxx 50</option>
              <option value="^IXIC">NASDAQ</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending || !form.name}
            className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            {mutation.isPending ? 'Creando...' : 'Crear'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Página principal del Dashboard ────────────────────────────────────
export default function DashboardPage() {
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null)
  const [showCreatePortfolio, setShowCreatePortfolio] = useState(false)
  const [showAddPosition, setShowAddPosition] = useState(false)

  const { data: portfolios = [], isLoading } = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfoliosApi.getAll,
  })

  // Selecciona el primer portfolio automáticamente
  if (portfolios.length > 0 && !selectedPortfolio) {
    setSelectedPortfolio(portfolios[0])
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold text-gray-900">
            Mis portfolios
          </h1>
          <button
            onClick={() => setShowCreatePortfolio(true)}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            + Nuevo portfolio
          </button>
        </div>

        {isLoading ? (
          <p className="text-sm text-gray-500">Cargando portfolios...</p>
        ) : portfolios.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <p className="text-gray-400 text-sm">No tienes portfolios aún</p>
            <button
              onClick={() => setShowCreatePortfolio(true)}
              className="mt-3 text-indigo-600 text-sm hover:underline"
            >
              Crear tu primer portfolio
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Lista de portfolios */}
            <div className="lg:col-span-1 space-y-2">
              {portfolios.map((portfolio) => (
                <button
                  key={portfolio.id}
                  onClick={() => setSelectedPortfolio(portfolio)}
                  className={`w-full text-left p-4 rounded-xl border transition-all ${
                    selectedPortfolio?.id === portfolio.id
                      ? 'border-indigo-300 bg-indigo-50'
                      : 'border-gray-200 bg-white hover:border-gray-300'
                  }`}
                >
                  <p className="text-sm font-medium text-gray-900">
                    {portfolio.name}
                  </p>
                  {portfolio.description && (
                    <p className="text-xs text-gray-500 mt-0.5 truncate">
                      {portfolio.description}
                    </p>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    vs {portfolio.benchmark_ticker}
                  </p>
                </button>
              ))}
            </div>

            {/* Detalle del portfolio seleccionado */}
            <div className="lg:col-span-3">
              {selectedPortfolio && (
                <PositionsTable
                  portfolioId={selectedPortfolio.id}
                  onAddPosition={() => setShowAddPosition(true)}
                />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Modales */}
      {showCreatePortfolio && (
        <CreatePortfolioModal onClose={() => setShowCreatePortfolio(false)} />
      )}
      {showAddPosition && selectedPortfolio && (
        <AddPositionModal
          portfolioId={selectedPortfolio.id}
          onClose={() => setShowAddPosition(false)}
        />
      )}
    </Layout>
  )
}