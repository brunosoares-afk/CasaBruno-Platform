import { AppBar, Toolbar, Typography, Box, Chip } from "@mui/material";

export default function Header() {
  return (
    <AppBar
      position="static"
      elevation={0}
      sx={{
        background: "#111827",
        borderBottom: "1px solid #1f2937"
      }}
    >
      <Toolbar>

        <Typography
          variant="h5"
          sx={{
            fontWeight: "bold",
            flexGrow: 1
          }}
        >
          CasaBruno Platform
        </Typography>

        <Box>

          <Chip
            label="ONLINE"
            color="success"
          />

        </Box>

      </Toolbar>
    </AppBar>
  );
}
