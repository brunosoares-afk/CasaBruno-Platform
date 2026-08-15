import Layout from "./layout/Layout";
import { JarvisProvider } from "./modules/jarvis/context/JarvisContext";
import { useHomeAssistantStatesSocket } from "./hooks/useHomeAssistantStatesSocket";

export default function App() {

    useHomeAssistantStatesSocket();

    return (

        <JarvisProvider>

            <Layout />

        </JarvisProvider>

    );

}
