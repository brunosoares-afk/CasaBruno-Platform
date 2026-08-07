import React from "react";
import ReactDOM from "react-dom/client";

import { ThemeProvider, CssBaseline } from "@mui/material";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import App from "./App";

import theme from "./theme/theme";

import "./styles/global.css";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>

        <ThemeProvider theme={theme}>

            <CssBaseline />

            <QueryClientProvider client={queryClient}>

                <App />

            </QueryClientProvider>

        </ThemeProvider>

    </React.StrictMode>
);
