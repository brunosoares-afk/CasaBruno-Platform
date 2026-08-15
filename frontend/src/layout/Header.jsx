import {

    Box,
    Chip,
    IconButton

} from "@mui/material";

import MenuIcon from "@mui/icons-material/Menu";

import { useJarvis } from "../modules/jarvis/context/JarvisContext";
import { getFredStatus } from "../modules/jarvis/utils/fredStatus";
import FredOrb from "../components/dashboard/FredOrb";

const CHIP_COLOR = {
    inactive: "default",
    listening: "success",
    capturing: "info",
    thinking: "warning",
    speaking: "secondary",
    error: "error",
};

export default function Header({ onToggleSidebar }) {

    const { supported, micEnabled, listenStatus, processing, micError } = useJarvis();
    const status = getFredStatus({ supported, micEnabled, listenStatus, processing, micError });
    const chip = { label: status.label, color: CHIP_COLOR[status.state] || "default" };

    return (

        <Box
            sx={{

                height: 120,

                px: 3,

                display: "flex",

                justifyContent: "space-between",

                alignItems: "center",

                borderBottom: "1px solid rgba(255,255,255,.05)",

                position: "relative",

                overflow: "hidden",

                backgroundImage: `url(${import.meta.env.BASE_URL}fred_banner.webp)`,

                backgroundSize: "cover",

                backgroundPosition: "center",

                "&::before": {
                    content: '""',
                    position: "absolute",
                    inset: 0,
                    background: "linear-gradient(90deg, rgba(8,17,31,.85) 0%, rgba(8,17,31,.35) 55%, rgba(8,17,31,.75) 100%)",
                },

            }}
        >

            <Box sx={{ position: "relative", zIndex: 1, display: "flex", alignItems: "center", gap: 1.5 }}>

                <IconButton onClick={onToggleSidebar}>
                    <MenuIcon />
                </IconButton>

            </Box>

            <Box sx={{ position: "relative", zIndex: 1, display: "flex", alignItems: "center", gap: 1 }}>

                <FredOrb state={status.state} size={22} />

                <Chip

                    label={chip.label}

                    color={chip.color}

                />

            </Box>

        </Box>

    );

}
