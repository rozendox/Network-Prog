// src/ports/comms.rs
use crate::domain::message::ConsensusMessage;

/// Define o contrato para comunicação entre nós.
/// Permite trocar a implementação de rede (TCP, UDP, Mock) sem afetar a lógica de negócio.
pub trait NetworkPort {

}
    

    
// src/ports/crypto.rs

/// Define o contrato para operações criptográficas.
/// Essencial para tolerância a falhas bizantinas (verificação de assinaturas).
pub trait CryptoPort {
    /// Assina um payload de dados.
}