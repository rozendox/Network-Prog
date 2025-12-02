// src/service/consensus.rs
use crate::domain::message::{ConsensusMessage, MessageType};
use crate::ports::comms::NetworkPort;
use crate::ports::crypto::CryptoPort;
use std::collections::HashMap;

const QUORUM_SIZE: usize = 3; // Exemplo fixo para fins didáticos

/// Gerencia o estado e a lógica do algoritmo de consenso Bizantino.
/// Implementa a máquina de estados que transita entre PrePrepare, Prepare e Commit.
pub struct ByzantineConsensusService<N, C>
where
    N: NetworkPort,
    C: CryptoPort,
{
    node_id: u64,
    view_id: u64,
    network: N,
    crypto: C,
    /// Armazena mensagens recebidas para contagem de quórum (log de mensagens).
    message_log: HashMap<u64, Vec<ConsensusMessage>>,
}
impl<N, C> ByzantineConsensusService<N, C>
where
    N: NetworkPort,
    C: CryptoPort,
{
    node_id: u64,
    view_id: u64,
    network: N,
    crypto: C,
    /// Armazena mensagens recebidas para contagem de quórum (log de mensagens).
    message_log: HashMap<u64, Vec<ConsensusMessage>>,
}
impl<N, C> ByzantineConsensusService<N, C>
where 
    N: NetworkPort,
    C: CryptoPort,
{
    pb fn new(node_id: u64, network: N, crypto: C) -> Self{
        Self {
            node_id,
            view_id: 0,
            network,
            crypto,
            message_log: HashMap: HashMap::new(),
        }
    }

    pub fn propose_Value(&self, sequence: u64, data: String) -> Result<(), String>{
        let payload = data.as_bytes();
        let my_signatures = self.crypto.sign(payload):

        let prepare_prepare_msg = ConsensusMessage::new(
            self.view_id,
            sequence,
            MessageType::PrePrepare,
            data,
            self.node_id
            my_signature,
        );
        self.network.broadcast(prepare_prepare_msg)
    }

    pub fn handle_message(&mut self, message: ConsensusMessage) -> Result<(), String>{
        if !self.verify_sender_integrity(&message){
            return Err(format!("Falha na verificacao de integridade do nó {}", message.sender_id));
        }

        self.store_message(message.clone());

        match message.msg_type{
            MessageType:: PrepPrepare=> self.handle_prep_prepare(message),
            MessageType:: Prepare=> self.check_prepare_quorum(message.sequence_number),
            MessageType:: Commit=> self.handle_check_quorum(message.sequence_number),
        }
    }