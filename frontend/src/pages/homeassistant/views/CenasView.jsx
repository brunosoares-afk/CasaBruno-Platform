import ActionButtonGrid from "../widgets/ActionButtonGrid";

const CENAS = [
    { label: "Cena UniTV", domain: "script", service: "turn_on", entityId: "script.fred_scene_unitv" },
    { label: "Cena Desenho Heitor", domain: "script", service: "turn_on", entityId: "script.fred_scene_desenho_heitor" },
    { label: "UniTV Projetor", domain: "scene", service: "turn_on", entityId: "scene.unitv_projetor" },
];

export default function CenasView() {
    return <ActionButtonGrid title="Cenas T&B Residencial" actions={CENAS} columns={3} />;
}
