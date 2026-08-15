const TOKEN_KEY = "gerencia_token";

export function getGerenciaToken() {
    return localStorage.getItem(TOKEN_KEY);
}

export function setGerenciaToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

export function clearGerenciaToken() {
    localStorage.removeItem(TOKEN_KEY);
}
