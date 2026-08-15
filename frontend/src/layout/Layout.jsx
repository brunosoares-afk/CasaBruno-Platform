import { useState } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";

import HomeAssistant from "../pages/HomeAssistant";
import Gerencia from "../pages/Gerencia";

import { Box, Drawer, useMediaQuery, useTheme } from "@mui/material";

function getInitialPage() {
    const params = new URLSearchParams(window.location.search);
    return params.get("page") || "homeassistant";
}

function isKioskMode() {
    const params = new URLSearchParams(window.location.search);
    return params.get("kiosk") === "1";
}

export default function Layout() {

    const theme = useTheme();
    const isMobile = useMediaQuery(theme.breakpoints.down("sm"));

    const kioskMode = isKioskMode();
    const [page, setPage] = useState(getInitialPage);
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navigate = (nextPage) => {
        setPage(nextPage);
        if (isMobile) setSidebarOpen(false);
    };

    const renderPage = () => {

        switch (page) {

            case "gerencia":
                return <Gerencia />;

            default:
                return <HomeAssistant />;
        }

    };

    return (

        <Box sx={{ display: "flex", height: "100vh" }}>

            {isMobile ? (
                <Drawer
                    variant="temporary"
                    open={sidebarOpen}
                    onClose={() => setSidebarOpen(false)}
                    ModalProps={{ keepMounted: true }}
                >
                    <Sidebar
                        page={page}
                        setPage={navigate}
                    />
                </Drawer>
            ) : (
                sidebarOpen && (
                    <Sidebar
                        page={page}
                        setPage={navigate}
                    />
                )
            )}

            <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>

                {!kioskMode && (
                    <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />
                )}

                <Box sx={{ p: 3, flex: 1, overflowY: "auto" }}>

                    {renderPage()}

                </Box>

            </Box>

        </Box>

    );

}
