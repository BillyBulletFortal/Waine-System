// Configuração da API
// PARA DESENVOLVIMENTO LOCAL: "http://localhost:5000/api"
// PARA PRODUÇÃO: "https://sua-api.railway.app/api"
const API_URL = "http://localhost:5000/api"; // Altere para sua URL do Railway depois

// Funções para comunicação com a API
async function carregarDados() {
    try {
        const response = await fetch(`${API_URL}/projetos`);
        const data = await response.json();
        
        if (data.success) {
            return data.projetos;
        } else {
            console.error("Erro ao carregar dados:", data.error);
            return [];
        }
    } catch (error) {
        console.error("Erro ao carregar dados:", error);
        return [];
    }
}

async function salvarDados(dados) {
    try {
        const response = await fetch(`${API_URL}/projetos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dados)
        });
        return await response.json();
    } catch (error) {
        console.error("Erro ao salvar:", error);
        return { success: false, error: error.message };
    }
}

async function buscarProjetos(termo) {
    try {
        const response = await fetch(`${API_URL}/projetos/buscar?termo=${encodeURIComponent(termo)}`);
        const data = await response.json();
        
        if (data.success) {
            return data.projetos;
        } else {
            console.error("Erro na busca:", data.error);
            return [];
        }
    } catch (error) {
        console.error("Erro na busca:", error);
        return [];
    }
}

async function verificarStatus() {
    try {
        const response = await fetch(`${API_URL}/status`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Erro ao verificar status:", error);
        return { status: "offline", error: error.message };
    }
}

// ========== FUNÇÕES EXISTENTES DO SEU PROJETO ==========
// (Mantenha suas funções existentes, mas atualize para usar as funções da API acima)

// Exemplo de como integrar com suas funções existentes:
async function inicializarSistema() {
    const status = await verificarStatus();
    
    if (status.status === "online") {
        console.log("✅ Conectado à API Wayne Industries");
        // Carrega os dados iniciais
        const projetos = await carregarDados();
        // Chama sua função existente para exibir os projetos
        exibirProjetos(projetos);
    } else {
        console.error("❌ Erro de conexão com a API");
        // Mostra mensagem de erro para o usuário
        mostrarErroConexao();
    }
}

// Suas funções existentes (exemplo):
function exibirProjetos(projetos) {
    // Sua lógica existente para exibir projetos na interface
    console.log("Projetos carregados:", projetos);
}

function mostrarErroConexao() {
    // Sua lógica para mostrar erro de conexão
    alert("Erro de conexão com o servidor. Verifique se a API está rodando.");
}

// Inicializa o sistema quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    inicializarSistema();
});
