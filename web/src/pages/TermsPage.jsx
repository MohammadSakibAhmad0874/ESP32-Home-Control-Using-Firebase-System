import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, ArrowLeft } from 'lucide-react';
import Header from '../components/Header';

export default function TermsPage({ user, role }) {
  return (
    <div className="min-h-screen bg-[#0B0E14] bg-grid-glow flex flex-col text-[#DDE3E8]">
      <Header user={user} role={role} />

      <main className="flex-1 max-w-4xl mx-auto px-4 lg:px-8 py-12">
        <Link to="/" className="inline-flex items-center gap-2 text-xs font-semibold text-[#00D9FF] hover:underline mb-8">
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Home</span>
        </Link>

        <div className="glass-panel p-8 sm:p-12 space-y-8">
          <div className="flex items-center gap-3 pb-6 border-b border-white/10">
            <div className="w-12 h-12 rounded-xl bg-[#FF2E93]/10 text-[#FF2E93] flex items-center justify-center">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h1 className="font-heading text-3xl font-extrabold text-white">Terms of Service</h1>
              <p className="text-xs text-[#8B9BB4] mt-1">ApnaGhar IoT Platform &bull; Last Updated: October 2026</p>
            </div>
          </div>

          <section className="space-y-3">
            <h2 className="font-heading text-lg font-bold text-white">1. Authorized Hardware Control</h2>
            <p className="text-sm text-[#8B9BB4] leading-relaxed">
              By using ApnaGhar, you agree to only link and control IoT devices that you legally own or operate with explicit authorization. Tampering with or controlling unauthorized electrical relays is strictly prohibited.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="font-heading text-lg font-bold text-white">2. Electrical Safety &amp; Disclaimers</h2>
            <p className="text-sm text-[#8B9BB4] leading-relaxed">
              ApnaGhar manages physical AC power relays. You are responsible for proper installation conforming to local electrical codes. The authors and maintainers provide this software on an "as-is" basis and accept no liability for hardware damage or network interruptions.
            </p>
          </section>

          <section className="space-y-3">
            <h2 className="font-heading text-lg font-bold text-white">3. Open Source Licensing</h2>
            <p className="text-sm text-[#8B9BB4] leading-relaxed">
              ApnaGhar firmware and web applications are open source under the MIT License on{' '}
              <a href="https://github.com/MohammadSakibAhmad0874/ESP32-Home-Control-Using-Firebase-System" target="_blank" rel="noreferrer" className="text-[#00D9FF] hover:underline">
                GitHub
              </a>.
            </p>
          </section>
        </div>
      </main>
    </div>
  );
}
