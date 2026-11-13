import os

from saga import SagaPedido
from servicos import ServicoEstoque, ServicoPagamento, ServicoPedido

for arquivo in ("pedidos.db", "estoque.db", "pagamentos.db"):
    if os.path.exists(arquivo):
        os.remove(arquivo)

pedidos = ServicoPedido()
estoque = ServicoEstoque({"Teclado": 10, "Monitor": 3, "Mouse": 5})
pagamento = ServicoPagamento(limite=1000)
saga = SagaPedido(pedidos, estoque, pagamento)

compras = [
    (1, "Teclado", 2, 300.0),
    (2, "Monitor", 1, 1500.0),
    (3, "Mouse", 10, 250.0),
]

for pedido_id, produto, quantidade, valor in compras:
    print(f"\nPedido {pedido_id}: {quantidade}x {produto} por R$ {valor:.2f}")
    resultado = saga.executar(pedido_id, produto, quantidade, valor)
    print("  => APROVADO" if resultado else "  => CANCELADO")

print("\n--- pedidos.db ---")
for linha in pedidos.conn.execute("SELECT * FROM pedido"):
    print(" ", linha)

print("\n--- estoque.db ---")
for linha in estoque.conn.execute("SELECT * FROM produto"):
    print(" ", linha)

print("\n--- pagamentos.db ---")
for linha in pagamento.conn.execute("SELECT * FROM pagamento"):
    print(" ", linha)
