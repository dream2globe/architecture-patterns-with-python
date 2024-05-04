from sqlalchemy import text

from src.model import Batch, OrderLine
from src.repository import SqlAlchemyRepository


def test_repository_can_save_a_batch(session):
    batch = Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)
    repo = SqlAlchemyRepository(session)
    repo.add(batch)  # a test case
    session.commit()
    rows = session.execute(
        text("SELECT reference, sku, _purchased_quantity, eta FROM batches")
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    sql = text(
        f"""
        INSERT INTO order_lines (orderid, sku, qty)
        VALUES ('order1', 'GENERIC-SOFA', 12)
        """
    )
    session.execute(sql)
    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid='order1' AND sku='GENERIC-SOFA'")
    )
    return orderline_id


def insert_batch(session, batch_id):
    sql = text(
        f"""
        INSERT INTO batches (reference, sku, _purchased_quantity, eta) 
        VALUES ('{batch_id}', 'GENERIC-SOFA', 100, null)"""
    )
    session.execute(sql)
    [[batch_id]] = session.execute(
        text(
            f"SELECT id FROM batches WHERE reference='{batch_id}' AND sku='GENERIC-SOFA'"
        )
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    sql = text(
        f"""
        INSERT INTO allocations (orderline_id, batch_id)
        VALUES ('{orderline_id}', '{batch_id}')
        """
    )
    session.execute(sql)


def test_repository_can_retrieve_a_batch_with_allocation(session):
    # Prepare data
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")

    # Run a test case
    insert_allocation(session, orderline_id, batch1_id)
    repo = SqlAlchemyRepository(session)

    # Check a result
    retrieved = repo.get("batch1")
    expected = Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {
        OrderLine("order1", "GENERIC-SOFA", 12),
    }
