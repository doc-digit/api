import uuid
from gino.ext.sanic import Gino

from sqlalchemy.dialects import postgresql

db = Gino()


# uuid field fix 
class UUID(postgresql.UUID):
    def result_processor(self, dialect, coltype):
        if self.as_uuid:

            def process(value):
                if not isinstance(value, uuid.UUID):
                    value = uuid.UUID(value)
                return value

            return process
        else:
            return None
            

"""
Models
"""

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)

    def __repr__(self):
        return 'Document {}'.format(self.id)

        
class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    document_id = db.Column(db.ForeignKey('documents.id'))

    def __repr__(self):
        return 'Page {} Document {}'.format(self.id, self.document_id)