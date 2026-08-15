import { useEffect, useState } from "react";
import { Alert, Box, Button, Paper, Tab, Tabs, TextField, Typography } from "@mui/material";

import api from "../services/api";
import { clearGerenciaToken, getGerenciaToken, setGerenciaToken } from "../services/gerenciaAuth";

import AndroidDashboard from "./AndroidDashboard";
import Network from "./Network";
import Docker from "./Docker";
import Mikrotik from "./Mikrotik";
import Settings from "./Settings";

const VIEWS = {
    android: AndroidDashboard,
    rede: Network,
    docker: Docker,
    mikrotik: Mikrotik,
    configuracoes: Settings,
};

function GerenciaLogin({ onSuccess }) {

    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);
        try {
            const res = await api.post("/api/auth/gerencia/login", { password });
            setGerenciaToken(res.data.token);
            onSuccess();
        } catch {
            setError("Senha incorreta.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box sx={{ display: "flex", justifyContent: "center", mt: { xs: 6, md: 12 }, px: 2 }}>

            <Paper component="form" onSubmit={handleSubmit} sx={{ p: 4, width: "100%", maxWidth: 340 }}>

                <Typography variant="h6" sx={{ mb: 3, fontWeight: 700 }}>
                    Gerência
                </Typography>

                <TextField
                    type="password"
                    label="Senha"
                    fullWidth
                    autoFocus
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    sx={{ mb: 2 }}
                />

                {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

                <Button type="submit" variant="contained" fullWidth disabled={loading || !password}>
                    Entrar
                </Button>

            </Paper>

        </Box>
    );

}

export default function Gerencia() {

    const [tab, setTab] = useState("android");
    const [checking, setChecking] = useState(() => !!getGerenciaToken());
    const [authorized, setAuthorized] = useState(false);

    useEffect(() => {

        if (!checking) return;

        api.get("/api/auth/gerencia/verify")
            .then(() => setAuthorized(true))
            .catch(() => clearGerenciaToken())
            .finally(() => setChecking(false));

    }, [checking]);

    useEffect(() => {

        const onExpired = () => setAuthorized(false);
        window.addEventListener("gerencia-auth-expired", onExpired);
        return () => window.removeEventListener("gerencia-auth-expired", onExpired);

    }, []);

    if (checking) return null;

    if (!authorized) {
        return <GerenciaLogin onSuccess={() => setAuthorized(true)} />;
    }

    const ActiveView = VIEWS[tab];

    return (
        <Box>
            <Typography variant="h4" sx={{ mb: 3, fontWeight: 700 }}>
                Gerência
            </Typography>

            <Tabs
                value={tab}
                onChange={(_, v) => setTab(v)}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ mb: 3 }}
            >
                <Tab value="android" label="Android" />
                <Tab value="rede" label="Rede" />
                <Tab value="docker" label="Docker" />
                <Tab value="mikrotik" label="MikroTik" />
                <Tab value="configuracoes" label="Configurações" />
            </Tabs>

            <ActiveView />
        </Box>
    );
}
