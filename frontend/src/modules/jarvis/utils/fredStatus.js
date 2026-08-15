// Mensagens amigáveis pros códigos de erro do SpeechRecognition (Web Speech
// API) — sem isso o usuário só via "Fred inativo" sem nenhuma pista do que
// deu errado de verdade (permissão negada vs sem mic vs sem rede etc.).
const MIC_ERROR_LABELS = {
    "not-allowed": "Microfone bloqueado",
    "service-not-allowed": "Microfone bloqueado",
    "audio-capture": "Sem microfone",
    "network": "Sem rede de voz",
};

// Mapeia o estado bruto do useJarvis() (voz/processamento) para o estado
// visual do FredOrb + um rótulo textual — única fonte de verdade usada tanto
// no header quanto em qualquer outro lugar que precise mostrar o status do Fred.
export function getFredStatus({ supported, micEnabled, listenStatus, processing, micError }) {
    if (!supported) return { state: "inactive", label: "Voz indisponível" };
    if (!micEnabled) return { state: "inactive", label: "Microfone desligado" };
    if (processing === "thinking") return { state: "thinking", label: "Pensando..." };
    if (processing === "speaking") return { state: "speaking", label: "Falando..." };
    if (listenStatus === "capturing") return { state: "capturing", label: "Fred ouvindo comando..." };
    if (listenStatus === "listening") return { state: "listening", label: "Fred Online" };
    if (micError) return { state: "error", label: MIC_ERROR_LABELS[micError] || `Erro no microfone (${micError})` };
    return { state: "inactive", label: "Fred inativo" };
}
