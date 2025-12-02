/// Define o contrato para operações criptográficas.
/// Essencial para tolerância a falhas bizantinas (verificação de assinaturas).
pub trait CryptoPort {
    /// Assina um payload de dados.
    fn sign(&self, data: &[u8]) -> Vec<u8>;
    
    /// Verifica se uma assinatura corresponde aos dados e à chave pública do remetente.
    fn verify(&self, sender_id: u64, data: &[u8], signature: &[u8]) -> bool;
}
