import axios from "axios";

import { clearGerenciaToken, getGerenciaToken } from "./gerenciaAuth";

// Caminho relativo (mesma origem) — funciona tanto acessando direto
// (http://<ip>:5173/casa/) quanto via HTTPS pelo nginx-proxy-manager
// (https://hda08fx9s7v.sn.mynetname.net/casa/), que faz proxy do /casa
// pro Vite; o Vite por sua vez tira o prefixo /casa/api antes de repassar
// pro backend (ver vite.config.js). Precisa ser relativo pra não tentar
// abrir HTTPS direto na porta 8090 do backend (sem certificado) quando a
// página é servida via HTTPS — ver memória casa-bruno-custom-frontend-dashboard.
const api = axios.create({
    baseURL: "/casa/api",
    timeout: 15000,
});

// Anexa o token da Gerência quando existir — rotas que não exigem login
// simplesmente ignoram o header. Em 401 (token ausente/expirado), limpa o
// token local e avisa quem estiver escutando (Gerencia.jsx volta pro login).
api.interceptors.request.use((config) => {
    const token = getGerenciaToken();
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            clearGerenciaToken();
            window.dispatchEvent(new Event("gerencia-auth-expired"));
        }
        return Promise.reject(error);
    }
);

export default api;
