import { useState } from 'react'
import axios from 'axios'

function App() {
  const [tenderFile, setTenderFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [status, setStatus] = useState("Awaiting Upload");
  const [evaluations, setEvaluations] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeModal, setActiveModal] = useState(null);
  const [criteria, setCriteria] = useState("");

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setTenderFile(file);
      if (file.type === "application/pdf") setPdfUrl(URL.createObjectURL(file));
      setEvaluations([]);
      setStatus("Ready to Extract");
    }
  };

  const handleUpload = async () => {
    if (!tenderFile) return setStatus("Please select a file.");
    const formData = new FormData();
    formData.append("file", tenderFile);
    formData.append("criteria", criteria);
    
    setIsProcessing(true);
    setStatus("AI Engine: Auditing Compliance...");
    
    try {
      // Find your axios call and update it
      const response = await axios.post("https://bidoptic-backend.onrender.com/upload-tender/", formData);
      setEvaluations(response.data.results);
      setStatus("Analysis Complete");
    } catch (error) {
      setStatus("Backend Error. Check terminal.");
    } finally {
      setIsProcessing(false);
    }
  };

  const getTheme = (type) => {
    if (type === 'pass') return { border: 'border-l-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50', icon: '✓' };
    if (type === 'review') return { border: 'border-l-amber-500', text: 'text-amber-700', bg: 'bg-amber-50', icon: '!' };
    return { border: 'border-l-rose-500', text: 'text-rose-700', bg: 'bg-rose-50', icon: '✕' };
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 antialiased">
      <header className="bg-white border-b border-slate-200 px-10 py-6 flex justify-between items-center shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold text-3xl">B</div>
          <h1 className="text-3xl font-black text-slate-900 tracking-tighter italic">BidOptic</h1>
        </div>
      </header>

      <main className="p-10 w-full max-w-[98%] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10">
        {/* Left: Input */}
        <section className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm flex flex-col h-[calc(100vh-160px)]">
          <h2 className="text-xl font-bold mb-6 italic underline decoration-blue-500 underline-offset-8">Document & Rules Input</h2>
          <div className="space-y-6 mb-6">
            <input type="file" onChange={handleFileChange} className="w-full text-sm text-slate-500 file:bg-blue-50 file:text-blue-700 file:border-0 file:py-3 file:px-6 file:rounded-xl file:font-bold border border-slate-100 p-1.5 rounded-2xl" />
            <textarea value={criteria} onChange={(e) => setCriteria(e.target.value)} placeholder="Enter eligibility criteria..." className="w-full p-5 bg-slate-50 border border-slate-200 rounded-2xl min-h-[120px] outline-none font-medium" />
            <button onClick={handleUpload} disabled={isProcessing} className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl shadow-xl active:scale-95 transition-all">
              {isProcessing ? "PROCESSING..." : "EXTRACT & VERIFY"}
            </button>
          </div>
          <div className="flex-1 bg-slate-100 rounded-2xl overflow-hidden">
            {pdfUrl ? <iframe src={pdfUrl} className="w-full h-full" /> : <div className="h-full flex items-center justify-center opacity-20 font-bold italic">Viewer Ready</div>}
          </div>
        </section>

        {/* Right: Results */}
        <section className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm h-[calc(100vh-160px)] overflow-y-auto">
          <h2 className="text-xl font-bold mb-6 italic underline decoration-emerald-500 underline-offset-8">Extracted Compliance Ledger</h2>
          <div className="space-y-6">
            {evaluations.map((item) => {
              const theme = getTheme(item.type);
              return (
                <div key={item.id} className={`bg-white border border-slate-200 border-l-[6px] ${theme.border} rounded-2xl shadow-sm`}>
                  <div className={`px-6 py-2 flex justify-between items-center ${theme.bg}`}>
                    <span className={`text-[10px] font-black uppercase tracking-widest ${theme.text}`}>{item.title}</span>
                    <span className="text-[10px] font-bold text-slate-400 uppercase">{item.confidence}</span>
                  </div>
                  <div className="p-6">
                    <p className="font-bold text-slate-800 text-lg mb-4">{item.rule}</p>
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 italic text-slate-600 text-sm">
                        "{item.found}"
                    </div>
                  </div>
                  <div className="px-6 py-3 border-t border-slate-50 flex justify-end">
                    <button onClick={() => setActiveModal(item)} className={`text-[11px] font-black uppercase ${theme.text} hover:underline`}>VIEW SOURCE PROOF →</button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </main>

      {/* Proof Modal */}
      {activeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/90 backdrop-blur-md p-10 animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl w-full max-w-5xl h-full flex flex-col shadow-2xl overflow-hidden">
             <div className="p-8 border-b flex justify-between items-center bg-slate-50">
               <h3 className="font-black text-slate-900 uppercase tracking-widest text-sm">SOURCE PROOF: {activeModal.rule}</h3>
               <button onClick={() => setActiveModal(null)} className="text-slate-400 hover:text-black font-bold text-xs uppercase">CLOSE INSPECTOR</button>
             </div>
             <div className="flex-1 bg-slate-200 p-12 overflow-y-auto flex justify-center">
                <div className="bg-white w-[700px] h-fit min-h-full shadow-2xl p-16 relative border border-slate-300 font-serif leading-loose text-slate-100">
                    <div className="h-4 bg-slate-50 w-full mb-6 rounded"></div><div className="h-4 bg-slate-50 w-3/4 mb-6 rounded"></div>
                    <div className="my-10 border-4 border-amber-400 bg-amber-50 p-10 rounded-2xl relative shadow-xl transform scale-105">
                        <p className="text-amber-950 font-sans font-bold text-2xl italic leading-relaxed">"{activeModal.found}"</p>
                        <span className="absolute -top-4 left-6 bg-amber-400 text-white text-[10px] font-black px-3 py-1 rounded-full">AI VERIFIED EVIDENCE</span>
                    </div>
                    <div className="h-4 bg-slate-50 w-full mt-10 rounded"></div><div className="h-4 bg-slate-50 w-5/6 rounded"></div>
                </div>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;