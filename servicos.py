import sqlite3


class ServicoPedido:
    def __init__(self, arquivo="pedidos.db"):
        self.conn = sqlite3.connect(arquivo)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS pedido (id INTEGER PRIMARY KEY, produto TEXT, quantidade INTEGER, valor REAL, status TEXT)"
        )

    def criar(self, pedido_id, produto, quantidade, valor):
        with self.conn:
            self.conn.execute(
                "INSERT INTO pedido VALUES (?, ?, ?, ?, 'PENDENTE')",
                (pedido_id, produto, quantidade, valor),
            )

    def aprovar(self, pedido_id):
        with self.conn:
            self.conn.execute("UPDATE pedido SET status = 'APROVADO' WHERE id = ?", (pedido_id,))

    def cancelar(self, pedido_id):
        with self.conn:
            self.conn.execute("UPDATE pedido SET status = 'CANCELADO' WHERE id = ?", (pedido_id,))


class ServicoEstoque:
    def __init__(self, produtos, arquivo="estoque.db"):
        self.conn = sqlite3.connect(arquivo)
        with self.conn:
            self.conn.execute("CREATE TABLE IF NOT EXISTS produto (nome TEXT PRIMARY KEY, quantidade INTEGER)")
            self.conn.execute("CREATE TABLE IF NOT EXISTS reserva (pedido_id INTEGER, produto TEXT, quantidade INTEGER)")
            self.conn.executemany("INSERT OR REPLACE INTO produto VALUES (?, ?)", produtos.items())

    def reservar(self, pedido_id, produto, quantidade):
        disponivel = self.conn.execute("SELECT quantidade FROM produto WHERE nome = ?", (produto,)).fetchone()[0]
        if disponivel < quantidade:
            raise RuntimeError(f"estoque insuficiente de {produto} ({disponivel} disponíveis)")
        with self.conn:
            self.conn.execute("UPDATE produto SET quantidade = quantidade - ? WHERE nome = ?", (quantidade, produto))
            self.conn.execute("INSERT INTO reserva VALUES (?, ?, ?)", (pedido_id, produto, quantidade))

    def liberar(self, pedido_id):
        produto, quantidade = self.conn.execute(
            "SELECT produto, quantidade FROM reserva WHERE pedido_id = ?", (pedido_id,)
        ).fetchone()
        with self.conn:
            self.conn.execute("UPDATE produto SET quantidade = quantidade + ? WHERE nome = ?", (quantidade, produto))
            self.conn.execute("DELETE FROM reserva WHERE pedido_id = ?", (pedido_id,))


class ServicoPagamento:
    def __init__(self, limite, arquivo="pagamentos.db"):
        self.limite = limite
        self.conn = sqlite3.connect(arquivo)
        self.conn.execute("CREATE TABLE IF NOT EXISTS pagamento (pedido_id INTEGER, valor REAL, status TEXT)")

    def cobrar(self, pedido_id, valor):
        if valor > self.limite:
            raise RuntimeError(f"pagamento recusado, R$ {valor:.2f} acima do limite de R$ {self.limite:.2f}")
        with self.conn:
            self.conn.execute("INSERT INTO pagamento VALUES (?, ?, 'PAGO')", (pedido_id, valor))

    def estornar(self, pedido_id):
        with self.conn:
            self.conn.execute("UPDATE pagamento SET status = 'ESTORNADO' WHERE pedido_id = ?", (pedido_id,))
