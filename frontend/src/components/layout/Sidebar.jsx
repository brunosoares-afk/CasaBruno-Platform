import {
  Drawer,
  Toolbar,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from "@mui/material";

import {
  MdDashboard,
  MdRouter,
  MdHome,
  MdDns,
  MdSettings,
  MdSmartToy
} from "react-icons/md";

const menu = [
  { text: "Dashboard", icon: <MdDashboard /> },
  { text: "Docker", icon: <MdDns /> },
  { text: "Home Assistant", icon: <MdHome /> },
  { text: "MikroTik", icon: <MdRouter /> },
  { text: "Jarvis IA", icon: <MdSmartToy /> },
  { text: "Configurações", icon: <MdSettings /> }
];

export default function Sidebar() {
  return (
    <Drawer
      variant="permanent"
      sx={{
        width: 250,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: 250,
          boxSizing: "border-box",
          backgroundColor: "#0f172a",
          color: "#fff"
        }
      }}
    >
      <Toolbar />

      <List>
        {menu.map((item) => (
          <ListItemButton key={item.text}>
            <ListItemIcon sx={{ color: "#60a5fa" }}>
              {item.icon}
            </ListItemIcon>

            <ListItemText primary={item.text} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
