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

# Criar um namespace para os endpoints de pedidos
ns_pedidos = api.namespace('pedidos', description='Operações relacionadas a pedidos')

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

@ns_pedidos.route('/')
class PedidoLista(Resource):
    def get(self):
        """Lista todos os pedidos"""
        return jsonify([p.to_dict() for p in repo_pedidos.listar_todos()])

    def post(self):
        """Cria um novo pedido"""
        dados = request.json
        ped = Pedido()
        for cod in dados.get('produtos', []):
            prod = repo_produtos.obter_por_id(cod)
            if prod:
                ped.adicionar_produto(prod)
        repo_pedidos.adicionar(ped)
        return jsonify(ped.to_dict()), 201

@ns_pedidos.route('/<string:codigo>')
class PedidoItem(Resource):
    def get(self, codigo):
        """Obtém um pedido pelo código"""
        ped = repo_pedidos.obter_por_id(codigo)
        if ped:
            return jsonify(ped.to_dict())
        return jsonify({"erro": "Pedido não encontrado"}), 404

@ns_pedidos.route('/<string:codigo>/produtos')
class PedidoProdutos(Resource):
    def post(self, codigo):
        """Adiciona um produto a um pedido"""
        ped = repo_pedidos.obter_por_id(codigo)
        if not ped:
            return jsonify({"erro": "Pedido não encontrado"}), 404
        dados = request.json
        prod = repo_produtos.obter_por_id(dados.get('codigo_produto'))
        if not prod:
            return jsonify({"erro": "Produto não encontrado"}), 404
        ped.adicionar_produto(prod)
        repo_pedidos.atualizar(codigo, ped)
        return jsonify(ped.to_dict())

@ns_pedidos.route('/<string:codigo>/produtos/<string:codigo_produto>')
class PedidoProdutoItem(Resource):
    def delete(self, codigo, codigo_produto):
        """Remove um produto de um pedido"""
        ped = repo_pedidos.obter_por_id(codigo)
        if not ped:
            return jsonify({"erro": "Pedido não encontrado"}), 404
        ped.remover_produto(codigo_produto)
        repo_pedidos.atualizar(codigo, ped)
        return '', 204

# Registrar o namespace na API
api.add_namespace(ns_produtos, path='/api/produtos')
api.add_namespace(ns_pedidos, path='/api/pedidos')

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
