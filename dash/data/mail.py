from dash.data import db


class PenguinPostcard(db.Model):
    __tablename__ = 'penguin_postcard'

    id = db.Column(db.Integer, primary_key=True,
                   server_default=db.text("nextval('\"penguin_postcard_id_seq\"'::regclass)"))
    penguin_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False,
                           index=True)
    sender_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    postcard_id = db.Column(db.ForeignKey('postcard.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    send_date = db.Column(db.DateTime, nullable=False, server_default=db.text("now()"))
    details = db.Column(db.String(255), nullable=False, server_default=db.text("''::character varying"))
    has_read = db.Column(db.Boolean, nullable=False, server_default=db.text("false"))
