# Implementação de Variante Byzantine Paxos em Rust

## Visão Geral

Este projeto apresenta uma implementação modular de um algoritmo de consenso baseado em Paxos, estendido para suportar Tolerância a Falhas Bizantinas (BFT - Byzantine Fault Tolerance). O sistema foi desenvolvido em Rust, focando em segurança de memória e desempenho, e serve como prova de conceito para a camada de consenso de uma Blockchain Permissionada.

O objetivo desta implementação é demonstrar arquiteturalmente como isolar a complexidade lógica de um algoritmo de consenso distribuído das camadas de infraestrutura (rede e criptografia), utilizando princípios de Clean Architecture e SOLID adaptados para o paradigma de Rust.

## Contexto Teórico e Motivação

### O Problema dos Generais Bizantinos
Diferente de sistemas distribuídos clássicos que assumem apenas falhas de parada (crash faults), redes descentralizadas e blockchains devem operar sob a premissa de que nós podem agir de maneira maliciosa ou arbitrária (mentir, omitir mensagens ou enviar informações conflitantes).

### Solução BFT
Para garantir a integridade do registro distribuído (ledger), o algoritmo implementado requer que mais de 2/3 dos nós da rede sejam honestos. A consistência é alcançada através de um protocolo de votação em três fases, assegurando que todas as réplicas honestas concordem com a mesma sequência de transações, mesmo na presença de adversários ativos.

## Decisões Arquiteturais

O projeto não segue uma estrutura monolítica. A arquitetura foi dividida em camadas para garantir testabilidade e desacoplamento:

1.  **Domínio (Core):** Contém as entidades puras e regras de negócio invariáveis. Não possui dependências de bibliotecas externas.
2.  **Portas (Ports):** Define as interfaces (Traits) necessárias para o funcionamento do sistema. Segue o Princípio da Inversão de Dependência (DIP), onde o módulo de alto nível define o contrato que os módulos de baixo nível devem implementar.
3.  **Serviço (Application):** Orquestra o fluxo de mensagens e gerencia a máquina de estados do consenso (Pre-Prepare, Prepare, Commit).
4.  **Infraestrutura (Adapters):** Implementações concretas das portas. No estado atual, utiliza Mocks para simulação local, mas permite a substituição por implementações reais (TCP/UDP, Curvas Elípticas) sem alteração no núcleo.

## Estrutura do Projeto

```text
src/
├── domain/
│   ├── mod.rs
│   ├── message.rs       # Definição de estruturas de dados e tipos de mensagens (ConsensusMessage)
│   └── node.rs          # Representação de identidade dos nós
├── ports/
│   ├── mod.rs
│   ├── comms.rs         # Interface (Trait) para abstração de comunicação de rede
│   └── crypto.rs        # Interface (Trait) para abstração de operações criptográficas
├── service/
│   ├── mod.rs
│   └── consensus.rs     # Implementação da lógica de consenso Bizantino e gestão de Quórum
└── main.rs              # Ponto de entrada, injeção de dependências e configuração de Mocks
Detalhes de Implementação
Máquina de Estados e Fases
O algoritmo processa mensagens seguindo o fluxo padrão de variantes PBFT (Practical Byzantine Fault Tolerance):

Pre-Prepare: O líder propõe um valor e o assina.

Prepare: Os nós validam a proposta e trocam confirmações entre si. É necessário um quórum de 2f + 1 para avançar.

Commit: Fase final de validação para garantir que a proposta foi "travada" na rede antes da execução.

Segurança
A integridade é assegurada através da CryptoPort. Cada mensagem carrega uma assinatura digital. O serviço de consenso verifica a assinatura de cada mensagem recebida antes de processá-la, garantindo a autenticidade da origem e a integridade do conteúdo (digest).

Como Executar
Este projeto requer a instalação da linguagem Rust e do gerenciador de pacotes Cargo.

Clone o repositório.

Navegue até o diretório do projeto.

Execute o comando de simulação:

Bash

cargo run
A execução demonstrará o ciclo de vida de uma mensagem sendo processada pelo serviço de consenso, utilizando os adaptadores simulados (Mocks) definidos no main.rs.

Limitações e Roteiro de Evolução
Esta é uma implementação de referência arquitetural. Para utilização em um ambiente de produção real, as seguintes evoluções são necessárias:

Persistência: Implementação de um Write-Ahead Log (WAL) para recuperação de estado após falhas.

Protocolo de View Change: Mecanismo para eleger um novo líder caso o atual falhe ou aja maliciosamente (Liveness).

Camada de Rede Real: Substituição dos Mocks por comunicação via gRPC ou Libp2p.

Criptografia Assimétrica: Integração com bibliotecas como ed25519-dalek ou secp256k1 para assinaturas reais.