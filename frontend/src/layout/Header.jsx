import {

    Box,
    Typography,
    Chip

} from "@mui/material";

export default function Header() {

    return (

        <Box
            sx={{

                height: 72,

                px: 4,

                display: "flex",

                justifyContent: "space-between",

                alignItems: "center",

                borderBottom: "1px solid rgba(255,255,255,.05)",

                bgcolor: "background.paper"

            }}
        >

            <Typography variant="h5">

                T&B Residencial

            </Typography>

            <Chip

                label="Fred Online"

                color="success"

            />

        </Box>

    );

}
