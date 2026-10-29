"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  History,
  Search,
  Filter,
  Download,
  Trash2,
  ChevronDown,
  ChevronRight,
  Activity,
  Calendar,
  FileText,
  AlertCircle,
  Loader2,
  RefreshCw
} from "lucide-react";
import { cn } from "@/lib/utils";
import { fetchHistory, type DiagnosisRecord } from "@/lib/api";

const severityConfig = {
  critical: { color: "#DC2626", bg: "#FEF2F2" },
  high: { color: "#F59E0B", bg: "#FFFBEB" },
  moderate: { color: "#F59E0B", bg: "#FFFBEB" },
  low: { color: "#10B981", bg: "#ECFDF5" },
};

export function DiagnosisHistory() {
  const [records, setRecords] = useState<DiagnosisRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState<string>("all");
  const [expandedRecord, setExpandedRecord] = useState<string | null>(null);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const data = await fetchHistory();
      setRecords(data);
    } catch (err) {
      console.error("Failed to load history:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filteredRecords = records.filter((record) => {
    const matchesSearch = record.condition.toLowerCase().includes(searchQuery.toLowerCase()) ||
      record.symptoms.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = severityFilter === "all" || record.severity === severityFilter;
    return matchesSearch && matchesSeverity;
  });

  const stats = {
    total: records.length,
    critical: records.filter((r) => r.severity === "critical").length,
    high: records.filter((r) => r.severity === "high").length,
    moderate: records.filter((r) => r.severity === "moderate").length,
    low: records.filter((r) => r.severity === "low").length,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl lg:text-3xl font-bold text-neutral-900 dark:text-white">
            Diagnosis History
          </h1>
          <p className="text-neutral-600 dark:text-neutral-400 mt-1">
            View and manage past diagnosis records
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadHistory}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-2 border border-neutral-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg text-neutral-700 dark:text-neutral-300 text-sm transition-colors"
            title="Refresh history from database"
          >
            <RefreshCw size={16} className={cn(isLoading && "animate-spin text-primary-600")} />
            Sync
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors">
            <Download size={18} />
            Export
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="p-4 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800">
          <p className="text-sm text-neutral-500">Total</p>
          <p className="text-2xl font-bold text-neutral-900 dark:text-white">{stats.total}</p>
        </div>
        <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
          <p className="text-sm text-red-600">Critical</p>
          <p className="text-2xl font-bold text-red-700">{stats.critical}</p>
        </div>
        <div className="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
          <p className="text-sm text-amber-600">High</p>
          <p className="text-2xl font-bold text-amber-700">{stats.high}</p>
        </div>
        <div className="p-4 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
          <p className="text-sm text-yellow-600">Moderate</p>
          <p className="text-2xl font-bold text-yellow-700">{stats.moderate}</p>
        </div>
        <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800">
          <p className="text-sm text-emerald-600">Low</p>
          <p className="text-2xl font-bold text-emerald-700">{stats.low}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by condition or symptoms..."
            className="w-full pl-10 pr-4 py-3 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="relative">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="appearance-none px-4 py-3 pr-10 rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 text-neutral-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 cursor-pointer"
          >
            <option value="all">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="moderate">Moderate</option>
            <option value="low">Low</option>
          </select>
          <Filter className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 pointer-events-none" size={16} />
        </div>
      </div>

      {/* Records List */}
      <div className="space-y-3">
        <AnimatePresence>
          {filteredRecords.map((record) => (
            <motion.div
              key={record.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="overflow-hidden rounded-xl bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800"
            >
              <button
                onClick={() => setExpandedRecord(expandedRecord === record.id ? null : record.id)}
                className="w-full flex items-center justify-between p-4 text-left hover:bg-neutral-50 dark:hover:bg-neutral-800 transition-colors"
              >
                <div className="flex items-center gap-4">
                  {expandedRecord === record.id ? (
                    <ChevronDown size={20} className="text-neutral-400" />
                  ) : (
                    <ChevronRight size={20} className="text-neutral-400" />
                  )}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-neutral-900 dark:text-white">
                        {record.condition}
                      </span>
                      <span
                        className="px-2 py-0.5 rounded-full text-xs font-medium capitalize"
                        style={{ 
                          backgroundColor: severityConfig[record.severity].bg,
                          color: severityConfig[record.severity].color 
                        }}
                      >
                        {record.severity}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 mt-1 text-sm text-neutral-500">
                      <span className="flex items-center gap-1">
                        <Calendar size={14} />
                        {record.date}
                      </span>
                      <span className="flex items-center gap-1">
                        <Activity size={14} />
                        {Math.round(record.confidence * 100)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    // Delete action
                  }}
                  className="p-2 text-neutral-400 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={18} />
                </button>
              </button>

              <AnimatePresence>
                {expandedRecord === record.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-neutral-200 dark:border-neutral-800"
                  >
                    <div className="p-4 space-y-4">
                      <div>
                        <h4 className="text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                          Reported Symptoms
                        </h4>
                        <p className="text-neutral-600 dark:text-neutral-400">
                          {record.symptoms}
                        </p>
                      </div>
                      <div className="flex gap-2">
                        <button className="flex items-center gap-2 px-3 py-2 text-sm bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-lg hover:bg-primary-200 dark:hover:bg-primary-800 transition-colors">
                          <FileText size={16} />
                          View Report
                        </button>
                        <button className="flex items-center gap-2 px-3 py-2 text-sm bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-200 dark:hover:bg-neutral-700 transition-colors">
                          <Download size={16} />
                          Download
                        </button>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredRecords.length === 0 && (
          <div className="text-center py-12">
            <History className="w-12 h-12 mx-auto text-neutral-300 dark:text-neutral-600 mb-4" />
            <p className="text-neutral-500">No diagnosis records found</p>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
        <AlertCircle className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
        <p className="text-sm text-amber-800 dark:text-amber-200">
          This history is stored locally on your device. For privacy, avoid sharing sensitive health information.
        </p>
      </div>
    </motion.div>
  );
}