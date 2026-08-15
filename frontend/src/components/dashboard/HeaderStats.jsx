import ChatBubbleOutlineIcon from "@mui/icons-material/ChatBubbleOutlined";
import MicIcon from "@mui/icons-material/Mic";
import WhatsAppIcon from "@mui/icons-material/WhatsApp";
import BoltIcon from "@mui/icons-material/Bolt";

import SwitchCard from "./SwitchCard";

// Mesmo visual dos cards de Cenas/Controles/Presença (ícone + texto numa
// linha só) em vez do grid de chips antigo — que espremia demais numa
// coluna estreita e quebrava os rótulos letra por letra.
export default function HeaderStats({ stats, automationsOn, automationsTotal }) {

    const byChannel = stats?.by_channel || {};
    const total = stats?.total ?? 0;
    const voice = byChannel.voice || 0;
    const whatsapp = byChannel.whatsapp || 0;

    return (
        <>
            <SwitchCard
                icon={<ChatBubbleOutlineIcon fontSize="small" />}
                name="Comandos hoje"
                stateLabel={`${total} · últimas ${stats?.since_hours ?? 24}h`}
            />

            <SwitchCard
                icon={<MicIcon fontSize="small" />}
                name="Voz"
                stateLabel={String(voice)}
            />

            <SwitchCard
                icon={<WhatsAppIcon fontSize="small" />}
                name="WhatsApp"
                stateLabel={String(whatsapp)}
            />

            <SwitchCard
                icon={<BoltIcon fontSize="small" />}
                name="Automações ativas"
                stateLabel={`${automationsOn}/${automationsTotal}`}
            />
        </>
    );

}
