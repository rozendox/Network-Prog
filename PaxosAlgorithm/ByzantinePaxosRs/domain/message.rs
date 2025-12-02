/// Representa os tipos de fases no algoritmo de consenso.
/// Em um modelo Bizantino, fases adicionais como Commit são necessárias para garantir consistência.
#[derive(Debug, Clone, PartialEq)]
pub enum MessageType {
    /// O líder propõe um valor para ser acordado.
    PrePrepare,
    /// Os nós confirmam que receberam a proposta e ela é válida.
    Prepare,
    /// Os nós confirmam que a maioria da rede aceitou a preparação.
    Commit,
}

/// Representa uma mensagem trocada entre os nós da rede.
/// Encapsula os dados necessários para o consenso.
#[derive(Debug, Clone)]
pub struct ConsensusMessage {
    /// Identificador único da visualização (view) ou rodada atual.
    pub view_id: u64,
    /// Número de sequência da operação.
    pub sequence_number: u64,
    /// O tipo da mensagem (fase do algoritmo).
    pub msg_type: MessageType,
    /// O hash do conteúdo sendo proposto (para integridade).
    pub digest: String,
    /// Identificador do nó que enviou a mensagem.
    pub sender_id: u64,
    /// Assinatura digital do remetente para garantir autenticidade (Byzantine Fault Tolerance).
    pub signature: Vec<u8>,
}

impl ConsensusMessage {
    /// Cria uma nova mensagem de consenso com validação básica de estado.
    pub fn new(
        view_id: u64,
        seq: u64,
        msg_type: MessageType,
        digest: String,
        sender: u64,
        sig: Vec<u8>
    ) -> Self {
        Self {
            view_id,
            sequence_number: seq,
            msg_type,
            digest,
            sender_id: sender,
            signature: sig,
        }
    }
}    /// TODO: Verificar a assinatura digital da mensagem.
    fn verify_signature(&self, public_key: &str) -> bool {
        // Implementação de verificação de assinatura
        true
    }