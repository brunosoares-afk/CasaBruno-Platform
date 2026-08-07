import axios from "axios";

const api = axios.create({
    baseURL: `${window.location.protocol}//${window.location.hostname}:8090`,
    timeout: 15000,
});

export default api;
