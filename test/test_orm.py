from sqlalchemy import text

from src.model import OrderLine


def test_orderline_mapper_can_load_lines(session):
    sql = text(
        """
        INSERT INTO order_lines (orderid, sku, qty) VALUES
        ('order1', 'RED-CHAIR', 12),
        ('order1', 'RED-TABLE', 13),
        ('order2', 'BLUE-LIPSTICK', 14)            
        """
    )
    session.execute(sql)
    expected = [
        OrderLine("order1", "RED-CHAIR", 12),
        OrderLine("order1", "RED-TABLE", 13),
        OrderLine("order2", "BLUE-LIPSTICK", 14),
    ]
    assert session.query(OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = OrderLine("order1", "DECORATIVE-WIDGET", 12)
    session.add(new_line)
    session.commit()
    sql = text("SELECT orderid, sku, qty FROM order_lines")
    rows = list(session.execute(sql))
    assert rows == [("order1", "DECORATIVE-WIDGET", 12)]
