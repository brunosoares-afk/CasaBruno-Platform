import { Accordion, AccordionDetails, AccordionSummary, Box, Paper, Typography } from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

// Manual de uso do Fred (pedido do Bruno 2026-09-24: todo projeto tem manual, e ele é atualizado
// a cada mudança). Só descreve o que existe de verdade no código — frases de comando conferidas
// em backend/app/services/intent_engine.py, automações em automations_service.py.

const secoes = [
    {
        titulo: "Como falar com o Fred",
        itens: [
            ["WhatsApp", "Mande mensagem de texto ou áudio para o número do Fred. Ele só responde ao Bruno e à Taiane — qualquer outro número é ignorado, por segurança. Áudio é transcrito e a resposta pode vir em voz."],
            ["Aqui no painel, por voz", "Com o microfone liberado no navegador, diga a palavra de ativação (\"Fred\" ou \"Jarvis\") e depois o comando. As palavras podem ser trocadas em Gerência › Configurações › Fred — Voz e Palavra de Ativação."],
            ["O rosto do Fred (status)", "O rostinho no topo mostra o estado: Fred Online (esperando a palavra de ativação), ouvindo comando, pensando, falando. \"Microfone bloqueado\" ou \"Sem microfone\" = libere o microfone no navegador. \"Microfone desligado\" = foi desligado no painel."],
            ["Reconhecimento pela câmera do aparelho", "Na aba Início, com a câmera do aparelho liberada, o Fred reconhece quem está usando o painel e cumprimenta pelo nome (quem ele não conhece recebe um boas-vindas genérico). Precisa abrir o painel pelo endereço https."],
        ],
    },
    {
        titulo: "O que pedir ao Fred (exemplos)",
        itens: [
            ["Aparelhos", "\"liga a luz da cozinha\", \"desliga o ar\", \"liga a tv da sala\", \"aumenta volume da tv da sala\", \"abre o portão\". Dá pra juntar: \"liga a luz da cozinha e desliga o ar\" — ele só executa se entender cada parte; se não, trata como uma frase só."],
            ["Cenas por frase", "\"boa noite\" / \"modo dormir\", \"bom dia\", \"vou sair\", \"estou chegando\" (de carro, abre o portão), \"chegando a pé\", \"quero assistir filme\", \"acabou o filme\", \"está calor\", \"não perturbe\", \"silêncio total\"."],
            ["Perguntas", "\"quem está em casa?\", \"como está a casa?\", \"como está a internet?\", \"vai chover?\" / previsão do tempo, \"que horas são?\", status de um aparelho (\"a luz da cozinha está ligada?\")."],
            ["Finanças", "Fale do gasto normalmente — \"gastei 45 no mercado no pix\" — e ele lança no app Casa (aba Finanças) no nome de quem mandou."],
            ["CRM", "Peça para anotar um contato, negociação ou tarefa (\"anota uma tarefa de ligar pro fornecedor amanhã\") e ele registra no AgentCRM."],
            ["Conversa livre", "Fora dos comandos, ele conversa normalmente e lembra do que cada pessoa já contou."],
        ],
    },
    {
        titulo: "Principal — as abas do painel",
        itens: [
            ["Início", "Status geral da casa, quem está em casa (pelo celular conectado no Wi-Fi), reconhecimento facial da câmera e a planta da casa com ícones que acendem conforme o estado real (luz, portão etc.)."],
            ["Câmeras", "Imagem ao vivo das câmeras da frente e externa."],
            ["Equipamentos", "Botões para cada aparelho: iluminação, ar, portão (pulso), projetor, BTV13, Alexa e detecção facial."],
            ["Áreas", "Os aparelhos agrupados por cômodo."],
            ["Cenas", "Atalhos que fazem várias coisas de uma vez (Bom Dia, Boa Noite, Modo Cinema, Chegando de Carro/a Pé, Saída de Casa…). Marque as mais usadas como favoritas."],
            ["Automações", "Liga/desliga cada automação (lista abaixo) e \"Executar agora\" para testar."],
            ["Rede", "Situação do MikroTik (identidade e CPU), dos roteadores (principal, sogra, TV) e dos aparelhos Android via ADB (BTV13, projetor)."],
            ["Agenda", "Seus compromissos do Google Agenda e criação de eventos. Na primeira vez, clique em \"Conectar Google Agenda\"."],
            ["Finanças", "O app Casa (controle financeiro) dentro do painel."],
        ],
    },
    {
        titulo: "Automações e avisos no WhatsApp",
        itens: [
            ["Presença", "Chegada em casa depois das 18h acende a luz da cozinha; casa vazia roda \"Saída de Casa\" sozinho e, a cada 30 min, confere se ar/luz ficaram ligados; ar liga sozinho quando alguém chega e está 28°C ou mais lá fora; aviso quando o Heitor chega."],
            ["Câmeras", "Placa cadastrada em Gerência › Placas abre o portão e avisa; rosto da família de manhã manda \"bom dia\" e pode acender a luz da cozinha; rosto desconhecido com a casa vazia gera alerta."],
            ["Rotina", "Previsão do tempo de manhã, agenda do dia seguinte à noite, lembretes cadastrados, aviso de luz ligada de dia, resumo semanal de uso (domingo à noite)."],
            ["Modo Férias", "Acende e apaga a luz da cozinha em horários aleatórios à noite para parecer que tem gente. Fica desligado — ligue em Automações antes de viajar e desligue na volta."],
            ["Avisos de sistema", "BTV13 sem conexão ADB, queda do link de internet, algum projeto do servidor fora do ar (pelo AgentCRM) e vencimentos do Detran na frota (8h)."],
        ],
    },
    {
        titulo: "Gerência (com senha)",
        itens: [
            ["Android, Rede, Docker, MikroTik", "Painéis técnicos: aparelhos Android via ADB, dispositivos da rede, containers do servidor e o roteador MikroTik (identidade, CPU, DHCP)."],
            ["Rostos", "Cadastrar alguém no reconhecimento facial: a pessoa fica de frente para a câmera, digite o nome, clique \"Capturar\" algumas vezes e depois \"Treinar modelo\" — vale na hora, sem reiniciar nada."],
            ["Placas", "Placas de confiança que abrem o portão sozinhas. A leitura tolera até 2 caracteres trocados (ex.: 0 no lugar de O)."],
            ["Configurações", "Voz e palavra de ativação do Fred, lembretes (com vencimento), planta da casa e seus marcadores, Google Agenda, aparelhos Tuya adicionados à mão, acesso ao MikroTik e dispositivos de rede monitorados."],
        ],
    },
];

export default function Manual() {
    return (
        <Box sx={{ maxWidth: 900, mx: "auto" }}>
            <Typography variant="h5" sx={{ fontWeight: 800, mb: 0.5 }}>Manual do Fred</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>Atualizado em 24/09/2026.</Typography>
            {secoes.map((s) => (
                <Paper key={s.titulo} variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 3 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 800, mb: 1 }}>{s.titulo}</Typography>
                    {s.itens.map(([t, texto]) => (
                        <Accordion key={t} disableGutters elevation={0} sx={{ bgcolor: "transparent", "&:before": { display: "none" }, borderTop: 1, borderColor: "divider" }}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                <Typography sx={{ fontWeight: 700 }}>{t}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>{texto}</Typography>
                            </AccordionDetails>
                        </Accordion>
                    ))}
                </Paper>
            ))}
        </Box>
    );
}
