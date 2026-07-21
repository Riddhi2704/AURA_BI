import { useState } from 'react';
import { 
  FileText, Presentation, ClipboardCheck, Share2, 
  Sparkles, Check, CheckCircle2 
} from 'lucide-react';
import type { BIReport } from '../types';
import { exportPdf, exportPpt } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';

interface NavbarProps {
  report: BIReport | null;
  isDark: boolean;
  onCopyText: () => void;
}

export default function Navbar({ report, isDark, onCopyText }: NavbarProps) {
  const [exportingPdf, setExportingPdf] = useState(false);
  const [exportingPpt, setExportingPpt] = useState(false);
  const [copiedLink, setCopiedLink] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);

  const handlePdfDownload = async () => {
    if (!report) return;
    try {
      setExportingPdf(true);
      const blob = await exportPdf(report);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${report.company_name.toLowerCase().replace(/ /g, '_')}_bi_report.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      console.error('PDF Export Error:', err);
      alert('Failed to export PDF.');
    } finally {
      setExportingPdf(false);
    }
  };

  const handlePptDownload = async () => {
    if (!report) return;
    try {
      setExportingPpt(true);
      const blob = await exportPpt(report);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${report.company_name.toLowerCase().replace(/ /g, '_')}_presentation.pptx`);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
    } catch (err) {
      console.error('PPT Export Error:', err);
      alert('Failed to export PowerPoint presentation.');
    } finally {
      setExportingPpt(false);
    }
  };

  const handleShare = () => {
    setCopiedLink(true);
    // Copy a fake sharing URL to clipboard
    const shareUrl = `${window.location.origin}?company=${encodeURIComponent(report?.company_name || '')}`;
    navigator.clipboard.writeText(shareUrl);
    setTimeout(() => setCopiedLink(false), 3000);
  };

  const handleCopyReport = () => {
    onCopyText();
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 3000);
  };

  return (
    <header className={`h-16 flex items-center justify-between px-6 border-b shrink-0 transition-colors z-10 ${
      isDark 
        ? 'bg-background-dark/80 backdrop-blur-md border-white/10 text-white' 
        : 'bg-white/80 backdrop-blur-md border-gray-200 text-gray-800'
    }`}>
      {/* Platform Title */}
      <div className="flex items-center gap-2">
        <Sparkles size={16} className="text-primary animate-pulse" />
        <span className="text-sm font-semibold tracking-wide uppercase opacity-90">
          AI Business Intelligence Hub
        </span>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center gap-2">
        {report && (
          <>
            {/* Copy Report */}
            <button
              onClick={handleCopyReport}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                isDark 
                  ? 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20' 
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
              }`}
            >
              {copiedReport ? (
                <>
                  <Check size={14} className="text-success animate-bounce" />
                  <span className="text-success font-semibold">Copied!</span>
                </>
              ) : (
                <>
                  <ClipboardCheck size={14} />
                  <span>Copy Report</span>
                </>
              )}
            </button>

            {/* Share */}
            <button
              onClick={handleShare}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                isDark 
                  ? 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20' 
                  : 'bg-gray-50 border-gray-200 hover:bg-gray-100 hover:border-gray-300'
              }`}
            >
              {copiedLink ? (
                <>
                  <Check size={14} className="text-success" />
                  <span className="text-success font-semibold">Shared Link!</span>
                </>
              ) : (
                <>
                  <Share2 size={14} />
                  <span>Share</span>
                </>
              )}
            </button>

            {/* Export PDF */}
            <button
              onClick={handlePdfDownload}
              disabled={exportingPdf}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-red-600 to-red-500 hover:brightness-110 shadow transition-all disabled:opacity-50"
            >
              <FileText size={14} />
              <span>{exportingPdf ? 'Generating PDF...' : 'Download PDF'}</span>
            </button>

            {/* Export PPT */}
            <button
              onClick={handlePptDownload}
              disabled={exportingPpt}
              className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-white bg-gradient-to-r from-primary via-secondary to-accent hover:brightness-110 shadow transition-all disabled:opacity-50"
            >
              <Presentation size={14} />
              <span>{exportingPpt ? 'Generating PPT...' : 'Export PPT'}</span>
            </button>
          </>
        )}
      </div>

      {/* Copy Alert Notification Bubble */}
      <AnimatePresence>
        {(copiedLink || copiedReport) && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.9 }}
            className="absolute top-20 right-6 flex items-center gap-3 px-4 py-3 rounded-xl shadow-xl z-50 border border-success/20 bg-emerald-950/90 text-emerald-300 backdrop-blur-md"
          >
            <CheckCircle2 size={18} className="text-success animate-bounce" />
            <div className="flex flex-col text-left">
              <span className="text-xs font-semibold text-white">Action Successful</span>
              <span className="text-[10px] opacity-80">
                {copiedLink ? 'Shareable company link copied to clipboard!' : 'Aggregated BI report markdown copied!'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
