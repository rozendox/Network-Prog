package main

import (
	"flag"
	"fmt"
	"log"
	"math/rand"
	"net"
	"net/rpc"
	"os"
	"sync"
	"time"
)

// --- Constantes e Tipos ---

type State int

const (
	Follower State = iota
	Candidate
	Leader
)

// Configurações de tempo (em milissegundos)
const (
	HeartbeatInterval = 100 * time.Millisecond
	MinElectionTimeout = 300
	MaxElectionTimeout = 600
)

// LogEntry representa um comando a ser aplicado na máquina de estados
type LogEntry struct {
	Term    int
	Command interface{}
}

// RaftServer é a estrutura principal do nosso nó
type RaftServer struct {
	mu sync.Mutex // Lock para proteger o estado compartilhado

	id    int
	peers map[int]string // Mapa de ID -> Endereço (ex: "localhost:8001")

	// Estado Persistente (em um Raft real, isso iria para o disco)
	currentTerm int
	votedFor    int
	log         []LogEntry

	// Estado Volátil
	state        State
	electionTimer *time.Timer
	lastHeartbeat time.Time
}

// --- Estruturas de RPC (Mensagens trocadas entre nós) ---

type RequestVoteArgs struct {
	Term         int
	CandidateId  int
	LastLogIndex int
	LastLogTerm  int
}

type RequestVoteReply struct {
	Term        int
	VoteGranted bool
}

type AppendEntriesArgs struct {
	Term     int
	LeaderId int
	Entries  []LogEntry
	// Simplificação: Omitindo prevLogIndex/Term para focar na eleição neste exemplo
}

type AppendEntriesReply struct {
	Term    int
	Success bool
}

// --- Lógica do Servidor ---

func NewRaftServer(id int, peers map[int]string) *RaftServer {
	rf := &RaftServer{
		id:          id,
		peers:       peers,
		state:       Follower,
		votedFor:    -1,
		currentTerm: 0,
		log:         make([]LogEntry, 0),
	}
	return rf
}

// Start inicia o loop principal do servidor
func (rf *RaftServer) Start() {
	// Inicializa RPC
	rpc.Register(rf)
	listener, err := net.Listen("tcp", rf.peers[rf.id])
	if err != nil {
		log.Fatal("Erro ao ouvir porta:", err)
	}
	
	// Thread para servir RPCs
	go func() {
		for {
			conn, err := listener.Accept()
			if err != nil {
				continue
			}
			go rpc.ServeConn(conn)
		}
	}()

	// Loop principal de controle (Ticker)
	go rf.runElectionLoop()

	log.Printf("Servidor %d iniciado em %s como FOLLOWER", rf.id, rf.peers[rf.id])
	
	// Mantém o processo vivo
	select {}
}

// runElectionLoop gerencia os timeouts e transições de estado
func (rf *RaftServer) runElectionLoop() {
	rf.resetElectionTimer()

	for {
		<-rf.electionTimer.C
		
		rf.mu.Lock()
		state := rf.state
		rf.mu.Unlock()

		switch state {
		case Follower, Candidate:
			rf.startElection()
		case Leader:
			rf.sendHeartbeats()
			rf.resetElectionTimer() // Líder reinicia timer apenas para manter o loop
		}
	}
}

// startElection: Transição para Candidato e solicitação de votos
func (rf *RaftServer) startElection() {
	rf.mu.Lock()
	rf.state = Candidate
	rf.currentTerm++
	rf.votedFor = rf.id // Vota em si mesmo
	term := rf.currentTerm
	rf.mu.Unlock()

	log.Printf("[%d] Iniciando eleição para Termo %d", rf.id, term)
	
	// Reinicia o timer para evitar split votes infinitos
	rf.resetElectionTimer()

	votesReceived := 1 // Conta o próprio voto
	totalPeers := len(rf.peers)

	// Envia RequestVote para todos os pares em paralelo
	for peerId, addr := range rf.peers {
		if peerId == rf.id {
			continue
		}

		go func(pid int, address string) {
			args := RequestVoteArgs{
				Term:        term,
				CandidateId: rf.id,
			}
			var reply RequestVoteReply

			if rf.sendRPC(address, "RaftServer.RequestVote", &args, &reply) {
				rf.mu.Lock()
				defer rf.mu.Unlock()

				// Se descobrimos um termo maior, voltamos a ser Follower
				if reply.Term > rf.currentTerm {
					rf.becomeFollower(reply.Term)
					return
				}

				if rf.state != Candidate || rf.currentTerm != term {
					return
				}

				if reply.VoteGranted {
					votesReceived++
					if votesReceived > totalPeers/2 {
						rf.becomeLeader()
					}
				}
			}
		}(peerId, addr)
	}
}

// sendHeartbeats: Líder envia mensagens vazias para manter autoridade
func (rf *RaftServer) sendHeartbeats() {
	rf.mu.Lock()
	term := rf.currentTerm
	if rf.state != Leader {
		rf.mu.Unlock()
		return
	}
	rf.mu.Unlock()

	for peerId, addr := range rf.peers {
		if peerId == rf.id {
			continue
		}

		go func(address string) {
			args := AppendEntriesArgs{
				Term:     term,
				LeaderId: rf.id,
			}
			var reply AppendEntriesReply
			
			// Envia heartbeat
			if rf.sendRPC(address, "RaftServer.AppendEntries", &args, &reply) {
				rf.mu.Lock()
				defer rf.mu.Unlock()
				
				if reply.Term > rf.currentTerm {
					rf.becomeFollower(reply.Term)
				}
			}
		}(addr)
	}
}

// --- Métodos Auxiliares de Estado ---

func (rf *RaftServer) becomeLeader() {
	if rf.state == Leader {
		return
	}
	rf.state = Leader
	log.Printf("[%d] --- GANHOU ELEIÇÃO! Agora é LIDER do Termo %d ---", rf.id, rf.currentTerm)
	
	// Ao virar líder, envia heartbeat imediatamente
	go rf.sendHeartbeats()
}

func (rf *RaftServer) becomeFollower(term int) {
	rf.state = Follower
	rf.currentTerm = term
	rf.votedFor = -1
	log.Printf("[%d] Voltando a ser Follower (Termo atualizado: %d)", rf.id, term)
}

func (rf *RaftServer) resetElectionTimer() {
	if rf.electionTimer != nil {
		rf.electionTimer.Stop()
	}
	// Randomized timeout entre 150-300ms + base (para evitar colisões)
	ms := MinElectionTimeout + rand.Intn(MaxElectionTimeout-MinElectionTimeout)
	rf.electionTimer = time.NewTimer(time.Duration(ms) * time.Millisecond)
}

// Helper para chamadas RPC
func (rf *RaftServer) sendRPC(address string, method string, args interface{}, reply interface{}) bool {
	client, err := rpc.Dial("tcp", address)
	if err != nil {
		// Falha de rede é normal em sistfghjklç~/3 distribuídos
		return false
	}
	defer client.Close()

	err = client.Call(method, args, reply)
	return err == nil
}

// --- Handlers RPC (Invocados remotamente) ---

// RequestVote: Outro nó está pedindo meu voto
func (rf *RaftServer) RequestVote(args *RequestVoteArgs, reply *RequestVoteReply) error {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	// 1. Se o termo dele for menor, rejeita
	if args.Term < rf.currentTerm {
		reply.Term = rf.currentTerm
		reply.VoteGranted = false
		return nil
	}

	// 2. Se o termo dele for maior, atualizo meu termo e viro follower
	if args.Term > rf.currentTerm {
		rf.becomeFollower(args.Term)
	}

	reply.Term = rf.currentTerm

	// 3. Voto se ainda não votei neste termo (ou se já votei nele mesmo)
	if (rf.votedFor == -1 || rf.votedFor == args.CandidateId) {
		rf.votedFor = args.CandidateId
		reply.VoteGranted = true
		rf.resetElectionTimer() // Ganhei tempo, não preciso iniciar eleição
		log.Printf("[%d] Votou em %d para o Termo %d", rf.id, args.CandidateId, args.Term)
	} else {
		reply.VoteGranted = false
	}

	return nil
}

// AppendEntries: Heartbeat ou novos logs
func (rf *RaftServer) AppendEntries(args *AppendEntriesArgs, reply *AppendEntriesReply) error {
	rf.mu.Lock()
	defer rf.mu.Unlock()

	// 1. Termo obsoleto
	if args.Term < rf.currentTerm {
		reply.Term = rf.currentTerm
		reply.Success = false
		return nil
	}

	// 2. Reconheço o líder
	rf.currentTerm = args.Term
	rf.state = Follower
	rf.resetElectionTimer() // Reseta meu timer pois o líder está vivo

	reply.Term = rf.currentTerm
	reply.Success = true
	
	// Aqui seria a lógica de replicar logs...
	// log.Printf("[%d] Heartbeat recebido do Líder %d", rf.id, args.LeaderId)
	
	return nil
}

// --- Main: Configuração dos Nós ---

func main() {
	// Pega ID via flag. Ex: go run main.go -id 1
	idPtr := flag.Int("id", 1, "ID deste servidor (1, 2 ou 3)")
	flag.Parse()

	id := *idPtr
	
	// Definição estática do cluster (3 nós rodando localmente em portas diferentes)
	peers := map[int]string{
		1: "localhost:8001",
		2: "localhost:8002",
		3: "localhost:8003",
	}

	if _, ok := peers[id]; !ok {
		log.Fatal("ID inválido. Use 1, 2 ou 3")
	}

	rand.Seed(time.Now().UnixNano()) // Aleatoriedade para os timers

	server := NewRaftServer(id, peers)
	server.Start()
}