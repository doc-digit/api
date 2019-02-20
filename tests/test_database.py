import uuid

from api.database import db,Document,Page
async def test_create_document(engine):
    db.bind = engine

    id = uuid.uuid4()
    doc = await Document.create(id=id)
    assert doc.id == id

async def test_documents(engine):
    
    query = db.select([Document])
    docs = await query.gino.all()
    
    assert len(docs) == 1