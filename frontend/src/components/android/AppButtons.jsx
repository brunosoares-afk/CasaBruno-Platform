import { Stack, Button } from "@mui/material";
import api from "../../services/api";

export default function AppButtons({ device }) {

    const run = async (command) => {

        await api.get(`/android/${device}/${command}`);

    };

    return (

        <Stack
            direction="row"
            spacing={1}
            flexWrap="wrap"
            mb={3}
        >

            <Button
                variant="contained"
                onClick={() => run("youtube")}
            >
                YouTube
            </Button>

            <Button
                variant="contained"
                color="secondary"
                onClick={() => run("unitv")}
            >
                UniTV
            </Button>

            <Button
                variant="outlined"
                onClick={() => run("power")}
            >
                Power
            </Button>

        </Stack>

    );

}
