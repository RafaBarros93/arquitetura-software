import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from flask import Flask, jsonify, request
from flask_restx import Api, Resource
from modelo_dominio.produto import Produto
from modelo_dominio.pedido import Pedido
from modelo_dominio.repositorio import RepositorioProduto, RepositorioPedido

"""
Servidor REST/HTTP2 usando Flask
Aspectos Arquiteturais:
- RESTful, separação de responsabilidades
- Uso didático de HTTP/2 (via Hypercorn)
- CRUD para Produtos e Pedidos
"""

app = Flask(__name__)
repo_produtos = RepositorioProduto()
repo_pedidos = RepositorioPedido()

# Configurar o Flask-RESTx
api = Api(app, title="API REST/HTTP2", version="1.0", description="Documentação da API REST/HTTP2", doc="/swagger")

# Criar um namespace para os endpoints
ns_produtos = api.namespace('produtos', description='Operações relacionadas a produtos')

# Atualizar os endpoints para usar o namespace do Flask-RESTx
@ns_produtos.route('/')
class ProdutoLista(Resource):
    def get(self):
        """Lista todos os produtos"""
        return jsonify([p.to_dict() for p in repo_produtos.listar_todos()])

    def post(self):
        """Adiciona um novo produto"""
        dados = request.json
        prod = Produto(nome=dados.get('nome'), preco=dados.get('preco'))
        repo_produtos.adicionar(prod)
        return jsonify(prod.to_dict()), 201

@ns_produtos.route('/<string:codigo>')
class ProdutoItem(Resource):
    def get(self, codigo):
        """Obtém um produto pelo código"""
        prod = repo_produtos.obter_por_id(codigo)
        if prod:
            return jsonify(prod.to_dict())
        return jsonify({"erro": "Produto não encontrado"}), 404

# Registrar o namespace na API
api.add_namespace(ns_produtos, path='/api/produtos')

# Dados iniciais
def seed():
    p1 = Produto(nome="Notebook", preco=3500.0)
    p2 = Produto(nome="Smartphone", preco=2000.0)
    repo_produtos.adicionar(p1)
    repo_produtos.adicionar(p2)
    ped = Pedido()
    ped.adicionar_produto(p1)
    repo_pedidos.adicionar(ped)

seed()
