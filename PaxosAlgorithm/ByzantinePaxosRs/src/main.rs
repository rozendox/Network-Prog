// src/main.rs

mod domain;
mod ports;
mod service;

// Mocks simples para demonstração (Adapter Layer)
struct MockNetwork;
struct MockCrypto;

impl crate::ports::comms::NetworkPort for MockNetwork {
    fn broadcast(&self, _msg: crate::domain::message::ConsensusMessage) -> Result<(), String> {
        println!("Network: Broadcast realizado.");
        Ok(())
    }
    fn send_to(&self, _target: u64, _msg: crate::domain::message::ConsensusMessage) -> Result<(), String> {
        Ok(())
    }
}

impl crate::ports::crypto::CryptoPort for MockCrypto {
    fn sign(&self, _data: &[u8]) -> Vec<u8> {
        vec![1, 2, 3] // Assinatura dummy
    }
    fn verify(&self, _sender: u64, _data: &[u8], _sig: &[u8]) -> bool {
        true // Sempre válido para teste
    }
}

fn main() {
    // Configuração de Dependências (Composition Root)
    let network_adapter = MockNetwork;
    let crypto_adapter = MockCrypto;
    let my_node_id = 1;

    // Injeção de Dependências no Serviço
    let mut consensus_service = crate::service::consensus::ByzantineConsensusService::new(
        my_node_id,
        network_adapter,
        crypto_adapter
    );

    // Simulação de recebimento de uma mensagem maliciosa ou legítima
    let incoming_msg = crate::domain::message::ConsensusMessage::new(
        0,
        100,
        crate::domain::message::MessageType::PrePrepare,
        "hash_da_transacao_blockcain".to_string(),
        2,
        vec![0, 0, 0]
    );

    match consensus_service.handle_message(incoming_msg) {
        Ok(_) => println!("Mensagem processada com sucesso."),
        Err(e) => eprintln!("Erro ao processar mensagem: {}", e),
    }
}