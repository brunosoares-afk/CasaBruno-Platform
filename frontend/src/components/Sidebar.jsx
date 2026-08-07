import {
  FaHome,
  FaDocker,
  FaServer,
  FaRobot,
  FaNetworkWired,
  FaCog,
} from "react-icons/fa";

export default function Sidebar() {
  return (
    <aside className="sidebar">

      <h2>CBOS</h2>

      <nav>

        <button><FaHome /> Dashboard</button>

        <button><FaDocker /> Docker</button>

        <button><FaServer /> Home Assistant</button>

        <button><FaNetworkWired /> MikroTik</button>

        <button><FaRobot /> IA</button>

        <button><FaCog /> Configurações</button>

      </nav>

    </aside>
  );
}
