from dash.data import db


class PenguinItem(db.Model):
    __tablename__ = 'penguin_item'

    penguin_id = db.Column(db.ForeignKey('penguin.id', ondelete='CASCADE', onupdate='CASCADE'),
                           primary_key=True, nullable=False)
    item_id = db.Column(db.ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'),
                        primary_key=True, nullable=False)