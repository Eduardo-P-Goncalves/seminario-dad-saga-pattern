class SagaPedido:
    def __init__(self, pedidos, estoque, pagamento):
        self.pedidos = pedidos
        self.estoque = estoque
        self.pagamento = pagamento

    def executar(self, pedido_id, produto, quantidade, valor):
        passos = [
            ("Criar pedido",
             lambda: self.pedidos.criar(pedido_id, produto, quantidade, valor),
             lambda: self.pedidos.cancelar(pedido_id)),
            ("Reservar estoque",
             lambda: self.estoque.reservar(pedido_id, produto, quantidade),
             lambda: self.estoque.liberar(pedido_id)),
            ("Cobrar pagamento",
             lambda: self.pagamento.cobrar(pedido_id, valor),
             lambda: self.pagamento.estornar(pedido_id)),
            ("Aprovar pedido",
             lambda: self.pedidos.aprovar(pedido_id),
             None),
        ]
        concluidos = []

        for nome, acao, compensacao in passos:
            try:
                acao()
                print(f"  [OK]    {nome}")
                concluidos.append((nome, compensacao))
            except RuntimeError as erro:
                print(f"  [FALHA] {nome}: {erro}")
                # Desfaz os passos já concluídos, do último para o primeiro.
                for nome_concluido, desfazer in reversed(concluidos):
                    desfazer()
                    print(f"  [DESFEITO] {nome_concluido}")
                return False

        return True
