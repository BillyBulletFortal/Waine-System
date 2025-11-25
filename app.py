from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
# Configuração CORS simplificada e eficaz
CORS(app)

# Configurações
DATABASE = 'wayne_industries.db'

def get_db_connection():
    """Cria conexão com o banco de dados"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados com tabelas e dados iniciais"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar tabela de projetos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT NOT NULL,
            tipo TEXT NOT NULL,
            nivel_acesso TEXT NOT NULL,
            status TEXT DEFAULT 'ativo',
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Verificar se já existem dados
    cursor.execute("SELECT COUNT(*) as count FROM projetos")
    count = cursor.fetchone()['count']
    
    # Inserir dados apenas se a tabela estiver vazia
    if count == 0:
        projetos_iniciais = [
            # Projetos Comerciais
            ('Sistema de Vigilância Urbana GCPD', 'Rede de monitoramento em tempo real para o departamento de polícia de Gotham', 'comercial', 'publico'),
            ('Bat-Computador Empresarial Series X', 'Workstations de alta performance para análise de dados corporativos', 'comercial', 'publico'),
            ('Sistema de Comunicação Criptografada', 'Rede segura para comunicações corporativas e governamentais', 'comercial', 'gerente'),
            ('Equipamento de Emergência Médica', 'Kits de primeiros socorros avançados para hospitais e instituições', 'comercial', 'publico'),
            
            # Projetos Secretos
            ('Tecnologia de Defesa Pessoal - Projeto Nighthawk', 'Sistemas defensivos avançados com materiais compostos experimentais', 'secreto', 'administrador'),
            ('Veículo de Resposta Rápida - Protótipo 01', 'Plataforma móvel multi-terreno com sistemas de ocultação', 'secreto', 'administrador'),
            ('Análise de Inteligência Criminal - Sistema Oracle', 'Algoritmo preditivo para análise de padrões criminais em Gotham', 'secreto', 'administrador'),
            ('Sistema de Energia Portátil - Célula Wayne', 'Fonte de energia de alta densidade para aplicações táticas', 'secreto', 'administrador'),
            
            # Projetos Públicos
            ('Projeto Orfanato Thomas & Martha Wayne', 'Iniciativa social para educação e desenvolvimento de jovens', 'publico', 'publico'),
            ('Fundação Wayne para Ciência e Tecnologia', 'Bolsa de estudos para jovens talentos em STEM', 'publico', 'publico'),
            ('Programa de Renovação Urbana do Distrito de Caçamba', 'Reurbanização de áreas carentes de Gotham City', 'publico', 'publico'),
            ('Centro Médico Martha Wayne', 'Hospital comunitário oferecendo serviços gratuitos', 'publico', 'publico')
        ]
        
        cursor.executemany('''
            INSERT INTO projetos (nome, descricao, tipo, nivel_acesso)
            VALUES (?, ?, ?, ?)
        ''', projetos_iniciais)
        
        print(f"✅ {len(projetos_iniciais)} projetos inseridos no banco de dados!")
    
    conn.commit()
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")

# ========== ROTAS DA API ==========

@app.route('/')
def home():
    """Página inicial - serve o frontend"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve arquivos estáticos (CSS, JS)"""
    return send_from_directory('frontend', path)

@app.route('/api/status')
def status():
    """Endpoint para verificar status do sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Contar projetos por tipo
        cursor.execute("SELECT tipo, COUNT(*) as count FROM projetos GROUP BY tipo")
        stats = cursor.fetchall()
        
        # Total de projetos
        cursor.execute("SELECT COUNT(*) as total FROM projetos")
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            "status": "online",
            "database": DATABASE,
            "projetos_total": total,
            "estatisticas": {row['tipo']: row['count'] for row in stats},
            "mensagem": "Sistema Wayne Industries operacional"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/api/projetos', methods=['GET'])
def get_projetos():
    """Endpoint para listar projetos"""
    try:
        tipo = request.args.get('tipo', 'all')
        conn = get_db_connection()
        
        if tipo == 'all':
            cursor = conn.execute('SELECT * FROM projetos WHERE status = "ativo" ORDER BY nome')
        else:
            cursor = conn.execute('SELECT * FROM projetos WHERE tipo = ? AND status = "ativo" ORDER BY nome', (tipo,))
        
        projetos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True,
            "count": len(projetos),
            "projetos": projetos
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projetos/buscar', methods=['GET'])
def buscar_projetos():
    """Endpoint para buscar projetos por termo"""
    try:
        termo = request.args.get('termo', '')
        conn = get_db_connection()
        
        cursor = conn.execute('''
            SELECT * FROM projetos 
            WHERE (nome LIKE ? OR descricao LIKE ?) 
            AND status = "ativo"
            ORDER BY nome
        ''', (f'%{termo}%', f'%{termo}%'))
        
        projetos = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            "success": True,
            "count": len(projetos),
            "projetos": projetos
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/projetos/<int:projeto_id>', methods=['GET'])
def get_projeto(projeto_id):
    """Endpoint para buscar um projeto específico"""
    try:
        conn = get_db_connection()
        
        cursor = conn.execute('SELECT * FROM projetos WHERE id = ?', (projeto_id,))
        projeto = cursor.fetchone()
        
        conn.close()
        
        if projeto:
            return jsonify({
                "success": True,
                "projeto": dict(projeto)
            })
        else:
            return jsonify({
                "success": False,
                "error": "Projeto não encontrado"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ========== INICIALIZAÇÃO ==========

if __name__ == '__main__':
    print("🚀 Iniciando Wayne Industries API...")
    print("📦 Inicializando banco de dados...")
    init_db()
    print("🌐 Servidor Flask iniciando...")
    print("📊 Acesse: http://localhost:5000")
    print("🔧 Frontend sendo servido automaticamente")
    app.run(debug=True, port=5000, host='0.0.0.0')