import {
    Grid,
    IconButton,
    Paper
} from "@mui/material";

import {
    ArrowUpward,
    ArrowDownward,
    ArrowBack,
    ArrowForward,
    Home,
    KeyboardReturn,
    Menu,
    Check
} from "@mui/icons-material";

import api from "../../services/api";

export default function RemoteControl({ device }) {

    const run = async (command) => {

        await api.get(`/android/${device}/${command}`);

    };

    return (

        <Paper
            sx={{
                mt: 3,
                p: 2,
                borderRadius: 3
            }}
        >

            <Grid container spacing={1} justifyContent="center">

                <Grid size={12} textAlign="center">

                    <IconButton onClick={() => run("up")}>
                        <ArrowUpward />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton onClick={() => run("left")}>
                        <ArrowBack />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton
                        color="primary"
                        onClick={() => run("ok")}
                    >
                        <Check />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton onClick={() => run("right")}>
                        <ArrowForward />
                    </IconButton>

                </Grid>

                <Grid size={12} textAlign="center">

                    <IconButton onClick={() => run("down")}>
                        <ArrowDownward />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton onClick={() => run("home")}>
                        <Home />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton onClick={() => run("back")}>
                        <KeyboardReturn />
                    </IconButton>

                </Grid>

                <Grid size={4} textAlign="center">

                    <IconButton onClick={() => run("menu")}>
                        <Menu />
                    </IconButton>

                </Grid>

            </Grid>

        </Paper>

    );

}
