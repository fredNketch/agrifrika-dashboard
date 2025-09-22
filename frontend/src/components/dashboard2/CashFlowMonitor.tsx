import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import AnimatedCard from '../ui/AnimatedCard';
import type { CashFlowData } from '../../types';

interface CashFlowMonitorProps {
  className?: string;
}

const CashFlowMonitor: React.FC<CashFlowMonitorProps> = ({ className = '' }) => {
  const [scrollPosition, setScrollPosition] = useState(0);
  const [isAutoScrolling, setIsAutoScrolling] = useState(true);
  const [data, setData] = useState<CashFlowData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCashFlow();
    const interval = setInterval(fetchCashFlow, 5 * 60 * 1000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchCashFlow = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://dashboard.agrifrika.com/api/v1/dashboard2/cash-flow', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        mode: 'cors'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (!result.success) {
        throw new Error(result.message || 'API call failed');
      }

      setData(result.data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erreur de connexion à l\'API');
    } finally {
      setLoading(false);
    }
  };

  // Utilise les vraies données Cash Flow ou fallback
  const cashflowSections = data ? [
    {
      title: "Balance & Metrics",
      data: {
        balance: `$${data.current_balance.toLocaleString()}`,
        currency: "Current Available",
        runway: data.thirty_day_projection > 0 ? "Positive" : "N/A",
        runwayDays: `${Math.ceil(data.current_balance / (Math.abs(data.thirty_day_projection) / 30))} Days`,
        burnRate: `$${Math.abs(data.weekly_summary.net_change).toLocaleString()}`,
        burnPeriod: "Weekly Average"
      },
      metrics: [
        { label: "Weekly Income", value: `$${data.weekly_summary.total_income.toLocaleString()}`, color: "text-emerald-600", bgColor: "bg-emerald-50", borderColor: "border-emerald-200", icon: "📈" },
        { label: "Weekly Expenses", value: `$${data.weekly_summary.total_expenses.toLocaleString()}`, color: "text-red-600", bgColor: "bg-red-50", borderColor: "border-red-200", icon: "📉" },
        { label: "Net Change", value: `$${data.weekly_summary.net_change.toLocaleString()}`, color: data.weekly_summary.net_change > 0 ? "text-emerald-600" : "text-red-600", bgColor: data.weekly_summary.net_change > 0 ? "bg-emerald-50" : "bg-red-50", borderColor: data.weekly_summary.net_change > 0 ? "border-emerald-200" : "border-red-200", icon: data.weekly_summary.net_change > 0 ? "💹" : "📊" },
        { label: "30-Day Projection", value: `$${data.thirty_day_projection.toLocaleString()}`, color: data.thirty_day_projection > 0 ? "text-emerald-600" : "text-red-600", bgColor: data.thirty_day_projection > 0 ? "bg-emerald-50" : "bg-red-50", borderColor: data.thirty_day_projection > 0 ? "border-emerald-200" : "border-red-200", icon: "🔮" }
      ]
    },
    {
      title: "Transaction History",
      data: {
        totalTransactions: data.recent_transactions.length,
        transactions: data.recent_transactions.map(transaction => ({
          date: new Date(transaction.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
          description: transaction.description,
          type: transaction.type === 'income' ? 'Income' : 'Expense',
          amount: `$${transaction.amount.toLocaleString()}`,
          status: "completed"
        }))
      }
    }
  ] : [];

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed': return { bg: 'bg-gradient-to-r from-emerald-50 to-green-50', text: 'text-emerald-700', badge: 'bg-emerald-500', border: 'border-emerald-200' };
      case 'approved': return { bg: 'bg-gradient-to-r from-blue-50 to-indigo-50', text: 'text-blue-700', badge: 'bg-blue-500', border: 'border-blue-200' };
      case 'submitted': return { bg: 'bg-gradient-to-r from-orange-50 to-amber-50', text: 'text-orange-700', badge: 'bg-orange-500', border: 'border-orange-200' };
      default: return { bg: 'bg-gradient-to-r from-gray-50 to-slate-50', text: 'text-gray-700', badge: 'bg-gray-500', border: 'border-gray-200' };
    }
  };

  // Auto-scroll pour voir toutes les sections
  useEffect(() => {
    if (!isAutoScrolling || cashflowSections.length <= 1) return;

    const interval = setInterval(() => {
      setScrollPosition(prev => {
        const maxScroll = Math.max(0, cashflowSections.length - 1);
        return prev >= maxScroll ? 0 : prev + 1;
      });
    }, 30000); // Change toutes les 30 secondes

    return () => clearInterval(interval);
  }, [isAutoScrolling, cashflowSections.length]);

  const currentSection = cashflowSections.length > 0 ? cashflowSections[scrollPosition] : null;

  return (
    <AnimatedCard
      title={`Cashflow ${data ? `$${data.current_balance.toLocaleString()}` : 'Loading...'}`}
      icon="💰"
      loading={loading}
      className={`h-full ${className}`}
    >
      <div 
        className="space-y-4 h-full flex flex-col"
        onMouseEnter={() => setIsAutoScrolling(false)}
        onMouseLeave={() => setIsAutoScrolling(true)}
      >
        {/* Section actuelle */}
        {currentSection ? (
          <motion.div
            key={`section-${scrollPosition}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="flex-1 overflow-hidden"
          >
            {/* Balance & Metrics */}
            {currentSection.title === "Balance & Metrics" && (
              <div className="space-y-4 h-full">
                {/* Balance cards avec design moderne */}
                <div className="grid grid-cols-3 gap-3">
                  <motion.div 
                    className="relative overflow-hidden bg-gradient-to-br from-blue-500 to-blue-600 p-3 rounded-xl shadow-lg border border-blue-400/20"
                    whileHover={{ scale: 1.02 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
                    <div className="relative z-10 text-center text-white">
                      <div className="text-xl mb-1">💰</div>
                      <div className="font-bold text-sm mb-1">Balance</div>
                      <div className="font-bold text-lg mb-1">{currentSection.data.balance}</div>
                      <div className="text-xs opacity-90">{currentSection.data.currency}</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    className="relative overflow-hidden bg-gradient-to-br from-emerald-500 to-emerald-600 p-3 rounded-xl shadow-lg border border-emerald-400/20"
                    whileHover={{ scale: 1.02 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
                    <div className="relative z-10 text-center text-white">
                      <div className="text-xl mb-1">⏰</div>
                      <div className="font-bold text-sm mb-1">Runway</div>
                      <div className="font-bold text-lg mb-1">{currentSection.data.runway}</div>
                      <div className="text-xs opacity-90">{currentSection.data.runwayDays}</div>
                    </div>
                  </motion.div>

                  <motion.div 
                    className="relative overflow-hidden bg-gradient-to-br from-orange-500 to-orange-600 p-3 rounded-xl shadow-lg border border-orange-400/20"
                    whileHover={{ scale: 1.02 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -translate-y-8 translate-x-8"></div>
                    <div className="relative z-10 text-center text-white">
                      <div className="text-xl mb-1">🔥</div>
                      <div className="font-bold text-sm mb-1">Burn Rate</div>
                      <div className="font-bold text-lg mb-1">{currentSection.data.burnRate}</div>
                      <div className="text-xs opacity-90">{currentSection.data.burnPeriod}</div>
                    </div>
                  </motion.div>
                </div>
                
                {/* Metrics details avec design moderne */}
                <div className="space-y-2">
                  {currentSection.metrics && currentSection.metrics.map((metric, idx) => (
                    <motion.div 
                      key={idx} 
                      className={`flex justify-between items-center p-3 ${metric.bgColor} rounded-lg border ${metric.borderColor} shadow-sm hover:shadow-md transition-all duration-200`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.1 }}
                      whileHover={{ scale: 1.01 }}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="text-base">{metric.icon}</div>
                        <span className="font-semibold text-gray-800">{metric.label}</span>
                      </div>
                      <span className={`font-bold text-base ${metric.color}`}>{metric.value}</span>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Transaction History avec design moderne */}
            {currentSection.title === "Transaction History" && (
              <div className="space-y-4 h-full">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="text-2xl">📈</div>
                    <h3 className="font-bold text-lg text-gray-800">Cashflow History</h3>
                  </div>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1.5 text-sm bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 font-medium">
                      All Transactions
                    </button>
                    <button className="px-3 py-1.5 text-sm bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 font-medium">
                      Add Transaction
                    </button>
                  </div>
                </div>
                
                <div className="bg-gradient-to-r from-gray-50 to-slate-50 p-4 rounded-xl border border-gray-200">
                  <div className="grid grid-cols-5 text-sm font-bold text-gray-700 mb-3">
                    <div>Date</div>
                    <div>Description</div>
                    <div>Type</div>
                    <div>Recurrence</div>
                    <div>Amount</div>
                  </div>
                </div>

                <div className="space-y-2 max-h-48 overflow-y-auto pr-2">
                  {currentSection.data.transactions && currentSection.data.transactions.map((transaction, idx) => {
                    const statusInfo = getStatusColor(transaction.status);
                    return (
                      <motion.div 
                        key={idx} 
                        className={`grid grid-cols-5 p-3 ${statusInfo.bg} rounded-xl border ${statusInfo.border} shadow-sm hover:shadow-md transition-all duration-200`}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        whileHover={{ scale: 1.01 }}
                      >
                        <div className="font-medium text-gray-800">{transaction.date}</div>
                        <div className="truncate text-gray-700">{transaction.description}</div>
                        <div className={`${statusInfo.text} font-semibold`}>{transaction.type}</div>
                        <div className="text-gray-500">-</div>
                        <div className="font-bold text-emerald-700">{transaction.amount}</div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div 
            className="flex-1 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="text-center text-gray-500">
              <div className="text-4xl mb-4">💰</div>
              <div className="text-lg font-medium mb-2">Aucune donnée Cash Flow disponible</div>
              <div className="text-sm">Vérifiez la connexion à l'API</div>
            </div>
          </motion.div>
        )}

        {/* Indicateur de scroll moderne */}
        {cashflowSections.length > 1 && (
          <div className="flex justify-center space-x-2 flex-shrink-0">
            {cashflowSections.map((_, index) => (
              <motion.button
                key={index}
                onClick={() => setScrollPosition(index)}
                className={`w-3 h-3 rounded-full transition-all duration-300 ${
                  scrollPosition === index 
                    ? 'bg-gradient-to-r from-blue-500 to-indigo-600 shadow-lg' 
                    : 'bg-gray-300 hover:bg-gray-400'
                }`}
                whileHover={{ scale: 1.2 }}
                whileTap={{ scale: 0.9 }}
              />
            ))}
          </div>
        )}

        {/* Section title indicator moderne */}
        {currentSection && (
          <motion.div 
            className="text-center text-sm font-medium text-gray-600 bg-gradient-to-r from-gray-50 to-slate-50 py-2 px-4 rounded-full border border-gray-200 flex-shrink-0"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            {currentSection.title}
          </motion.div>
        )}
      </div>
    </AnimatedCard>
  );
};

export default CashFlowMonitor;