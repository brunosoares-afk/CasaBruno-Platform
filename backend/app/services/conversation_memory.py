class ConversationMemory:

    def __init__(self, max_size: int = 5):

        self.max_size = max_size

        self.history = []

        self.last_context = None

    # ============================================
    # REGISTRA CONTEXTO ATUAL
    # ============================================

    def update_context(self, context: str):

        if not context:

            return

        self.last_context = context

        self.history.append(context)

        if len(self.history) > self.max_size:

            self.history.pop(0)

    # ============================================
    # CONTEXTO ATUAL OU RECENTE
    # ============================================

    def get_context(self):

        if self.last_context:

            return self.last_context

        if self.history:

            return self.history[-1]

        return None

    # ============================================
    # VERIFICA CONTEXTO ANTERIOR
    # ============================================

    def get_history(self):

        return self.history

    # ============================================
    # LIMPA MEMÓRIA
    # ============================================

    def reset(self):

        self.history = []

        self.last_context = None


conversation_memory = ConversationMemory()
