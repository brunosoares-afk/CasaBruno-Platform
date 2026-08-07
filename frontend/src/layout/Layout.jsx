import { useState } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";

import Dashboard from "../pages/Dashboard";
import AndroidDashboard from "../pages/AndroidDashboard";
import HomeAssistant from "../pages/HomeAssistant";
import Mikrotik from "../pages/Mikrotik";
import Network from "../pages/Network";
import Docker from "../pages/Docker";
import Settings from "../pages/Settings";

import { Box } from "@mui/material";

export default function Layout() {

    const [page, setPage] = useState("dashboard");

    const renderPage = () => {

        switch (page) {

            case "android":
                return <AndroidDashboard />;

            case "homeassistant":
                return <HomeAssistant />;

            case "mikrotik":
                return <Mikrotik />;

            case "network":
                return <Network />;

            case "docker":
                return <Docker />;

            case "settings":
                return <Settings />;

            default:
                return <Dashboard />;
        }

    };

    return (

        <Box sx={{ display: "flex" }}>

            <Sidebar
                page={page}
                setPage={setPage}
            />

            <Box sx={{ flex: 1 }}>

                <Header />

                <Box sx={{ p: 3 }}>

                    {renderPage()}

                </Box>

            </Box>

        </Box>

    );

}
