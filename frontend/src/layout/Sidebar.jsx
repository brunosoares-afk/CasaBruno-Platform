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
        nome: "Principal",
        page: "homeassistant"
    },

    {
        nome: "Gerência",
        page: "gerencia"
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
                borderRight: "1px solid rgba(255,255,255,.05)",
                height: "100vh",
                overflowY: "auto",
                flexShrink: 0
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

                CASA INTELIGENTE

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
