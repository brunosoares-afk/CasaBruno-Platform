import { Grid, Typography, Card, CardContent, Box } from "@mui/material";
import MemoryIcon from "@mui/icons-material/Memory";
import StorageIcon from "@mui/icons-material/Storage";
import RouterIcon from "@mui/icons-material/Router";
import SmartToyIcon from "@mui/icons-material/SmartToy";

export default function Dashboard() {
  const cards = [
    {
      title: "CPU",
      value: "-- %",
      icon: <MemoryIcon fontSize="large" />,
    },
    {
      title: "Memória",
      value: "-- %",
      icon: <StorageIcon fontSize="large" />,
    },
    {
      title: "Rede",
      value: "Online",
      icon: <RouterIcon fontSize="large" />,
    },
    {
      title: "Fred",
      value: "Ativo",
      icon: <SmartToyIcon fontSize="large" />,
    },
  ];

  return (
    <>
      <Typography
        variant="h4"
        sx={{
          mb: 4,
          fontWeight: 700,
        }}
      >
        Dashboard
      </Typography>

      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid size={{ xs: 12, md: 3 }} key={card.title}>
            <Card>
              <CardContent>
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <Box>
                    <Typography color="text.secondary">
                      {card.title}
                    </Typography>

                    <Typography variant="h5" sx={{ mt: 1 }}>
                      {card.value}
                    </Typography>
                  </Box>

                  {card.icon}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  );
}
