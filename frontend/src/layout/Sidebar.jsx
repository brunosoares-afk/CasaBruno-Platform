import {
    Box,
    Typography,
    Divider,
    List,
    ListItemButton,
    ListItemText
} from "@mui/material";

const itens = [

    {
        nome: "Dashboard",
        page: "dashboard"
    },

    {
        nome: "Android",
        page: "android"
    },

    {
        nome: "Rede",
        page: "network"
    },

    {
        nome: "Docker",
        page: "docker"
    },

    {
        nome: "Home Assistant",
        page: "homeassistant"
    },

    {
        nome: "MikroTik",
        page: "mikrotik"
    },

    {
        nome: "Configurações",
        page: "settings"
    }

];

export default function Sidebar({

    page,
    setPage

}) {

    return (

        <Box
            sx={{
                width: 270,
                bgcolor: "background.paper",
                borderRight: "1px solid rgba(255,255,255,.05)"
            }}
        >

            <Typography
                variant="h5"
                sx={{
                    p:3,
                    fontWeight:700,
                    color:"primary.main"
                }}
            >

                CBOS

            </Typography>

            <Divider />

            <List>

                {

                    itens.map(item => (

                        <ListItemButton

                            key={item.page}

                            selected={page===item.page}

                            onClick={()=>setPage(item.page)}

                        >

                            <ListItemText
                                primary={item.nome}
                            />

                        </ListItemButton>

                    ))

                }

            </List>

        </Box>

    );

}
