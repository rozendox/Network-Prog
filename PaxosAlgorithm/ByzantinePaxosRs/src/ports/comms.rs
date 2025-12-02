// src/ports/comms.rs
use crate::domain::message::ConsensusMessage;

/// Define o contrato para comunicação entre nós.
/// Permite trocar a implementação de rede (TCP, UDP, Mock) sem afetar a lógica de negócio.
pub trait NetworkPort {
    /// Envia uma mensagem para todos os outros nós da rede (Broadcast).
    fn broadcast(&self, message: ConsensusMessage) -> Result<(), String>;
    
    /// Envia uma mensagem para um nó específico.
    fn send_to(&self, target_id: u64, message: ConsensusMessage) -> Result<(), String>;
}

