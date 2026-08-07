import Sidebar from "./Sidebar";
import Header from "./Header";
import Dashboard from "./Dashboard";

export default function Layout() {
  return (
    <div className="layout">
      <Sidebar />

      <div className="content">
        <Header />
        <Dashboard />
      </div>
    </div>
  );
}
