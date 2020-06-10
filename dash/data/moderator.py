from dash.data import db


class Ban(db.Model):
    __tablename__ = 'ban'

    penguin_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                           nullable=False)
    issued = db.Column(db.DateTime, primary_key=True, nullable=False, server_default=db.text("now()"))
    expires = db.Column(db.DateTime, primary_key=True, nullable=False, server_default=db.text("now()"))
    moderator_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    reason = db.Column(db.SmallInteger, nullable=False)
    comment = db.Column(db.Text)
    message = db.Column(db.Text)
